import sys
import os
from datetime import datetime
from typing import List, Tuple

# Add src to path for relative imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import UnivariateSpline, CubicSpline

from models.watering_prediction import MoisturePoint
from services.plant_service import PlantService
from services.prediction_service import PredictionService


def create_spline_interpolation(data_points: List[MoisturePoint],
                                num_points: int = 300,
                                smoothing: float | None = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create smooth spline interpolation using SciPy.

    Args:
        data_points: List of MoisturePoint objects
        num_points: Number of points for smooth curve
        smoothing: Smoothing factor for UnivariateSpline (None for exact interpolation)

    Returns:
        Tuple of (time_array, moisture_array) for plotting
    """
    if len(data_points) < 2:
        timestamps = [datetime.fromisoformat(p.timestamp) for p in data_points]
        values = [p.value for p in data_points]
        return np.array(timestamps), np.array(values)

    # Convert to numeric arrays
    timestamps = [datetime.fromisoformat(
        p.timestamp).timestamp() for p in data_points]
    values = [p.value for p in data_points]

    timestamps = np.array(timestamps)
    values = np.array(values)

    # Use CubicSpline for exact interpolation or UnivariateSpline for smoothing
    if smoothing is None:
        # Exact interpolation through all points
        spline = CubicSpline(timestamps, values)
    else:
        # Smoothing spline (may not pass through all points exactly)
        spline = UnivariateSpline(timestamps, values, s=smoothing)

    # Generate dense points for smooth curve
    t_smooth = np.linspace(timestamps.min(), timestamps.max(), num_points)
    y_smooth = spline(t_smooth)

    # Clamp values to reasonable moisture range
    y_smooth = np.clip(y_smooth, 0, 100)

    # Convert back to datetime objects
    time_smooth = [datetime.fromtimestamp(t) for t in t_smooth]

    return np.array(time_smooth), y_smooth


def visualize_moisture_prediction(plant_id: int = 1):
    """
    Create and display moisture prediction visualization.

    Args:
        plant_id: ID of the plant to visualize
    """
    # Initialize services
    prediction_service = PredictionService()
    plant_service = PlantService()

    # Get plant and prediction data
    plant = plant_service.get_by_id(plant_id)
    if not plant:
        print(f"Plant {plant_id} not found!")
        return

    prediction = prediction_service.get_watering_prediction(plant)

    print(f"📊 Generating chart for Plant {plant_id}")
    print(f"   Current moisture: {prediction.current_moisture}%")
    print(f"   Historical points: {len(prediction.historical)}")
    print(f"   Predicted points: {len(prediction.predicted)}")

    # Create figure with high DPI for crisp display
    _, ax = plt.subplots(figsize=(14, 8), dpi=100)

    # Generate smooth curves using spline interpolation
    hist_time, hist_smooth = create_spline_interpolation(
        prediction.historical, 300)
    pred_time, pred_smooth = create_spline_interpolation(
        prediction.predicted, 200)

    # Plot smooth curves
    ax.plot(hist_time, hist_smooth,
            color='#2563eb', linewidth=2, alpha=0.9,
            label='Historical (Spline Interpolation)', zorder=3)

    ax.plot(pred_time, pred_smooth,
            color='#2563eb', linewidth=2, alpha=0.9, linestyle='--',
            label='Predicted (Spline Interpolation)', zorder=3)

    # Add separator line between historical and predicted data
    if prediction.historical:
        separator_time = datetime.fromisoformat(
            prediction.historical[-1].timestamp)
        # Convert datetime to matplotlib date number for axvline
        separator_mpl: float = float(mdates.date2num(separator_time))
        ax.axvline(x=separator_mpl, color='#f59e0b', linestyle='-',
                   linewidth=3, alpha=0.8, label='Historical/Prediction Separator')

    # Add threshold lines
    all_times = list(hist_time) + list(pred_time)
    time_range = [min(all_times), max(all_times)]

    ax.axhline(y=plant.moisture_min, color='#dc2626', linestyle=':',
               linewidth=2, alpha=0.8, label=f'Min Threshold ({plant.moisture_min}%)')
    ax.axhline(y=plant.moisture_max, color='#16a34a', linestyle=':',
               linewidth=2, alpha=0.8, label=f'Max Threshold ({plant.moisture_max}%)')

    # Fill area below minimum threshold
    ax.fill_between(time_range, 0, plant.moisture_min,
                    color='#dc2626', alpha=0.1, label='Critical Zone')

    # Styling
    ax.set_title(f'🌱 Moisture Prediction for Plant {plant_id}\n'
                 f'Current: {prediction.current_moisture}% | '
                 f'Watering needed in: {prediction.minutes_until_water or "Not needed"} minutes',
                 fontsize=16, fontweight='bold', pad=20)

    ax.set_xlabel('Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Moisture (%)', fontsize=12, fontweight='bold')

    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

    # Format x-axis
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax.xaxis.set_minor_locator(mdates.HourLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Legend
    ax.legend(loc='best', frameon=True,
              fancybox=True, shadow=True, fontsize=10)

    # Tight layout
    plt.tight_layout()

    # Add statistics text box
    stats_text = (f'Statistics:\n'
                  f'• Data Points: {len(prediction.historical + prediction.predicted)}\n'
                  f'• Time Range: {len(prediction.historical + prediction.predicted)} minutes\n'
                  f'• Interpolation: Cubic Spline (SciPy)\n'
                  f'• Curve Points: {len(hist_smooth) + len(pred_smooth)}')

    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox={'boxstyle': 'round,pad=0.5', 'facecolor': 'lightgray', 'alpha': 0.8})

    print("🎯 Chart generated successfully!")
    print("📈 Displaying interactive plot...")

    # Show plot
    plt.show()


def main():
    """Main entry point for the script."""
    plant_id = 1

    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            plant_id = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid plant ID. Using default plant ID = 1")

    print(f"🚀 Starting moisture visualization for plant {plant_id}...")

    try:
        visualize_moisture_prediction(plant_id)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Value error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
