from datetime import datetime, timedelta
import csv
from models.sensor import SensorDataOut

CSV_PATH = "mocked_data.csv"


class PredictionRepository:
    def get_all(self) -> list[SensorDataOut]:
        readings = []
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                readings.append(SensorDataOut(
                    lux=float(row["lux"]),
                    temperature=float(row["temperature"]),
                    moisture=int(row["moisture"]),
                    timestamp=row["timestamp"]
                ))
        return readings

    def get_recent(self, hours: int = 24) -> list[SensorDataOut]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            r for r in self.get_all()
            if datetime.fromisoformat(r.timestamp) >= cutoff
        ]
