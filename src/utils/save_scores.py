import json
from src.utils.db import get_conn

def save_user_scores(user_id: int, scores: list[dict]):
    with get_conn() as conn:
        for s in scores:
            conn.execute("""
            INSERT OR IGNORE INTO user_scores (
                user_id, score_id,
                mode, score, pp, accuracy,
                max_combo, passed,
                rank, created_at,
                beatmap_id, beatmapset_id,
                mods, raw_json
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
                json.dumps(s, ensure_ascii=False)
            ))
