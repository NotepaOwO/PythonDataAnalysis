# src/utils/db_writer.py
from queue import Queue
import threading
import json
from src.utils.db import get_conn

queue = Queue()

def writer_loop():
    conn = get_conn()
    while True:
        item = queue.get()
        if item is None:
            break
        user_id, scores = item
        for s in scores:
            conn.execute("""
            INSERT OR IGNORE INTO user_scores (
                user_id, score_id, mode, score, pp, accuracy,
                max_combo, passed, rank, created_at,
                beatmap_id, beatmapset_id, mods, raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                s["id"],
                s["mode"],
                s["score"],
                s.get("pp"),
                s["accuracy"],
                s["max_combo"],
                int(s["passed"]),
                s["rank"],
                s["created_at"],
                s["beatmap"]["id"],
                s["beatmapset"]["id"],
                json.dumps(s["mods"]),
                json.dumps(s)
            ))
        conn.commit()
        queue.task_done()

def start_writer():
    t = threading.Thread(target=writer_loop, daemon=True)
    t.start()
