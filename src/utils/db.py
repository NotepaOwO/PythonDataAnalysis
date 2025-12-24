# src/utils/db.py
import sqlite3
from pathlib import Path
from datetime import datetime

now_str = datetime.now().strftime("%Y%m%d%H%M") + ".db"
DB_PATH = Path(__file__).resolve().parents[2] / "data" / now_str

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(
        DB_PATH,
        timeout=30,
        isolation_level=None,  # autocommit
        check_same_thread=False
    )

def init_db():
    """初始化数据库和表"""
    with get_conn() as conn:
        conn.executescript("""
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;

        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER NOT NULL,
            mode TEXT NOT NULL,
            username TEXT,
            country_code TEXT,
            total_pp REAL,
            global_rank INTEGER,
            country_rank INTEGER,
            accuracy REAL,
            play_count INTEGER,
            level INTEGER,
            level_progress REAL,
            updated_at TEXT,
            PRIMARY KEY (user_id, mode)
        );

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
            mods TEXT
        );
        """)
