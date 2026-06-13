from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from repos.device_repo import DeviceRepository
from repos.plant_repo import PlantRepository
from models.plant import Plant

router = APIRouter(prefix="/api/device")

device_repo = DeviceRepository()
plant_repo = PlantRepository()


class AssignPlantRequest(BaseModel):
    plant_id: int


@router.post("/assign-plant", response_model=Plant)
def assign_plant(body: AssignPlantRequest):
    plant = plant_repo.get_by_id(body.plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    device_repo.assign_plant(body.plant_id)
    return plant


@router.get("/current-plant", response_model=Plant)
def get_current_plant():
    plant = device_repo.get_active_plant()
    if not plant:
        raise HTTPException(status_code=404, detail="No plant assigned")
    return plant


@router.delete("/data")
def delete_all_data():
    device_repo.delete_all_data()
    return {"status": "ok"}
