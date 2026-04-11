import sqlite3
from core.config import settings

def get_connection():
    return sqlite3.connect(settings.db_file)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lux REAL,
            temperature REAL,
            moisture INTEGER,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()
