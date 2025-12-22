from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from analysis.load_dataset import load_scores
from analysis.feature_engineering import build_user_features
from analysis.dataset_builder import add_labels
import joblib

def main():
    df = load_scores(mode="osu")
    features = build_user_features(df)
    features = add_labels(features)

    X = features.drop(columns=["user_id", "label"])
    y = features["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("Accuracy:", acc)

    joblib.dump(model, "data/osu_rf_model.pkl")

if __name__ == "__main__":
    main()
