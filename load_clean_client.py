import json
import pandas as pd
import sqlite3
import logging
from pathlib import Path


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

SOURCE_FILE = "data/sources/clients.json"
DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_clean_clients.log"


# -------------------------------------------------------------------------------
# Configuration du logging
# -------------------------------------------------------------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Fonction pour normaliser les villes
# -------------------------------------------------------------------------------

def normaliser_ville(ville):

    if not isinstance(ville, str):
        return ville

    ville = ville.strip().lower()

    villes = {
        "sete": "Sète",
        "sète": "Sète",
        "ales": "Alès",
        "alès": "Alès",
        "agde": "Agde",
        "lodeve": "Lodève",
        "lodève": "Lodève",
        "pezenas": "Pézenas",
        "pézenas": "Pézenas",
        "nimes": "Nîmes",
        "nîmes": "Nîmes",
        "mauguio": "Mauguio",
        "beziers": "Béziers",
        "béziers": "Béziers",
        "millau": "Millau",
        "lunel": "Lunel",
        "montpellier": "Montpellier"
    }

    return villes.get(ville, ville)


# -------------------------------------------------------------------------------
# Fonction de chargement du fichier JSON
# -------------------------------------------------------------------------------

def load_data():

    try:
        with open(
            SOURCE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        logger.info(
            "Lecture réussie du fichier %s : %d enregistrements lus",
            SOURCE_FILE,
            len(data)
        )

        return data

    except FileNotFoundError:
        logger.error(
            "Fichier introuvable : %s",
            SOURCE_FILE
        )
        raise

    except json.JSONDecodeError as e:
        logger.error(
            "Erreur JSON dans %s : %s",
            SOURCE_FILE,
            e
        )
        raise


# -------------------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------------------

try:

    logger.info("===== Début du chargement clients =====")

    # Lecture des données
    data = load_data()

    # Création du DataFrame
    df = pd.DataFrame(data)

    nombre_lus = len(df)

    print("Nombre de lignes lues :", nombre_lus)

    # ---------------------------------------------------------------------------
    # Nettoyage de l'adresse
    # ---------------------------------------------------------------------------

    if "adresse" in df.columns:

        df["ville"] = df["adresse"].apply(
            lambda x: x.get("ville") if isinstance(x, dict) else None
        )

        df["code_postal"] = df["adresse"].apply(
            lambda x: x.get("code_postal") if isinstance(x, dict) else None
        )

        df = df.drop(columns=["adresse"])

    else:

        logger.warning(
            "La colonne 'adresse' est absente du fichier"
        )

    # ---------------------------------------------------------------------------
    # Normalisation des villes
    # ---------------------------------------------------------------------------

    if "ville" in df.columns:

        df["ville"] = df["ville"].apply(normaliser_ville)

    # ---------------------------------------------------------------------------
    # Normalisation des codes postaux
    # ---------------------------------------------------------------------------

    if "code_postal" in df.columns:

        df["code_postal"] = (
            df["code_postal"]
            .astype("string")
            .str.strip()
        )

    # ---------------------------------------------------------------------------
    # Normalisation des dates d'inscription
    # ---------------------------------------------------------------------------

    if "date_inscription" in df.columns:

        df["date_inscription"] = pd.to_datetime(
            df["date_inscription"],
            errors="coerce",
            format="mixed"
        ).dt.strftime("%Y-%m-%d")

    # ---------------------------------------------------------------------------
    # Vérification des données
    # ---------------------------------------------------------------------------

    nombre_rejetes = 0

    if "date_inscription" in df.columns:

        nombre_rejetes = df["date_inscription"].isna().sum()

        if nombre_rejetes > 0:

            logger.warning(
                "%d date(s) d'inscription invalide(s)",
                nombre_rejetes
            )

    nombre_acceptes = nombre_lus - nombre_rejetes

    logger.info(
        "Volume lu : %d",
        nombre_lus
    )

    logger.info(
        "Volume accepté : %d",
        nombre_acceptes
    )

    logger.info(
        "Volume rejeté : %d",
        nombre_rejetes
    )

    # ---------------------------------------------------------------------------
    # Connexion à SQLite
    # ---------------------------------------------------------------------------

    conn = sqlite3.connect(DATABASE_FILE)

    # ---------------------------------------------------------------------------
    # Chargement dans SQLite
    # ---------------------------------------------------------------------------

    df.to_sql(
        "clean_clients",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    logger.info(
        "Chargement SQLite réussi : table clean_clients (%d lignes)",
        len(df)
    )

    logger.info("===== Fin du chargement clients =====")

    print(
        f"Données enregistrées dans {DATABASE_FILE}"
    )

    print(
        f"Lues : {nombre_lus} | "
        f"Acceptées : {nombre_acceptes} | "
        f"Rejetées : {nombre_rejetes}"
    )


except Exception as e:

    logger.exception(
        "Erreur lors du chargement des clients : %s",
        e
    )

    print(
        "Une erreur est survenue. Consultez le fichier de log :",
        LOG_FILE
    )