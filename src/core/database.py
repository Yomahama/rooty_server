import sqlite3
from core.config import settings

DEFAULT_PLANTS = [
    ("Braškės",   12, 16, 15, 26, 60, 80),
    ("Pomidorai", 20, 30, 18, 28, 50, 70),
    ("Salotos",   10, 14, 15, 22, 60, 75),
]

def get_connection():
    return sqlite3.connect(settings.db_file)

def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lux         REAL,
            temperature REAL,
            moisture    INTEGER,
            timestamp   TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            dli_min  REAL,
            dli_max  REAL,
            temp_min REAL,
            temp_max REAL,
            moisture_min INTEGER,
            moisture_max INTEGER
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM plants").fetchone()[0]
    if count == 0:
        conn.executemany(
            """INSERT INTO plants 
               (name, dli_min, dli_max, temp_min, temp_max, moisture_min, moisture_max) 
               VALUES (?,?,?,?,?,?,?)""",
            DEFAULT_PLANTS
        )

    conn.commit()
    conn.close()