import logging
from datetime import datetime
from repos.sensor_repo import SensorRepository
from repos.device_repo import DeviceRepository
from models.sensor import SensorDataIn, SensorDataOut
from services.notification_service import LogNotificationService

logger = logging.getLogger(__name__)


class SensorService:
    def __init__(self):
        self.repo = SensorRepository()
        self.device_repo = DeviceRepository()
        self.notification_service = LogNotificationService()

    def save_reading(self, data: SensorDataIn) -> SensorDataOut:
        timestamp = datetime.now().isoformat()
        active_plant = self.device_repo.get_active_plant()
        plant_id = active_plant.id if active_plant else None
        self.repo.save(data, timestamp, device_id=data.device_id, plant_id=plant_id)
        logger.info(
            "[%s] lux=%s, temperature=%s, moisture=%s%%, battery=%s%%, humidity=%s%%, soil_temp=%s",
            timestamp, data.lux, data.temperature, data.moisture,
            data.battery, data.humidity, data.soil_temp,
        )
        if active_plant and data.moisture is not None:
            if data.moisture < active_plant.moisture_min:
                self.notification_service.send_low_moisture_alert(
                    active_plant.name, float(data.moisture), float(active_plant.moisture_min)
                )
            elif data.moisture > active_plant.moisture_max:
                self.notification_service.send_high_moisture_alert(
                    active_plant.name, float(data.moisture), float(active_plant.moisture_max)
                )
        return SensorDataOut(**data.model_dump(), timestamp=timestamp)

    def get_latest(self) -> SensorDataOut | None:
        return self.repo.get_latest()

    def get_history(self, limit: int) -> list[SensorDataOut]:
        return self.repo.get_history(limit)

    def get_by_timerange(self, from_time: str, to_time: str) -> list[SensorDataOut]:
        return self.repo.get_by_timerange(from_time, to_time)
