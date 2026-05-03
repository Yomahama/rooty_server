from datetime import datetime, timedelta
import csv
import numpy as np


def generate(days: int = 25, interval_min: int = 5, output: str = "mocked_data.csv"):
    np.random.seed(42)

    now = datetime.now().replace(second=0, microsecond=0)
    now = now.replace(minute=(now.minute // 5) * 5)
    start = now - timedelta(days=days)
    interval = timedelta(minutes=interval_min)

    # Laistymas kas 7 dienas 9:00, pradedant 3-ią dieną (iš viso 4 kartai)
    first_watering = (start + timedelta(days=2)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    watering_set = {first_watering + timedelta(days=7 * i) for i in range(4)}

    # Lėtai kintantis debesuotumas (koreliuotas triukšmas)
    total_steps = int((days * 24 * 60) / interval_min) + 2
    cloud = np.zeros(total_steps)
    cloud[0] = 1.0
    for i in range(1, total_steps):
        cloud[i] = cloud[i - 1] + 0.01 * \
            (1.0 - cloud[i - 1]) + np.random.normal(0, 0.04)
        cloud[i] = np.clip(cloud[i], 0.15, 1.3)

    rows = []
    moisture = 70.0
    current = start
    step = 0
    post_watering_steps = 0

    while current <= now:
        hour = current.hour
        minute = current.minute
        time_of_day = hour + minute / 60.0
        is_day = 7.0 <= time_of_day <= 19.0

        is_watering = current in watering_set

        # --- Šviesa (lux) ---
        if is_day:
            peak = np.sin(np.pi * (time_of_day - 7.0) / 12.0)
            lux = float(peak * 4000.0 *
                        cloud[step] + np.random.uniform(-100, 100))
            lux = round(max(0.0, lux), 1)
        else:
            lux = round(float(np.random.uniform(0, 15)), 1)

        # --- Temperatūra (19–26°C) ---
        if 7.0 <= time_of_day <= 21.0:
            temp = 19.0 + 7.0 * np.sin(np.pi * (time_of_day - 7.0) / 14.0)
        else:
            temp = 19.5
        temp += np.random.uniform(-0.5, 0.5)
        temperature = round(float(np.clip(temp, 18.0, 27.0)), 1)

        # --- Drėgmė ---
        if is_watering:
            moisture = round(float(np.random.uniform(75, 90)), 1)
            # ~90 min sulėtintas garavimas
            post_watering_steps = int(90 / interval_min)
        else:
            if is_day:
                evap = np.random.uniform(0.010, 0.030)
                evap *= 1.0 + (temperature - 22.0) * 0.03
            else:
                evap = np.random.uniform(0.005, 0.015)

            if post_watering_steps > 0:
                evap *= 0.25
                post_watering_steps -= 1

            moisture -= evap
            moisture += np.random.normal(0, 0.04)
            moisture = round(float(moisture), 1)

        rows.append({
            "lux": lux,
            "temperature": temperature,
            "moisture": moisture,
            "timestamp": current.isoformat()
        })
        current += interval
        step += 1

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["lux", "temperature", "moisture", "timestamp"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Sugeneruota {len(rows)} eilučių -> {output}")


if __name__ == "__main__":
    generate()
