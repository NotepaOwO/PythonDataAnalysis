import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np

def build_user_features(df: pd.DataFrame):
    """
    每个 user → 一个样本
    """
    features = df.groupby("user_id").agg(
        mean_pp=("pp", "mean"),
        max_pp=("pp", "max"),
        mean_acc=("accuracy", "mean"),
        max_combo=("max_combo", "max"),
        play_count=("pp", "count"),
        pass_rate=("passed", "mean")
    ).reset_index()

    return features

def build_user_map_matrix(df: pd.DataFrame):
    df = df[df['pp']>=0.5]
    tab = pd.crosstab(
        index=df['user_id'],
        columns=df['beatmap_id'],
        values=df['pp'],
        aggfunc='sum'
    )
    tab.dropna(axis=0, thresh=50, inplace=True) # 筛选游玩数过少的玩家
    tab.dropna(axis=1, thresh=10, inplace=True) # 筛选被游玩次数过少的谱面

    user_list = tab.index.tolist()
    print(f'筛选后玩家总数：{len(user_list)}')
    map_list = tab.columns.tolist()
    print(f'筛选后谱面总数：{len(map_list)}')

    # tab = tab.apply(lambda x: np.log(x + 0.5))
    pp_mean = tab.mean(axis=None)
    tab_norm = (tab - pp_mean).fillna(0)
    sparse_matrix = csr_matrix(tab_norm)

    return sparse_matrix, pp_mean, user_list, map_list
