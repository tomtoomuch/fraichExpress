import json
import pandas as pd
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from etl.load_clean_sqlite import charger_sqlite

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_clean_approvisionnement.log"

# Génération d'un horodatage pour le nom du fichier de journalisation
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = f"{timestamp}_{LOG_FILE}"

# -------------------------------------------------------------------------------
# Configuration du logging
# -------------------------------------------------------------------------------

logging.basicConfig(
    filename=f"{LOG_FILE}",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Fonction pour normaliser  Libellés
# -------------------------------------------------------------------------------


def normaliser_saison(saison):
    if not isinstance(saison, str):
        print(saison)
        return saison

    # Nettoyage de base
    saison = saison.strip().lower()

    saisons = {
        "touteannee": "toute_annee",
        "toute annee": "toute_annee",
        "toute année": "toute_annee",
        "Toute Annee": "toute_annee",
        "toute Annee": "toute_annee",
        "été": "ete",
        "éte": "ete",
        "eté": "ete",
    }

    return saisons.get(saison, saison)


# -------------------------------------------------------------------------------
# Fonction pour normaliser les identifiants de produits
# -------------------------------------------------------------------------------
def normaliser_id_produit(id_produit):
    if not isinstance(id_produit, str):
        return id_produit

    id_produit = int(id_produit)

    return id_produit

# -------------------------------------------------------------------------------
# Fonction pour normaliser les identifiants de producteurs
# -------------------------------------------------------------------------------
def normaliser_id_producteur(id_producteur):
    if not isinstance(id_producteur, str):
        return id_producteur

    id_producteur = int(id_producteur)

    return id_producteur

# -------------------------------------------------------------------------------
# Fonction de chargement du fichier JSON
# -------------------------------------------------------------------------------


def load_data():
    try:
        donnees_approvisionnement, donnees_producteurs, donnees_produits = (
            charger_sqlite()
        )

        logger.info(
            "Récupération réussie des approvisionnements : %d enregistrements lus",
            len(donnees_approvisionnement),
        )
        return donnees_approvisionnement

    except FileNotFoundError:
        logger.error(
            "Erreur lors de la récuperation des données approvisionnements sur la base source_catalogue.db"
        )
        raise

def main():
    try:
    
        logger.info("===== Début du chargement des approvisionnements =====")

        # Lecture des données
        df = load_data()

        print(df)

        nombre_lus = len(df)

        print("Nombre de lignes lues :", nombre_lus)

        # ---------------------------------------------------------------------------
        # Normalisation des saisons
        # ---------------------------------------------------------------------------

        if "saison" in df.columns:

            df["saison"] = df["saison"].apply(normaliser_saison)

        # ---------------------------------------------------------------------------
        # Normalisation des identifiants de produits
        # ---------------------------------------------------------------------------

        if "id_produit" in df.columns:

            df["id_produit"] = df["id_produit"].apply(normaliser_id_produit)

        # ---------------------------------------------------------------------------
        # Vérification des données
        # ---------------------------------------------------------------------------

        nombre_rejetes = 0

        if "saison" in df.columns:

            nombre_rejetes = df["saison"].isna().sum()

            if nombre_rejetes > 0:

                logger.warning("%d saison(s) invalide(s)", nombre_rejetes)

        nombre_acceptes = nombre_lus - nombre_rejetes

        logger.info("Volume lu : %d", nombre_lus)

        logger.info("Volume accepté : %d", nombre_acceptes)

        logger.info("Volume rejeté : %d", nombre_rejetes)

        # ---------------------------------------------------------------------------
        # Connexion à SQLite
        # ---------------------------------------------------------------------------

        conn = sqlite3.connect(DATABASE_FILE)

        # ---------------------------------------------------------------------------
        # Chargement dans SQLite
        # ---------------------------------------------------------------------------

        df.to_sql("clean_approvisionnement", conn, if_exists="replace", index=False)

        conn.close()

        logger.info("Chargement SQLite réussi : table clean_approvisionnement (%d lignes)", len(df))

        logger.info("===== Fin du chargement clean_approvisionnement =====")

        print(f"Données enregistrées dans {DATABASE_FILE}")

        print(
            f"Lues : {nombre_lus} | "
            f"Acceptées : {nombre_acceptes} | "
            f"Rejetées : {nombre_rejetes}"
        )


    except Exception as e:

        logger.exception("Erreur lors du chargement des producteurs : %s", e)

        print("Une erreur est survenue. Consultez le fichier de log :", LOG_FILE)


# -------------------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    main()