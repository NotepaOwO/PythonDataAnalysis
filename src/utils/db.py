import sqlite3
from pathlib import Path

from datetime import datetime
now_str = datetime.now().strftime("%Y%m%d%H%M") + ".db"

DB_PATH = Path(__file__).resolve().parents[2] / "data" / now_str

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score_id INTEGER UNIQUE,

            mode TEXT,
            score INTEGER,
            pp REAL,
            accuracy REAL,
            max_combo INTEGER,
            passed INTEGER,

            rank TEXT,
            created_at TEXT,

            beatmap_id INTEGER,
            beatmapset_id INTEGER,

            mods TEXT,
            raw_json TEXT
        );
        """)

