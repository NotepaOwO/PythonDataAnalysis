from sklearn.decomposition import NMF

from src.analysis.load_dataset import load_scores
from src.analysis.feature_engineering import build_user_map_matrix
import joblib
from pathlib import Path

from src.utils.config_loader import load_config

def main():
    config = load_config()["model"]
    
    df = load_scores(config["mode"])

    _, X, _, _, _ = build_user_map_matrix(df)
    model = NMF(n_components=128, random_state=42, max_iter=2000, alpha_W=0.01, l1_ratio=0.1)
    model.fit(X)
    
    model_path = Path(config["model_path"])
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config["model_path"])

if __name__ == "__main__":
    main()
