from fastapi import APIRouter, HTTPException, Header
from models.sensor import SensorDataIn, SensorDataOut
from services.sensor_service import SensorService
from core.config import settings

router = APIRouter(prefix="/api")
service = SensorService()

def _check_key(x_api_key: str | None):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/sensor-data", response_model=SensorDataOut)
def save(data: SensorDataIn, x_api_key: str = Header(None)):
    _check_key(x_api_key)
    return service.save_reading(data)

@router.get("/latest", response_model=SensorDataOut)
def get_latest():
    result = service.get_latest()
    if not result:
        raise HTTPException(status_code=404, detail="Data does not exist")
    return result

@router.get("/history", response_model=list[SensorDataOut])
def get_history(limit: int = 50):
    return service.get_history(limit)
