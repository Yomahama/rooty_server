import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NotificationService(ABC):
    @abstractmethod
    def send_low_moisture_alert(self, plant_name: str, current_moisture: float, threshold: float) -> None:
        pass

    @abstractmethod
    def send_high_moisture_alert(self, plant_name: str, current_moisture: float, threshold: float) -> None:
        pass


class LogNotificationService(NotificationService):
    def send_low_moisture_alert(self, plant_name: str, current_moisture: float, threshold: float) -> None:
        logger.info(
            "🪴 LOW moisture alert: %s is at %.1f%% (threshold: %.1f%%)",
            plant_name, current_moisture, threshold,
        )

    def send_high_moisture_alert(self, plant_name: str, current_moisture: float, threshold: float) -> None:
        logger.info(
            "💧 HIGH moisture alert: %s is at %.1f%% (threshold: %.1f%%)",
            plant_name, current_moisture, threshold,
        )
