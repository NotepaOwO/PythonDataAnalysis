import matplotlib.pyplot as plt
from analysis.load_dataset import load_scores

def main():
    df = load_scores()

    plt.hist(df["pp"], bins=50)
    plt.xlabel("PP")
    plt.ylabel("Count")
    plt.title("PP Distribution")
    plt.show()

if __name__ == "__main__":
    main()
