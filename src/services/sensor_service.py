from datetime import datetime
from repos.sensor_repo import SensorRepository
from models.sensor import SensorDataIn, SensorDataOut


class SensorService:
    def __init__(self):
        self.repo = SensorRepository()

    def save_reading(self, data: SensorDataIn) -> SensorDataOut:
        timestamp = datetime.now().isoformat()
        self.repo.save(data.lux, data.temperature, data.moisture, data.battery, timestamp)
        print(
            f"[{timestamp}] lux={data.lux}, temperature={data.temperature}, moisture={data.moisture}%, battery={data.battery}%")
        return SensorDataOut(**data.model_dump(), timestamp=timestamp)

    def get_latest(self) -> SensorDataOut | None:
        return self.repo.get_latest()

    def get_history(self, limit: int) -> list[SensorDataOut]:
        return self.repo.get_history(limit)

    def get_by_timerange(self, from_time: str, to_time: str) -> list[SensorDataOut]:
        return self.repo.get_by_timerange(from_time, to_time)
