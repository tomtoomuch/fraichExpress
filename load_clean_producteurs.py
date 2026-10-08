import json
import pandas as pd
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from load_clean_sqlite import charger_sqlite

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_clean_producteurs.log"

# Génération d'un horodatage pour le nom du fichier de journalisation
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# -------------------------------------------------------------------------------
# Configuration du logging
# -------------------------------------------------------------------------------

logging.basicConfig(
    filename=f"{timestamp}_{LOG_FILE}",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Fonction pour normaliser  Libellés
# -------------------------------------------------------------------------------


def normaliser_producteur(nom):
    if not isinstance(nom, str):
        print(nom)
        return nom

    # Nettoyage de base
    nom = nom.strip().lower()

    noms = {
        "ferme des garrigues": "Ferme des Garrigues",
        "Ferme des garrigues": "Ferme des Garrigues",
        "ferme des Garrigues": "Ferme des Garrigues",
        "maraichers de thau": "Maraîchers de Thau",
        "Maraichers de thau": "Maraîchers de Thau",
        "maraîchers de Thau": "Maraîchers de Thau",
        "domaine de la combe": "Domaine de la Combe",
        "domaine de la Combe": "Domaine de la Combe",
        "Domaine de la combe": "Domaine de la Combe",
        "verger de pezenas": "Verger de Pézenas",
        "Verger de pezenas": "Verger de Pézenas",
        "verger de Pézenas": "Verger de Pézenas",
        "rucher des cevennes": "Rucher des Cévennes",
        "Rucher des cevennes": "Rucher des Cévennes",
        "rucher des Cévennes": "Rucher des Cévennes",
        "fromagerie du larzac": "Fromagerie du Larzac",
        "fromagerie du Larzac": "Fromagerie du Larzac",
        "fromagerie de Larzac": "Fromagerie du Larzac",
        "boulangerie paysanne": "Boulangerie Paysanne",
        "Boulangerie paysanne": "Boulangerie Paysanne",
        "boulangerie Paysanne": "Boulangerie Paysanne",
        "camargue gourmande": "Camargue Gourmande",
        "Camargue gourmande": "Camargue Gourmande",
        "camargue Gourmande": "Camargue Gourmande",
    }

    return noms.get(nom, nom)


# -------------------------------------------------------------------------------
# Fonction pour normaliser communes
# -------------------------------------------------------------------------------
def normaliser_commune(commmune):
    if not isinstance(commmune, str):
        return commmune

    commmune = commmune.strip().lower()

    communes = {
        "gignac": "Gignac",
        "sète": "Sète",
        "Sete": "Sète",
        "séte": "Sète",
        "sete": "Sète",
        "lodève": "Lodève",
        "lodeve": "Lodève",
        "Lodeve": "Lodève",
        "pézenas": "Pézenas",
        "pezenas": "Pézenas",
        "Pezenas": "Pézenas",
        "Pézena": "Pézenas",
        "levigan": "Le Vigan",
        "le vigan": "Le Vigan",
        "Le vigan": "Le Vigan",
        "le Vigan": "Le Vigan",
        "millau": "Millau",
        "ganges": "Ganges",
        "gange": "Ganges",
        "Gange": "Ganges",
        "aigues mortes": "Aigues-Mortes",
        "aigues-mortes": "Aigues-Mortes",
        "aigues mortes": "Aigues-Mortes",
        "Aigues Mortes": "Aigues-Mortes",
        "aigues Mortes": "Aigues-Mortes",
    }

    return communes.get(commmune, commmune)


# -------------------------------------------------------------------------------
# Fonction de chargement du fichier JSON
# -------------------------------------------------------------------------------


def load_data():
    try:
        donnees_approvisionnement, donnees_produits, donnees_producteurs = (
            charger_sqlite()
        )

        logger.info(
            "Récupération réussie des producteurs : %d enregistrements lus",
            len(donnees_producteurs),
        )
        return donnees_producteurs

    except FileNotFoundError:
        logger.error(
            "Erreur lors de la récuperation des données producteurs sur la base source_catalogue.db"
        )
        raise


# -------------------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    try:

        logger.info("===== Début du chargement des producteurs =====")

        # Lecture des données
        df = load_data()

        print(df)

        nombre_lus = len(df)

        print("Nombre de lignes lues :", nombre_lus)

        # ---------------------------------------------------------------------------
        # Normalisation des noms des producteurs
        # ---------------------------------------------------------------------------

        if "nom" in df.columns:

            df["nom"] = df["nom"].apply(normaliser_producteur)

        # ---------------------------------------------------------------------------
        # Normalisation des communes des producteurs
        # ---------------------------------------------------------------------------

        if "commune" in df.columns:

            df["commune"] = df["commune"].astype("string").str.strip()
            df["commune"] = df["commune"].apply(normaliser_commune)

        # ---------------------------------------------------------------------------
        # Vérification des données
        # ---------------------------------------------------------------------------

        nombre_rejetes = 0

        if "nom" in df.columns:

            nombre_rejetes = df["nom"].isna().sum()

            if nombre_rejetes > 0:

                logger.warning("%d nom(s) invalide(s)", nombre_rejetes)

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

        df.to_sql("clean_producteurs", conn, if_exists="replace", index=False)

        conn.close()

        logger.info("Chargement SQLite réussi : table clean_producteurs (%d lignes)", len(df))

        logger.info("===== Fin du chargement clean_producteurs =====")

        print(f"Données enregistrées dans {DATABASE_FILE}")

        print(
            f"Lues : {nombre_lus} | "
            f"Acceptées : {nombre_acceptes} | "
            f"Rejetées : {nombre_rejetes}"
        )


    except Exception as e:

        logger.exception("Erreur lors du chargement des producteurs : %s", e)

        print("Une erreur est survenue. Consultez le fichier de log :", LOG_FILE)
