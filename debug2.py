import pandas as pd
# La jointure de dataframe n'est pas pertinente sur la colonne id_produit car il y a un doublon dans la table produits.
# Il faut supprimer les doublons dans la table produits avant de faire la jointure.

lignes = pd.DataFrame({
    "id_commande": ["A", "A", "B"],
    "id_produit": [1, 2, 1],
    "quantite": [2, 1, 3],
})
produits = pd.DataFrame({
    "id_produit": [1, 1, 2],
    "libelle": ["Tomates", "Tomates", "Miel"],
    "prix_unitaire": [4.2, 4.2, 7.5],
})

# Détection des doublons dans la table produits
doublons = produits.duplicated()
if not doublons.empty:
    # Suppression des doublons dans la table produits
    produits = produits.drop_duplicates()
    print("Les doublons détectés dans la table Produits ont été supprimés")

df = lignes.merge(produits, on="id_produit")
# On multiplie le prix unitaire à la quantité pour chaque produit afin d'obtenir le juste prix.
print("CA total :", (df["prix_unitaire"]*df["quantite"]).sum())