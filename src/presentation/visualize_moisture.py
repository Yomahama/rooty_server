import csv
import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.sensor import SensorDataOut  # pylint: disable=wrong-import-position
from models.plant import Plant  # pylint: disable=wrong-import-position
from services.plant_service import PlantService  # pylint: disable=wrong-import-position
from services.prediction_service import PredictionService  # pylint: disable=wrong-import-position

CSV_PATH = "mocked_data.csv"


def _load_csv(path: str) -> list[SensorDataOut]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}. Run generate_data.py first.")
    readings = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            readings.append(SensorDataOut(
                lux=float(row["lux"]),
                temperature=float(row["temperature"]),
                moisture=int(float(row["moisture"])),
                battery=0,
                humidity=float(row.get("humidity", 0.0)),
                soil_temp=float(row.get("soil_temp", 0.0)),
                timestamp=row["timestamp"],
            ))
    return readings


def _plot(plant: Plant, prediction, readings: list[SensorDataOut]) -> None:
    hist_timestamps = mdates.date2num(
        [datetime.fromisoformat(r.timestamp) for r in readings])
    hist_moisture = [r.moisture for r in readings]

    pred_timestamps = mdates.date2num(
        [datetime.fromisoformat(p.timestamp) for p in prediction.predicted])
    pred_moisture = [p.value for p in prediction.predicted]

    _, ax = plt.subplots(figsize=(16, 7), dpi=100)

    hist_line, = ax.plot(
        hist_timestamps, hist_moisture,
        color='#2563eb', linewidth=1.5, alpha=0.9, label='Moisture (historical)'
    )
    pred_line, = ax.plot(
        pred_timestamps, pred_moisture,
        color='#2563eb', linewidth=1.5, alpha=0.9, linestyle='--',
        label='Moisture (predicted)'
    )

    if len(hist_timestamps) > 0:
        ax.axvline(x=float(hist_timestamps[-1]), color='#f59e0b',
                   linewidth=2.0, alpha=0.8, label='Now')

    ax.axhline(y=plant.moisture_min, color='#dc2626', linestyle=':',
               linewidth=1.5, alpha=0.8, label=f'Min ({plant.moisture_min}%)')
    ax.axhline(y=plant.moisture_max, color='#16a34a', linestyle=':',
               linewidth=1.5, alpha=0.8, label=f'Max ({plant.moisture_max}%)')

    watering_text = f"in {prediction.hours_until_watering}h" if prediction.hours_until_watering else "not predicted"
    ax.set_title(
        f'{plant.name} — moisture forecast\n'
        f'Current: {prediction.current_moisture}%  |  '
        f'Confidence: {prediction.confidence or "n/a"}  |  '
        f'Watering: {watering_text}',
        fontsize=13, fontweight='bold', pad=14,
    )
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Moisture (%)', color='#2563eb', fontsize=11, fontweight='bold')
    ax.tick_params(axis='y', labelcolor='#2563eb')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.5)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend(handles=[hist_line, pred_line], loc='upper left',
              frameon=True, fancybox=True, shadow=True, fontsize=10)

    plt.tight_layout()
    plt.show()


def visualize(plant_id: int = 1) -> None:
    plant_service = PlantService()
    prediction_service = PredictionService()

    plant = plant_service.get_by_id(plant_id)
    if not plant:
        print(f"Plant {plant_id} not found in DB.")
        return

    readings = _load_csv(CSV_PATH)
    prediction = prediction_service.predict_for_readings(plant, readings)

    print(f"Plant: {plant.name}")
    print(f"  Historical readings: {len(readings)}")
    print(f"  Current moisture:    {prediction.current_moisture}%")
    print(f"  Confidence:          {prediction.confidence or 'n/a'}")
    print(f"  Watering in:         {prediction.hours_until_watering}h" if prediction.hours_until_watering else "  Watering:           not predicted")

    _plot(plant, prediction, readings)


def main() -> None:
    plant_id = 1
    if len(sys.argv) > 1:
        try:
            plant_id = int(sys.argv[1])
        except ValueError:
            print("Invalid plant ID, using 1")

    try:
        visualize(plant_id)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
