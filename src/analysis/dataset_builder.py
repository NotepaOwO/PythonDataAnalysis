def add_labels(df):
    """
    根据 max_pp 打标签
    """
    df["label"] = (df["max_pp"] >= 300).astype(int)
    return df
