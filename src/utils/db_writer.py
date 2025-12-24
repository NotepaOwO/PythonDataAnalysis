# src/utils/db_writer.py
from queue import Queue
import threading
import json
from src.utils.db import get_conn
from datetime import datetime, timezone

queue = Queue()

def writer_loop():
    conn = get_conn()
    cnt = 0
    while True:
        item = queue.get()
        try:
            if item is None:
                break

            kind = item[0]

            if kind == "user":
                user = item[1]
                stats = user.get("statistics", {})
                level = user.get("level", {})
                conn.execute("""
                INSERT OR REPLACE INTO users (
                    user_id, mode, username, country_code,
                    total_pp, global_rank, country_rank,
                    accuracy, play_count, level, level_progress,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user["id"],
                    user["playmode"],
                    user["username"],
                    user.get("country", {}).get("code"),
                    stats.get("pp"),
                    stats.get("global_rank"),
                    stats.get("country_rank"),
                    stats.get("hit_accuracy"),
                    stats.get("play_count"),
                    level.get("current", 0),
                    level.get("progress", 0),
                    datetime.now(timezone.utc).isoformat(),
                ))

            elif kind == "scores":
                _, user_id, mode, scores = item
                for s in scores:
                    conn.execute("""
                    INSERT OR IGNORE INTO user_scores (
                        score_id, user_id, mode,
                        beatmap_id, beatmapset_id,
                        score, pp, accuracy,
                        max_combo, passed, rank,
                        created_at, mods
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        s["id"],
                        user_id,
                        mode,
                        s["beatmap"]["id"],
                        s["beatmapset"]["id"],
                        s["score"],
                        s.get("pp"),
                        s["accuracy"],
                        s["max_combo"],
                        int(s["passed"]),
                        s["rank"],
                        s["created_at"],
                        json.dumps(s.get("mods", [])),
                    ))
            cnt += 1
            if cnt % 20 == 0:
                conn.commit()
            # queue.task_done()
        finally:
            queue.task_done()

    conn.commit()
    conn.close()

def start_writer():
    t = threading.Thread(target=writer_loop, daemon=True)
    t.start()
