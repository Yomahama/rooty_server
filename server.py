from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

API_KEY = "slaptas-raktas-123"
DB_FILE = "duomenys.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            lux       REAL,
            temp      REAL,
            soil      INTEGER,
            laikas    TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


class SensorData(BaseModel):
    lux:  float
    temp: float
    soil: int


@app.post("/api/sensor-data")
def gauti_duomenis(
    data: SensorData,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Blogas API raktas")

    laikas = datetime.now().isoformat()

    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO measurements (lux, temp, soil, laikas) VALUES (?, ?, ?, ?)",
        (data.lux, data.temp, data.soil, laikas)
    )
    conn.commit()
    conn.close()

    print(f"[{laikas}] lux={data.lux}, temp={data.temp}, soil={data.soil}%")
    return {"status": "ok", "laikas": laikas}

@app.get("/api/latest")
def paskutinis():
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT lux, temp, soil, laikas FROM measurements ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Duomenu nera")

    return {
        "lux":    row[0],
        "temp":   row[1],
        "soil":   row[2],
        "laikas": row[3]
    }

@app.get("/api/history")
def istorija(limit: int = 50):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        "SELECT lux, temp, soil, laikas FROM measurements ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()

    return [
        {"lux": r[0], "temp": r[1], "soil": r[2], "laikas": r[3]}
        for r in rows
    ]
