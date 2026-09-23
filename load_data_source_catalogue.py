# Le script chargement_produits.py se connecte à la base de données source_catalogue.db,
# récupère les données, les normalise et les prépare pour l'insertion dans la base de données
# fraichexpress.db
# Importation des moduules nécessaires
from pathlib import Path
import pandas as pd
import sqlite3 as sqlite

RACINE = Path("./")
DOSSIER_SOURCES = Path("./data/sources/")
CHEMIN_BDD = ""

def charger_sqlite():
    # Recherche du fichier "source_catalogue.db"
    for chemin in DOSSIER_SOURCES.rglob("source_catalogue.db"):
        CHEMIN_BDD = chemin
        try:
            # Stockage de l'uri de la BDD en incluant le paramètre
            # garantissant d'accéder aux données en lecture seule
            uri = f"file:{CHEMIN_BDD}?mode=ro"

            # Connexion à la base de données source_catalogue.db
            connexion = sqlite.connect(uri, uri=True)
            print("Connexion à la base de données établie...")

            # Définition de la requête SQL pouor récupérer les données
            requetes = [
                { "code":"approvisionnement",
                "req":"SELECT * FROM `approvisionnement`" },
                { "code":"producteurs",
                "req":"SELECT * from `producteurs`" },
                { "code":"produits",
                "req":"SELECT * from `produits`" },
                ]
            # Déclaration du dictionnaire qui reçoit les résultats
            resultats = {}
            print("Les requêtes sont prêtese à être exécutées.")

            # On charge les données dans un DataFrame
            for requete in requetes:
                print(f"{requete["code"]} : {requete["req"]}")
                df = pd.read_sql_query(requete["req"], connexion)
                resultats[requete["code"]] = df

                print(f"Requête terminée. Les données de la table '{requete["code"]}' ont été récupérées.")

            connexion.close()
            print("La récupération des données est terminées.")
            #print(resultats)
            donnees_approvisionnement = resultats["approvisionnement"]
            donnees_producteurs = resultats["producteurs"]
            donnees_produits = resultats["produits"]

        except sqlite.OperationalError as error:
            raise ConnectionError(f"Impossible de se connecter à la base SQLite : {error}")

    return donnees_approvisionnement,donnees_producteurs,donnees_produits

if __name__ == "__main__":
    donnees_approvisionnement,donnees_producteurs,donnees_produits = charger_sqlite()
    print("Donnees appro")
    print(donnees_approvisionnement)
    print("Donnees producteurs")
    print(donnees_producteurs)
    print("Donnees produits")
    print(donnees_produits)