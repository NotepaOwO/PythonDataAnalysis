import joblib
import numpy as np
from src.analysis.load_dataset import load_scores
from src.analysis.feature_engineering import build_user_map_matrix

from src.utils.config_loader import load_config

def main():
    config = load_config()["model"]
    
    model = joblib.load(config["model_path"])
    print(f"model loaded: {model}")

    df = load_scores(mode=config["mode"])
    X, X_train, test_mask, _, _ = build_user_map_matrix(df)

    map_m = model.components_
    user_m = model.transform(X_train)

    X_pred = np.dot(user_m, map_m)

    test_real = np.where(test_mask, X, 0)
    test_pred = np.where(test_mask, X_pred, 0)

    mae = np.abs(test_real - test_pred).mean(axis=None)
    nmse = np.sqrt(((test_real - test_pred) ** 2).mean(axis=None))

    print('Test MAE:', mae)
    print('Test NMSE:', nmse)

if __name__ == "__main__":
    main()
