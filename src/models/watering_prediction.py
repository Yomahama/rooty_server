from pydantic import BaseModel


class MoisturePoint(BaseModel):
    value: float
    timestamp: str


class WateringPrediction(BaseModel):
    current_moisture: float | None
    predicted_watering_time: str | None
    hours_until_watering: float | None
    confidence: str | None
    historical: list[MoisturePoint]
    predicted: list[MoisturePoint]
