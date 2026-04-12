from fastapi import FastAPI
from core.database import init_db
from api.sensor_routes import router as sensor_router
from api.plant_routes import router as plant_router
from api.dli_routes import router as dli_router

app = FastAPI()
init_db()
app.include_router(sensor_router)
app.include_router(plant_router)
app.include_router(dli_router)
