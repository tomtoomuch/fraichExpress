import pandas as pd
df = pd.read_csv("./data/commandes_2025.csv", sep=";", encoding="latin-1")
print(df.shape)
print(df["quantite"].sum())