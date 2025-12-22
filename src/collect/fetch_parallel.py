# src/collect/fetch_data.py
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time
from src.collect.osu_client import OsuApiClient
from src.utils.db import init_db
from src.utils.db_writer import queue, start_writer
from src.utils.logger import logger

TARGET_USERS = 10_000
MAX_WORKERS = 8
MODE = "mania"

client = OsuApiClient()

def fetch_one(uid):
    try:
        scores = client.get_user_scores(uid, mode=MODE)
        if scores:
            queue.put((uid, scores))
            return True
    except Exception as e:
        logger.error(f"user {uid} failed: {e}")
    return False

def main():
    init_db()
    start_writer()

    candidates = random.sample(range(1, 30_000_000), TARGET_USERS * 6)
    success = 0

    with ThreadPoolExecutor(MAX_WORKERS) as pool:
        futures = [pool.submit(fetch_one, uid) for uid in candidates]

        for f in as_completed(futures):
            # print("waht")
            if f.result():
                
                success += 1
                print(f"{success}/{TARGET_USERS}")
                if success >= TARGET_USERS:
                    break

    queue.put(None)
    print("Done")

if __name__ == "__main__":
    main()
