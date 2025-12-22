import joblib
from sklearn.metrics import classification_report
from analysis.load_dataset import load_scores
from analysis.feature_engineering import build_user_features
from analysis.dataset_builder import add_labels

def main():
    model = joblib.load("data/osu_rf_model.pkl")

    df = load_scores()
    features = add_labels(build_user_features(df))

    X = features.drop(columns=["user_id", "label"])
    y = features["label"]

    y_pred = model.predict(X)

    print(classification_report(y, y_pred))

if __name__ == "__main__":
    main()
