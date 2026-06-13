import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from models.watering_prediction import MoisturePoint, WateringPrediction
from models.plant import Plant
from repos.sensor_repo import SensorRepository
from repos.device_repo import DeviceRepository

MAX_PREDICTION_DAYS = 7
MIN_READINGS_AFTER_FILTER = 6
WATERING_MOISTURE_JUMP = 10.0
LOOKBACK_HOURS = 12
PROJECTION_STEP_MINUTES = 30

logger = logging.getLogger(__name__)


@dataclass
class RegressionResult:
    t0: datetime
    elapsed: list
    slope: float
    intercept: float
    r_squared: float


def _weighted_linear_regression(
    x: list[float], y: list[float], weights: list[float]
) -> tuple[float, float, float]:
    w_sum = sum(weights)
    wx_sum = sum(w * xi for w, xi in zip(weights, x))
    wy_sum = sum(w * yi for w, yi in zip(weights, y))
    wxx_sum = sum(w * xi * xi for w, xi in zip(weights, x))
    wxy_sum = sum(w * xi * yi for w, xi, yi in zip(weights, x, y))

    denom = w_sum * wxx_sum - wx_sum * wx_sum
    if denom == 0:
        return 0.0, wy_sum / w_sum, 0.0

    slope = (w_sum * wxy_sum - wx_sum * wy_sum) / denom
    intercept = (wy_sum - slope * wx_sum) / w_sum

    y_mean = wy_sum / w_sum
    ss_tot = sum(w * (yi - y_mean) ** 2 for w, yi in zip(weights, y))
    ss_res = sum(w * (yi - (slope * xi + intercept)) ** 2 for w, xi, yi in zip(weights, x, y))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return slope, intercept, r_squared


def _confidence_label(r_squared: float) -> str | None:
    if r_squared >= 0.7:
        return "high"
    if r_squared >= 0.5:
        return "medium"
    if r_squared >= 0.3:
        return "low"
    return None


def _build_projected_points(
    t0: datetime, elapsed: list[float], slope: float, intercept: float, minutes_until_dry: float
) -> list[MoisturePoint]:
    cap_minutes = MAX_PREDICTION_DAYS * 24 * 60
    projection_minutes = min(minutes_until_dry + PROJECTION_STEP_MINUTES, cap_minutes)
    last_elapsed = elapsed[-1]
    points = []
    for t in range(0, int(projection_minutes), PROJECTION_STEP_MINUTES):
        abs_t = last_elapsed + t
        val = slope * abs_t + intercept
        ts = (t0 + timedelta(minutes=abs_t)).isoformat()
        points.append(MoisturePoint(value=round(val, 1), timestamp=ts))
    return points


def _compute_prediction_time(
    t0: datetime, slope: float, intercept: float, moisture_min: float
) -> tuple[str | None, float | None]:
    minutes_until_dry = (moisture_min - intercept) / slope
    now = datetime.now()
    predicted_dt = t0 + timedelta(minutes=minutes_until_dry)
    cap_dt = now + timedelta(days=MAX_PREDICTION_DAYS)
    if now < predicted_dt <= cap_dt:
        return predicted_dt.isoformat(), round((predicted_dt - now).total_seconds() / 3600.0, 1)
    return None, None


def _last_watering_index(readings: list) -> int:
    idx = 0
    for i in range(1, len(readings)):
        if readings[i].moisture - readings[i - 1].moisture > WATERING_MOISTURE_JUMP:
            idx = i
    return idx


def _fit_filtered_readings(filtered: list) -> RegressionResult:
    t0 = datetime.fromisoformat(filtered[0].timestamp)
    elapsed = [(datetime.fromisoformat(r.timestamp) - t0).total_seconds() / 60.0 for r in filtered]
    moisture_vals = [float(r.moisture) for r in filtered]
    n = len(filtered)
    weights = [0.1 + 0.9 * i / (n - 1) for i in range(n)]
    slope, intercept, r_squared = _weighted_linear_regression(elapsed, moisture_vals, weights)
    return RegressionResult(t0=t0, elapsed=elapsed, slope=slope, intercept=intercept, r_squared=r_squared)


class PredictionService:
    def __init__(self):
        self.sensor_repo = SensorRepository()
        self.device_repo = DeviceRepository()

    def get_active_plant(self) -> Plant | None:
        return self.device_repo.get_active_plant()

    def predict_for_readings(self, plant: Plant, readings: list) -> WateringPrediction:
        if not readings:
            return self._empty_prediction(None, [])
        return self._predict_from_readings(plant, readings)

    def _empty_prediction(self, current_moisture: float | None, readings: list) -> WateringPrediction:
        return WateringPrediction(
            current_moisture=current_moisture,
            predicted_watering_time=None,
            hours_until_watering=None,
            confidence=None,
            historical=[MoisturePoint(value=r.moisture, timestamp=r.timestamp) for r in readings],
            predicted=[],
        )

    def _apply_regression(
        self, active_plant: Plant, reg: RegressionResult
    ) -> tuple[str | None, float | None, list[MoisturePoint]]:
        if reg.r_squared < 0.3 or reg.slope >= 0:
            return None, None, []
        target = float(active_plant.moisture_min)
        predicted_watering_time, hours_until_watering = _compute_prediction_time(
            reg.t0, reg.slope, reg.intercept, target
        )
        minutes_until_dry = (target - reg.intercept) / reg.slope
        predicted_points = _build_projected_points(
            reg.t0, reg.elapsed, reg.slope, reg.intercept, minutes_until_dry
        )
        return predicted_watering_time, hours_until_watering, predicted_points

    def _predict_from_readings(self, active_plant: Plant, readings: list) -> WateringPrediction:
        filtered = readings[_last_watering_index(readings):]
        current_moisture = float(readings[-1].moisture)

        if len(filtered) < MIN_READINGS_AFTER_FILTER:
            return self._empty_prediction(current_moisture, readings)

        reg = _fit_filtered_readings(filtered)
        predicted_watering_time, hours_until_watering, predicted_points = self._apply_regression(
            active_plant, reg
        )

        return WateringPrediction(
            current_moisture=current_moisture,
            predicted_watering_time=predicted_watering_time,
            hours_until_watering=hours_until_watering,
            confidence=_confidence_label(reg.r_squared),
            historical=[MoisturePoint(value=r.moisture, timestamp=r.timestamp) for r in readings],
            predicted=predicted_points,
        )

    def get_watering_prediction(self, plant: Plant | None = None) -> WateringPrediction:
        active_plant = plant or self.device_repo.get_active_plant()

        if not active_plant:
            return WateringPrediction(
                current_moisture=None,
                predicted_watering_time=None,
                hours_until_watering=None,
                confidence=None,
                historical=[],
                predicted=[],
            )

        readings = self.sensor_repo.get_recent_by_plant(active_plant.id, LOOKBACK_HOURS)
        if not readings:
            return self._empty_prediction(None, [])

        return self._predict_from_readings(active_plant, readings)
