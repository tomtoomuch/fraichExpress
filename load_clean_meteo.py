import json
import pandas as pd
import sqlite3
import logging
from pathlib import Path


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

SOURCE_FILE = "data/sources/meteo.csv"
DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_clean_meteo.log"


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
        
        df = pd.read_csv(SOURCE_FILE, sep=";", encoding="utf-8")

        logger.info(
            "Lecture réussie du fichier %s : %d enregistrements lus",
            SOURCE_FILE,
            len(df)
        )

        return df

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

    logger.info("===== Début du chargement meteo.csv =====")

    # Lecture des données
    data = load_data()

    # Création du DataFrame
    df = pd.DataFrame(data)

    nombre_lus = len(df)

    print("Nombre de lignes lues :", nombre_lus)

    
    # ---------------------------------------------------------------------------
    # Normalisation des villes
    # ---------------------------------------------------------------------------

    if "ville" in df.columns:

        df["ville"] = df["ville"].apply(normaliser_ville)

   

    # ---------------------------------------------------------------------------
    # Normalisation des dates
    # ---------------------------------------------------------------------------

    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
            format="mixed"
        ).dt.strftime("%Y-%m-%d")
        
    # ---------------------------------------------------------------------------
    # 
    # ---------------------------------------------------------------------------  
        
   
    

     # ---------------------------------------------------------------------------
     # Vérification des doublons
     # ---------------------------------------------------------------------------
    doublons = df.duplicated(
    subset=["date", "ville"]
    ).sum()

    
    
    # ---------------------------------------------------------------------------
    # Vérification des données
    # ---------------------------------------------------------------------------

    nombre_rejetes = 0

    if "date" in df.columns:

        nombre_rejetes = df["date"].isna().sum()

        if nombre_rejetes > 0:

            logger.warning(
                "%d date(s)  invalide(s)",
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
    
    logger.info("Doublons : %d", doublons)
    
    
    #logger.info("Valeures manquantes : %d", df.isnull().sum())
    
    print(df.isnull().sum())
    # ---------------------------------------------------------------------------
    # Traitement des valeures manquantes
    # ---------------------------------------------------------------------------

    # Température : on conserve les valeurs manquantes
    # Pluie : remplacement des valeures manquantes par 0 mm
    df["pluie_mm"] = df["pluie_mm"].fillna(0)
    
    # ---------------------------------------------------------------------------
    # Connexion à SQLite
    # ---------------------------------------------------------------------------

    conn = sqlite3.connect(DATABASE_FILE)

    # ---------------------------------------------------------------------------
    # Chargement dans SQLite
    # ---------------------------------------------------------------------------

    df.to_sql(
        "clean_meteo",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    logger.info(
        "Chargement SQLite réussi : table clean_meteo (%d lignes)",
        len(df)
    )

    logger.info("===== Fin du chargement clean_meteo =====")

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
        "Erreur lors du chargement des données meteos : %s",
        e
    )

    print(
        "Une erreur est survenue. Consultez le fichier de log :",
        LOG_FILE
    )