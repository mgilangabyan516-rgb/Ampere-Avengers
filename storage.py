import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).with_name("aquadrain.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pressure_1 REAL NOT NULL,
            pressure_2 REAL NOT NULL,
            flow_1 REAL NOT NULL,
            flow_2 REAL NOT NULL,
            pump_status INTEGER NOT NULL,
            source TEXT DEFAULT 'dashboard'
        )
        """)

def save_reading(row, source="dashboard"):
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        INSERT INTO readings(timestamp, pressure_1, pressure_2, flow_1, flow_2, pump_status, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(row["timestamp"]), float(row["pressure_1"]), float(row["pressure_2"]),
              float(row["flow_1"]), float(row["flow_2"]), int(row["pump_status"]), source))

def load_readings(limit=1000):
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?", con, params=(int(limit),)
        ).sort_values("id")
