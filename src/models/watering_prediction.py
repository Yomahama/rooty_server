from pydantic import BaseModel


class MoisturePoint(BaseModel):
    value: float
    timestamp: str


class WateringPrediction(BaseModel):
    current_moisture: int
    minutes_until_water: int | None
    historical: list[MoisturePoint]
    predicted: list[MoisturePoint]
