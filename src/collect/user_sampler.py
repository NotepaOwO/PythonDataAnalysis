import random

def sample_user_ids(
    n: int,
    min_id: int = 1,
    max_id: int = 30_000_000
) -> list[int]:
    """
    随机抽 n 个用户 ID（不保证存在）
    """
    return random.sample(range(min_id, max_id), n)
