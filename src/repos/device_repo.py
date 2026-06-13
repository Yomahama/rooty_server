from datetime import datetime
from core.database import get_connection
from models.plant import Plant


class DeviceRepository:
    def assign_plant(self, plant_id: int) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO device_assignments (plant_id, assigned_at) VALUES (?, ?)",
            (plant_id, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def get_active_plant(self) -> Plant | None:
        conn = get_connection()
        row = conn.execute(
            """
            SELECT p.id, p.name, p.dli_min, p.dli_max, p.temp_min, p.temp_max,
                   p.moisture_min, p.moisture_max
            FROM device_assignments da
            JOIN plants p ON p.id = da.plant_id
            ORDER BY da.id DESC
            LIMIT 1
            """
        ).fetchone()
        conn.close()
        if not row:
            return None
        return Plant(
            id=row[0], name=row[1], dli_min=row[2], dli_max=row[3],
            temp_min=row[4], temp_max=row[5], moisture_min=row[6], moisture_max=row[7],
        )

    def delete_all_data(self) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM measurements")
        conn.execute("DELETE FROM device_assignments")
        conn.commit()
        conn.close()
