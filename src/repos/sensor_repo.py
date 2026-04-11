from core.database import get_connection
from models.sensor import SensorDataOut

class SensorRepository:
    def save(self, lux: float, temperature: float, moisture: int, timestamp: str) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO measurements (lux, temperature, moisture, timestamp) VALUES (?, ?, ?, ?)",
            (lux, temperature, moisture, timestamp),
        )
        conn.commit()
        conn.close()

    def get_latest(self) -> SensorDataOut | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT lux, temperature, moisture, timestamp FROM measurements ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return None
        return SensorDataOut(lux=row[0], temperature=row[1], moisture=row[2], timestamp=row[3])

    def get_history(self, limit: int = 50) -> list[SensorDataOut]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT lux, temperature, moisture, timestamp FROM measurements ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [SensorDataOut(lux=r[0], temperature=r[1], moisture=r[2], timestamp=r[3]) for r in rows]
