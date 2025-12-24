# src/collect/fetch_data.py
import random
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.collect.osu_client import OsuApiClient
from src.utils.db import init_db
from src.utils.db_writer import queue, start_writer
from src.utils.logger import logger
from src.utils.config_loader import load_config


# ----------------------------
# 配置参数
# ----------------------------
TARGET_USERS = 50000
MAX_WORKERS = 8

RANK_TYPE = "performance"
RANK_PAGE_LIMIT = 50          # API 最大 50
RANK_MAX_OFFSET = 10000       # API 实际上最多只支持到这里

LIMIT = 100                   # 每个用户抓多少成绩
MIN_SCORES = 10
MIN_PP = 2000
MIN_PLAY_COUNT = 50
SLEEP_BETWEEN_REQUESTS = 0.1

MODE = load_config()["model"]["mode"]

client = OsuApiClient()


# ============================================================
# Step 0: 抓 global Top10000
# ============================================================
def fetch_global_top10000():
    ranking = []
    offset = 0

    while offset < RANK_MAX_OFFSET:
        try:
            page = client.get_leaderboard(
                mode=MODE,
                type_=RANK_TYPE,
                limit=RANK_PAGE_LIMIT,
                offset=offset
            )
            if not page:
                break

            ranking.extend(page)
            print(
                f"\rFetching global leaderboard: {offset + 1} ~ {offset + len(page)}",
                end=""
            )

            offset += RANK_PAGE_LIMIT
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        except Exception as e:
            logger.error(f"Global leaderboard failed at offset {offset}: {e}")
            break

    print()
    return ranking


# ============================================================
# Step 1: 统计国家分布
# ============================================================
def count_country_distribution(global_ranking):
    counter = Counter()
    for entry in global_ranking:
        country = entry["user"]["country"]["code"]
        counter[country] += 1
    return counter


# ============================================================
# Step 2: 计算每个国家的抽样配额
# ============================================================
def compute_country_quota(counter, target_total):
    total = sum(counter.values())
    quota = {}

    for country, count in counter.items():
        quota[country] = int(count / total * target_total)

    # 处理四舍五入导致的不足
    current_sum = sum(quota.values())
    remaining = target_total - current_sum

    for country in counter:
        if remaining <= 0:
            break
        quota[country] += 1
        remaining -= 1

    return quota


# ============================================================
# Step 3: 按国家抓排行榜用户
# ============================================================
def fetch_users_by_country(country, need_count):
    users = []
    offset = 0
    cnt = need_count // 20 + 1

    while offset < cnt * RANK_PAGE_LIMIT and offset < RANK_MAX_OFFSET:
        try:
            ranking = client.get_leaderboard(
                mode=MODE,
                type_=RANK_TYPE,
                country=country,
                limit=RANK_PAGE_LIMIT,
                offset=offset
            )
            if not ranking or len(ranking) == 0:
                break

            for entry in ranking:
                users.append(entry["user"]["id"])

            offset += RANK_PAGE_LIMIT
            
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        except Exception as e:
            logger.error(f"{country} leaderboard failed at offset {offset}: {e}")
            break
    
    
    return random.sample(users, min(len(users), need_count))


# ============================================================
# Step 4: 按国家分布抽取 10000 用户
# ============================================================
def fetch_users_by_country_distribution():
    global_ranking = fetch_global_top10000()
    logger.info(f"Global ranking size: {len(global_ranking)}")

    country_counter = count_country_distribution(global_ranking)
    quota = compute_country_quota(country_counter, TARGET_USERS)

    all_user_ids = []

    for country, need in quota.items():
        if need <= 0:
            continue

        logger.info(f"Fetching {need} users from {country}")
        users = fetch_users_by_country(country, need)
        all_user_ids.extend(users)

    # 防止重复 & 打乱
    all_user_ids = list(set(all_user_ids))
    random.shuffle(all_user_ids)

    return all_user_ids[:TARGET_USERS]


# ============================================================
# Step 5: 抓取单个用户信息
# ============================================================
def fetch_user_info(uid):
    try:
        user = client.get_user(uid, mode=MODE)
        stats = user.get("statistics", {})

        if stats.get("pp", 0) < MIN_PP:
            return False
        if stats.get("play_count", 0) < MIN_PLAY_COUNT:
            return False

        scores = client.get_user_scores(uid, mode=MODE, limit=LIMIT)
        if len(scores) < MIN_SCORES:
            return False

        queue.put(("user", user))
        queue.put(("scores", uid, MODE, scores))
        return True

    except Exception as e:
        logger.error(f"user {uid} failed: {e}")
        return False


# ============================================================
# main
# ============================================================
def main():
    init_db()
    start_writer()

    candidate_user_ids = fetch_users_by_country_distribution()
    print(f"Candidate users fetched: {len(candidate_user_ids)}")

    success_users = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [
            pool.submit(fetch_user_info, uid)
            for uid in candidate_user_ids
        ]

        for future in as_completed(futures):
            if future.result():
                success_users += 1
                print(
                    f"\rUsers fetched: {success_users}/{TARGET_USERS}",
                    end=""
                )

            if success_users >= TARGET_USERS:
                break

    print("\nWaiting for DB writer...")
    queue.join()
    queue.put(None)

    print("All done!")


if __name__ == "__main__":
    main()
