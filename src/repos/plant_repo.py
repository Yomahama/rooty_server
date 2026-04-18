from core.database import get_connection
from models.plant import Plant


class PlantRepository:
    def get_all(self) -> list[Plant]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, name, dli_min, dli_max, temp_min, temp_max, moisture_min, moisture_max FROM plants").fetchall()
        conn.close()
        return [Plant(id=r[0], name=r[1], dli_min=r[2], dli_max=r[3], temp_min=r[4], temp_max=r[5], moisture_min=r[6], moisture_max=r[7]) for r in rows]

    def get_by_id(self, plant_id: int) -> Plant | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT id, name, dli_min, dli_max, temp_min, temp_max, moisture_min, moisture_max FROM plants WHERE id = ?", (plant_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return Plant(id=row[0], name=row[1], dli_min=row[2], dli_max=row[3], temp_min=row[4], temp_max=row[5], moisture_min=row[6], moisture_max=row[7])
