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

USR_ID = 31309744
# MAP_ID = 767046

client = OsuApiClient()
config = load_config()["model"]

def main():
    model = joblib.load(config["model_path"])
    print(f"model loaded: {model}")

    df = load_scores(config["mode"])
    X, pp_mean, user_list, map_list = build_user_map_matrix(df)

    map_m = model.components_.T

    scores = client.get_user_scores(USR_ID, mode=MODE, limit=LIMIT)

    usr_array = np.zeros((1, len(map_list)))
    for i in scores:
        beatmap_id = i['beatmap']['id']
        if beatmap_id in map_list:
            usr_array[0, map_list.index(beatmap_id)] = i['pp']

    usr_array = usr_array - pp_mean #np.log(usr_array + 0.5) - pp_mean
    usr_array = csr_matrix(usr_array)

    usr_m = model.transform(usr_array)[0]

    pred_scores = pd.Series(np.matmul(map_m, usr_m) + pp_mean, index=pd.Index(map_list)).apply(lambda x: max(x, 0))
    # pred_scores = pd.Series(np.exp(np.matmul(map_m, usr_m) + pp_mean) - 0.5, index=pd.Index(map_list))

    print('\nRecommended beatmaps:')
    print(pred_scores.nlargest(10))

    plt.hist(pred_scores)
    plt.title(f'PP Distribution for User {USR_ID}')
    plt.xlabel('PP Pred')
    plt.ylabel('Beatmap Count')
    plt.show()

if __name__=='__main__':
    main()