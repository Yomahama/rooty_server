from repos.plant_repo import PlantRepository
from models.plant import Plant

class PlantService:
    def __init__(self):
        self.repo = PlantRepository()

    def get_all(self) -> list[Plant]:
        return self.repo.get_all()

    def get_by_id(self, plant_id: int) -> Plant | None:
        return self.repo.get_by_id(plant_id)