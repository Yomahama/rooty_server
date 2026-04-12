from datetime import date
from models.plant import Plant
from models.dli_result import DliResult
from services.sensor_service import SensorService
from repos.plant_repo import PlantRepository

LUX_TO_PPFD = 0.0185

class DliService:
    def __init__(self):
        self.sensor_service = SensorService()
        self.plant_repo = PlantRepository()

    def calculate_dli(self, readings: list[dict], plant: Plant, interval_s: int = 60) -> DliResult:
        ppfd_sum = sum(r["lux"] * LUX_TO_PPFD for r in readings)
        dli = ppfd_sum * interval_s / 1_000_000

        return DliResult(
            current_dli=round(dli, 2),
            target_dli=plant.dli_target,
            percent=round((dli / plant.dli_target) * 100, 1),
        )

    def get_today_dli(self, plant_id: int) -> DliResult | None:
        plant = self.plant_repo.get_by_id(plant_id)
        if not plant:
            return None

        today = date.today().isoformat()
        readings = self.sensor_service.get_by_timerange(
            f"{today}T00:00:00",
            f"{today}T23:59:59"
        )

        return self.calculate_dli([r.model_dump() for r in readings], plant)