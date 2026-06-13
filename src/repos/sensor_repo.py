from core.database import get_connection
from models.sensor import SensorDataIn, SensorDataOut


class SensorRepository:
    def save(self, data: SensorDataIn, timestamp: str, device_id: str | None = None, plant_id: int | None = None) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO measurements (lux, temperature, moisture, battery, humidity, soil_temp, timestamp, device_id, plant_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (data.lux, data.temperature, data.moisture, data.battery, data.humidity, data.soil_temp, timestamp, device_id, plant_id),
        )
        conn.commit()
        conn.close()

    def get_latest(self) -> SensorDataOut | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT lux, temperature, moisture, battery, humidity, soil_temp, timestamp FROM measurements ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return None
        return SensorDataOut(
            lux=row[0], temperature=row[1], moisture=row[2], battery=row[3],
            humidity=row[4], soil_temp=row[5], timestamp=row[6]
        )

    def get_history(self, limit: int = 50) -> list[SensorDataOut]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT lux, temperature, moisture, battery, humidity, soil_temp, timestamp FROM measurements ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [
            SensorDataOut(
                lux=r[0], temperature=r[1], moisture=r[2], battery=r[3],
                humidity=r[4], soil_temp=r[5], timestamp=r[6]
            )
            for r in rows
        ]

    def get_by_timerange(self, from_time: str, to_time: str) -> list[SensorDataOut]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT lux, temperature, moisture, battery, humidity, soil_temp, timestamp FROM measurements WHERE timestamp BETWEEN ? AND ?",
            (from_time, to_time)
        ).fetchall()
        conn.close()
        return [
            SensorDataOut(
                lux=r[0], temperature=r[1], moisture=r[2], battery=r[3],
                humidity=r[4], soil_temp=r[5], timestamp=r[6]
            )
            for r in rows
        ]

    def get_recent_by_plant(self, plant_id: int, hours: int) -> list[SensorDataOut]:
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT lux, temperature, moisture, battery, humidity, soil_temp, timestamp
            FROM measurements
            WHERE plant_id = ?
              AND timestamp >= datetime('now', ? || ' hours')
            ORDER BY timestamp ASC
            """,
            (plant_id, f"-{hours}"),
        ).fetchall()
        conn.close()
        return [
            SensorDataOut(
                lux=r[0], temperature=r[1], moisture=r[2], battery=r[3],
                humidity=r[4], soil_temp=r[5], timestamp=r[6]
            )
            for r in rows
        ]
