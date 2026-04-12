from fastapi import APIRouter, HTTPException
from services.dli_service import DliService
from models.dli_result import DliResult

dli_service = DliService()
router = APIRouter(prefix="/api")

@router.get("/dli/{plant_id}", response_model=DliResult)
def get_dli(plant_id: int):
    result = dli_service.get_today_dli(plant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Plant does not exist")
    return result
