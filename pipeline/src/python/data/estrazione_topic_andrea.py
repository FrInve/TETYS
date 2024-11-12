import pandas as pd

if __name__ == "__main__":

    df = pd.read_csv("pipeline/src/python/data/export.csv")

    print(df.head())