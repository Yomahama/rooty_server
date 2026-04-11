from pydantic import BaseModel

class SensorDataIn(BaseModel):
    lux: float
    temperature: float
    moisture: int # in %

class SensorDataOut(SensorDataIn):
    timestamp: str
