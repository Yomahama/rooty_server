from pydantic import BaseModel


class SensorDataIn(BaseModel):
    lux: float | None = None
    temperature: float | None = None
    moisture: int | None = None
    battery: int | None = None
    humidity: float | None = None
    soil_temp: float | None = None
    device_id: str = "default"


class SensorDataOut(SensorDataIn):
    timestamp: str
