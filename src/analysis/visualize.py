import matplotlib.pyplot as plt
from src.analysis.load_dataset import load_scores
from src.utils.config_loader import load_config
import numpy as np

def main():
    df = load_scores(load_config()["model"]["mode"])
    plt.figure(figsize=(6, 8))
    plt.subplot(211)
    plt.hist(df["pp"], bins=50)
    plt.xlabel("PP")
    plt.ylabel("Count")
    plt.title("PP Distribution")
    plt.subplot(212)
    plt.hist(df["pp"][df['pp']>=0.5].apply(lambda x: np.log(x + 0.5)), bins=50)
    plt.xlabel("ln(PP+0.5)")
    plt.ylabel("Count")
    plt.title("PP Distribution Normalized")
    plt.show()

if __name__ == "__main__":
    main()
