import matplotlib.pyplot as plt
from src.analysis.load_dataset import load_scores
from src.utils.config_loader import load_config

def main():
    df = load_scores(load_config()["model"]["mode"])

    plt.hist(df["pp"], bins=50)
    plt.xlabel("PP")
    plt.ylabel("Count")
    plt.title("PP Distribution")
    plt.show()

if __name__ == "__main__":
    main()
