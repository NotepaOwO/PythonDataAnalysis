import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "osu.db"

def load_scores(mode="osu"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT
            user_id,
            pp,
            accuracy,
            score,
            max_combo,
            passed,
            beatmap_id,
            beatmapset_id
        FROM user_scores
        WHERE mode = ?
          AND pp IS NOT NULL
    """, conn, params=(mode,))
    conn.close()
    return df
