import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.plant_service import PlantService
from services.prediction_service import PredictionService


def visualize_moisture_prediction(plant_id: int = 1):
    prediction_service = PredictionService()
    plant_service = PlantService()

    plant = plant_service.get_by_id(plant_id)
    if not plant:
        print(f"Plant {plant_id} not found!")
        return

    monthly_readings = prediction_service.get_recent(hours=24 * 30)
    prediction = prediction_service.get_watering_prediction(plant)

    print(f"Generating chart for Plant {plant_id}")
    print(f"  Current moisture: {prediction.current_moisture}%")
    print(f"  Monthly readings: {len(monthly_readings)}")
    print(f"  Predicted points: {len(prediction.predicted)}")

    hist_timestamps = mdates.date2num(
        [datetime.fromisoformat(r.timestamp) for r in monthly_readings])
    hist_moisture = [r.moisture for r in monthly_readings]
    hist_temp = [r.temperature for r in monthly_readings]
    hist_lux = [r.lux for r in monthly_readings]

    pred_timestamps = mdates.date2num(
        [datetime.fromisoformat(p.timestamp) for p in prediction.predicted])
    pred_moisture = [p.value for p in prediction.predicted]

    fig, ax_moist = plt.subplots(figsize=(16, 7), dpi=100)

    # Twin axes for temperature and lux
    ax_temp = ax_moist.twinx()
    ax_lux = ax_moist.twinx()
    ax_lux.spines['right'].set_position(('outward', 70))

    # --- Lux (thin line, historical only) ---
    lux_line, = ax_lux.plot(
        hist_timestamps, hist_lux,
        color='#f59e0b', linewidth=0.8, alpha=0.6, label='Lux'
    )
    ax_lux.set_ylabel('Lux', color='#f59e0b', fontsize=10)
    ax_lux.tick_params(axis='y', labelcolor='#f59e0b')
    ax_lux.set_ylim(bottom=0)

    # --- Temperature (thick line, historical only) ---
    temp_line, = ax_temp.plot(
        hist_timestamps, hist_temp,
        color='#dc2626', linewidth=2.5, alpha=0.8, label='Temperature (°C)'
    )
    ax_temp.set_ylabel('Temperature (°C)', color='#dc2626', fontsize=10)
    ax_temp.tick_params(axis='y', labelcolor='#dc2626')

    # --- Moisture historical ---
    moist_hist_line, = ax_moist.plot(
        hist_timestamps, hist_moisture,
        color='#2563eb', linewidth=1.8, alpha=0.9, label='Moisture (historical)'
    )

    # --- Moisture prediction ---
    moist_pred_line, = ax_moist.plot(
        pred_timestamps, pred_moisture,
        color='#2563eb', linewidth=1.8, alpha=0.9, linestyle='--',
        label='Moisture (predicted)'
    )

    # --- Separator: historical / prediction ---
    if len(hist_timestamps):
        sep_mpl = float(hist_timestamps[-1])
        ax_moist.axvline(
            x=sep_mpl, color='#f59e0b', linestyle='-',
            linewidth=2.5, alpha=0.8, label='Now'
        )

    # --- Min / Max thresholds ---
    ax_moist.axhline(
        y=plant.moisture_min, color='#dc2626', linestyle=':',
        linewidth=1.8, alpha=0.8, label=f'Min ({plant.moisture_min}%)'
    )
    ax_moist.axhline(
        y=plant.moisture_max, color='#16a34a', linestyle=':',
        linewidth=1.8, alpha=0.8, label=f'Max ({plant.moisture_max}%)'
    )

    # --- Styling ---
    watering_text = (
        f"{prediction.minutes_until_water // 60}h {prediction.minutes_until_water % 60}min"
        if prediction.minutes_until_water else "not needed"
    )
    ax_moist.set_title(
        f'Plant {plant_id} — moisture, temperature, lux\n'
        f'Current moisture: {prediction.current_moisture}%  |  '
        f'Watering needed in: {watering_text}',
        fontsize=13, fontweight='bold', pad=14
    )
    ax_moist.set_xlabel('Date', fontsize=11)
    ax_moist.set_ylabel('Moisture (%)', color='#2563eb',
                        fontsize=11, fontweight='bold')
    ax_moist.tick_params(axis='y', labelcolor='#2563eb')
    ax_moist.set_ylim(0, 100)
    ax_moist.grid(True, alpha=0.25, linestyle='-', linewidth=0.5)

    ax_moist.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax_moist.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.setp(ax_moist.get_xticklabels(), rotation=45, ha='right')

    # Combined legend (moisture axis owns it)
    all_lines = [moist_hist_line, moist_pred_line, temp_line, lux_line]
    ax_moist.legend(
        handles=all_lines,
        loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10
    )

    plt.tight_layout()
    plt.show()


def main():
    plant_id = 1
    if len(sys.argv) > 1:
        try:
            plant_id = int(sys.argv[1])
        except ValueError:
            print("Invalid plant ID, using default plant ID = 1")

    print(f"Starting moisture visualization for plant {plant_id}...")
    try:
        visualize_moisture_prediction(plant_id)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Value error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
