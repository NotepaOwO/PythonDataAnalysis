import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from src.analysis.load_dataset import load_scores
from src.analysis.feature_engineering import build_user_map_matrix
from src.collect.osu_client import OsuApiClient

from src.utils.config_loader import load_config

LIMIT = 500
MODE = load_config()["model"]["mode"]

USR_ID = 36437108 # Enter your own UID
# MAP_ID = 767046

client = OsuApiClient()
config = load_config()["model"]

def main():
    model = joblib.load(config["model_path"])
    print(f"model loaded: {model}")

    df = load_scores(config["mode"])
    _, _, _, _, map_list = build_user_map_matrix(df)

    map_m = model.components_.T

    scores = client.get_user_scores(USR_ID, mode=MODE, limit=LIMIT)

    usr_array = np.zeros((1, len(map_list)))

    b_p_list = []

    for i in scores:
        beatmap_id = i['beatmap']['id']
        if beatmap_id in map_list:
            usr_array[0, map_list.index(beatmap_id)] = i['pp']
        b_p_list.append({'beatmap_id': beatmap_id, 'pp':i['pp']})
    
    b_p_df = pd.DataFrame(b_p_list).set_index('beatmap_id')['pp']

    # nz = np.nonzero(usr_array)
    # usr_array[nz] = np.log(usr_array[nz] + 0.5)
    usr_array = csr_matrix(usr_array)

    usr_m = model.transform(usr_array)[0]

    pred_scores = pd.Series(np.matmul(map_m, usr_m), index=pd.Index(map_list))
    # pred_scores = pd.Series(np.exp(np.matmul(map_m, usr_m)) - 0.5, index=pd.Index(map_list))

    pred_scores.sort_values(ascending=False, inplace=True)

    print('\nRecommended beatmaps:')
    print(f'{"Beatmap Id":<12}Pred PP')
    j = 0
    for bid, pp in pred_scores.items():
        if j > 10:
            break
        elif bid not in b_p_df.index:
            print(f'{bid:<12}{pp:.2f}')
        elif b_p_df[bid] < pp:
            print(f'{bid:<12}{pp:.2f}')
        else:
            continue
        j += 1
    
    top_n = 200
    top_pred = pred_scores.head(top_n)
    
    plt.hist(top_pred, bins=50)
    plt.title(f'PP Distribution for User {USR_ID}')
    plt.xlabel('PP Pred')
    plt.ylabel('Beatmap Count')
    plt.show()

if __name__=='__main__':
    main()