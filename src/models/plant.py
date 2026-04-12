from pydantic import BaseModel

class Plant(BaseModel):
    id: int
    name: str
    dli_min: float
    dli_max: float
    temp_min: float
    temp_max: float
    moisture_min: int
    moisture_max: int

    @property
    def dli_target(self) -> float:
        return (self.dli_min + self.dli_max) / 2
