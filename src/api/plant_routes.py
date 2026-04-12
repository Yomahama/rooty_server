from fastapi import APIRouter, HTTPException
from services.plant_service import PlantService
from models.plant import Plant

plant_service = PlantService()
router = APIRouter(prefix="/api")

@router.get("/plants", response_model=list[Plant])
def get_plants():
    return plant_service.get_all()

@router.get("/plants/{plant_id}", response_model=Plant)
def get_plant(plant_id: int):
    plant = plant_service.get_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant does not exist")
    return plant
