# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score

# from src.analysis.feature_engineering import build_user_features
# from src.analysis.dataset_builder import add_labels

from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import NMF

from src.analysis.load_dataset import load_scores
from src.analysis.feature_engineering import build_user_map_matrix
import joblib
from pathlib import Path

from src.utils.config_loader import load_config

def main():
    config = load_config()["model"]
    
    df = load_scores(config["mode"])

    # features = build_user_features(df)
    # features = add_labels(features)

    # X = features.drop(columns=["user_id", "label", "max_pp"])
    # y = features["label"]

    # X_train, X_test, y_train, y_test = train_test_split(
    #     X, y, test_size=0.2, random_state=42
    # )

    # model = RandomForestClassifier(
    #     n_estimators=200,
    #     max_depth=10,
    #     random_state=42
    # )
    # model.fit(X_train, y_train)

    
    # y_pred = model.predict(X_test)
    # acc = accuracy_score(y_test, y_pred)

    # print("Accuracy:", acc)

    _, X, _, _, _ = build_user_map_matrix(df)
    model = NMF(n_components=32, random_state=42, max_iter=500)
    model.fit(X)
    
    model_path = Path(config["model_path"])
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config["model_path"])

if __name__ == "__main__":
    main()
