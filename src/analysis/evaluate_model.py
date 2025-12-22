import joblib
from sklearn.metrics import classification_report
from src.analysis.load_dataset import load_scores
from src.analysis.feature_engineering import build_user_features
from src.analysis.dataset_builder import add_labels

from src.utils.config_loader import load_config

def main():
    config = load_config()["model"]
    
    model = joblib.load(config["model_path"])
    print(f"model loaded: {model}")

    df = load_scores(mode=config["mode"])
    features = add_labels(build_user_features(df))

    X = features.drop(columns=["user_id", "label", "max_pp"])
    y = features["label"]
    
    if X.shape[0] == 0:
        print("❌ 没有可用于评估的数据")
        return

    y_pred = model.predict(X)

    print(classification_report(y, y_pred))

if __name__ == "__main__":
    main()
