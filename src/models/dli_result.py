from pydantic import BaseModel

class DliResult(BaseModel):
    current_dli: float
    target_dli: float
    percent: float
