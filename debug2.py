import pandas as pd
lignes = pd.DataFrame({
    "id_commande": ["A", "A", "B"],
    "id_produit": [1, 2, 1],
    "quantite": [2, 1, 3],
})
produits = pd.DataFrame({
    "id_produit": [1, 1, 2],
    "libelle": ["Tomates", "Tomates ", "Miel"],
    "prix_unitaire": [4.2, 4.2, 7.5],
})
df = lignes.merge(produits, on="id_produit")
print("CA total :", df["prix_unitaire"].sum())