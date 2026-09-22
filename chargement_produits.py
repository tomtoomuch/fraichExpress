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
        requetes = {
            "approvisionnement": "SELECT * FROM `approvisionnement`",
            "producteurs": "SELECT * from `producteurs`",
            "produits": "SELECT * from `produits`"
            }
        # Déclaration du dictionnaire qui reçoit les résultats
        resultats = {}
        print("Les requêtes sont prêtese à être exécutées.")

        # On charge les données dans un DataFrame
        for cle,requete in enumerate(requetes):
            print(f"{cle} : {requete}")
            resultats[cle] = pd.read_sql_query(requete, connexion)

            print("Requête terminée. Les données de la table 'produits' ont été récupérées.")

        connexion.close()

        print(df)

    except sqlite.OperationalError as error:
        raise ConnectionError(f"Impossible de se connecter à la base SQLite : {error}")
    