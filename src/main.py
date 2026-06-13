from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import init_db
from api.routes.sensor_routes import router as sensor_router
from api.routes.plant_routes import router as plant_router
from api.routes.dli_routes import router as dli_router
from api.routes.watering_prediction_routes import router as watering_prediction_router
from api.routes.device import router as device_router
from generate_data import generate


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    generate(days=30)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(sensor_router)
app.include_router(plant_router)
app.include_router(dli_router)
app.include_router(watering_prediction_router)
app.include_router(device_router)
