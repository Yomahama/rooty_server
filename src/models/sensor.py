from pydantic import BaseModel


class SensorDataIn(BaseModel):
    lux: float
    temperature: float
    moisture: int
    battery: int
    humidity: float
    soil_temp: float


class SensorDataOut(SensorDataIn):
    timestamp: str
