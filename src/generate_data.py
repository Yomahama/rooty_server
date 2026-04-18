from datetime import datetime, timedelta
import csv
import numpy as np


def generate(days: int = 14, interval_min: int = 1, output: str = "mocked_data.csv"):
    now = datetime.now()
    start = now - timedelta(days=days)
    interval = timedelta(minutes=interval_min)

    rows = []
    moisture = 75.0
    current = start

    while current <= now:
        hour = current.hour

        lux = 0.0
        if 6 <= hour <= 20:
            peak = np.sin(np.pi * (hour - 6) / 14)
            lux = round(float(peak * 4500 + np.random.uniform(-200, 200)), 1)
            lux = max(0.0, lux)

        temperature = round(
            float(18 + 8 * np.sin(np.pi * (hour - 6) / 12) + np.random.uniform(-1, 1)), 1)

        moisture -= np.random.uniform(0.05, 0.2)
        if moisture < 40:
            moisture = 75.0
        moisture = round(moisture, 1)

        rows.append({
            "lux": lux,
            "temperature": temperature,
            "moisture": int(moisture),
            "timestamp": current.isoformat()
        })
        current += interval

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["lux", "temperature", "moisture", "timestamp"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Sugeneruota {len(rows)} eilučių -> {output}")


if __name__ == "__main__":
    generate()
