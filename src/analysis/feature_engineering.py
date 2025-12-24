import pandas as pd
from scipy.sparse import csr_matrix
import numpy as np

def build_user_map_matrix(df: pd.DataFrame):
    df = df[df['pp']>=0.5]

    map_counts = df['beatmap_id'].value_counts()
    df = df[df['beatmap_id'].apply(lambda x: map_counts[x]>=10)] # 筛选被游玩次数过少的谱面

    tab = pd.crosstab(
        index=df['user_id'],
        columns=df['beatmap_id'],
        values=df['pp'],
        aggfunc='sum'
    ).fillna(0)

    print(f'筛选后玩家总数：{tab.shape[0]}')
    print(f'筛选后谱面总数：{tab.shape[1]}')

    # tab = tab.apply(lambda x: np.log(x + 0.5)).fillna(0)

    user_list = tab.index.tolist()
    map_list = tab.columns.tolist()

    test_mask = np.zeros(tab.shape)

    i = 0
    np.random.seed(42)
    for _, col in tab.items():
        idx = np.random.choice(col.to_numpy().nonzero()[0])
        test_mask[idx, i] = 1
        i += 1

    train_split = np.where(np.logical_not(test_mask), tab.to_numpy(), 0)

    train_matrix = csr_matrix(train_split)

    return tab.to_numpy(), train_matrix, test_mask, user_list, map_list
