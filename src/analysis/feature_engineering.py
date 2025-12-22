import pandas as pd

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
