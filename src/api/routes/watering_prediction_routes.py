from fastapi import APIRouter
from models.watering_prediction import WateringPrediction
from services.prediction_service import PredictionService

router = APIRouter(prefix="/api")
prediction_service = PredictionService()


@router.get("/prediction", response_model=WateringPrediction)
def get_prediction():
    return prediction_service.get_watering_prediction()
