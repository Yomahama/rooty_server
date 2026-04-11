from fastapi import FastAPI
from core.database import init_db
from api.routes import router

app = FastAPI()
init_db()
app.include_router(router)
