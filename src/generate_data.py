from datetime import datetime, timedelta
from dataclasses import dataclass
import csv
import numpy as np


@dataclass
class MoistureState:
    moisture: float
    post_watering_steps: int


def _generate_cloud(total_steps: int) -> np.ndarray:
    cloud = np.zeros(total_steps)
    cloud[0] = 1.0
    for i in range(1, total_steps):
        cloud[i] = cloud[i - 1] + 0.01 * (1.0 - cloud[i - 1]) + np.random.normal(0, 0.04)
        cloud[i] = np.clip(cloud[i], 0.15, 1.3)
    return cloud


def _compute_lux(time_of_day: float, cloud_factor: float) -> float:
    is_day = 7.0 <= time_of_day <= 19.0
    if is_day:
        peak = np.sin(np.pi * (time_of_day - 7.0) / 12.0)
        lux = float(peak * 4000.0 * cloud_factor + np.random.uniform(-100, 100))
        return round(max(0.0, lux), 1)
    return round(float(np.random.uniform(0, 15)), 1)


def _compute_temperature(time_of_day: float) -> float:
    if 7.0 <= time_of_day <= 21.0:
        temp = 19.0 + 7.0 * np.sin(np.pi * (time_of_day - 7.0) / 14.0)
    else:
        temp = 19.5
    temp += np.random.uniform(-0.5, 0.5)
    return round(float(np.clip(temp, 18.0, 27.0)), 1)


def _step_moisture(state: MoistureState, is_watering: bool, is_day: bool, temperature: float, interval_min: int) -> MoistureState:
    if is_watering:
        return MoistureState(round(float(np.random.uniform(75, 90)), 1), int(90 / interval_min))

    evap = np.random.uniform(0.010, 0.030) if is_day else np.random.uniform(0.005, 0.015)
    if is_day:
        evap *= 1.0 + (temperature - 22.0) * 0.03

    steps = state.post_watering_steps
    if steps > 0:
        evap *= 0.25
        steps -= 1

    moisture = round(float(state.moisture - evap + np.random.normal(0, 0.04)), 1)
    return MoistureState(moisture, steps)


def _build_watering_set(start: datetime) -> set:
    first_watering = (start + timedelta(days=2)).replace(hour=9, minute=0, second=0, microsecond=0)
    return {first_watering + timedelta(days=7 * i) for i in range(4)}


def _write_csv(rows: list, output: str) -> None:
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["lux", "temperature", "moisture", "humidity", "soil_temp", "timestamp"])
        writer.writeheader()
        writer.writerows(rows)


@dataclass
class SimulationParams:
    start: datetime
    now: datetime
    interval: timedelta
    watering_set: set
    cloud: np.ndarray
    interval_min: int


def _simulate_rows(params: SimulationParams) -> list:
    rows = []
    state = MoistureState(moisture=70.0, post_watering_steps=0)
    current = params.start
    for _, cloud_val in enumerate(params.cloud):
        if current > params.now:
            break
        time_of_day = current.hour + current.minute / 60.0
        is_day = 7.0 <= time_of_day <= 19.0
        temperature = _compute_temperature(time_of_day)
        state = _step_moisture(state, current in params.watering_set, is_day, temperature, params.interval_min)
        rows.append({
            "lux": _compute_lux(time_of_day, float(cloud_val)),
            "temperature": temperature,
            "moisture": state.moisture,
            "humidity": 0.0,
            "soil_temp": 0.0,
            "timestamp": current.isoformat(),
        })
        current += params.interval
    return rows


def generate(days: int = 25, interval_min: int = 5, output: str = "mocked_data.csv"):
    np.random.seed(42)

    now = datetime.now().replace(second=0, microsecond=0)
    now = now.replace(minute=(now.minute // 5) * 5)
    start = now - timedelta(days=days)
    interval = timedelta(minutes=interval_min)

    total_steps = int((days * 24 * 60) / interval_min) + 2
    cloud = _generate_cloud(total_steps)
    params = SimulationParams(
        start=start, now=now, interval=interval,
        watering_set=_build_watering_set(start), cloud=cloud, interval_min=interval_min
    )
    rows = _simulate_rows(params)

    _write_csv(rows, output)
    print(f"Sugeneruota {len(rows)} eilučių -> {output}")


if __name__ == "__main__":
    generate()
