from fastapi import APIRouter, HTTPException
from models.watering_prediction import WateringPrediction
from services.prediction_service import PredictionService
from services.plant_service import PlantService
from shedulers.model_scheduler import model_scheduler

router = APIRouter(prefix="/api")
prediction_service = PredictionService()
plant_service = PlantService()


@router.get("/predict/watering/{plant_id}", response_model=WateringPrediction)
def get_watering_prediction(plant_id: int):
    plant = plant_service.get_by_id(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Augalas nerastas")
    return prediction_service.get_watering_prediction(plant)


@router.post("/predict/retrain")
def retrain():
    """Execute training manually"""
    readings = prediction_service.get_recent()
    prediction_service.train(readings)
    return {"status": "ok"}


@router.get("/predict/model-status")
def get_model_status():
    """Get current model status and training information"""
    return model_scheduler.get_model_status()
