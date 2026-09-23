import json
import pandas as pd
import sqlite3
import logging
from pathlib import Path
from load_data_source_catalogue import charger_sqlite

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_clean_produits.log"


# -------------------------------------------------------------------------------
# Configuration du logging
# -------------------------------------------------------------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Fonction pour normaliser  Libellés
# -------------------------------------------------------------------------------


def normaliser_produit(produit):
    if not isinstance(produit, str):
        return produit

    # Nettoyage de base
    produit = produit.strip().lower()

    produits = {
        "tomates grappe": "Tomates grappe",
        "courgettes": "Courgettes",
        "aubergines": "Aubergines",
        "carottes": "Carottes",
        "pommes de terre": "Pommes de terre",
        "salade batavia": "Salade batavia",
        "poivrons": "Poivrons",
        "oignons doux": "Oignons doux",
        "ail violet": "Ail violet",
        "courge butternut": "Courge butternut",
        "pommes gala": "Pommes Gala",
        "poires conférence": "Poires Conférence",
        "abricots": "Abricots",
        "pêches": "Pêches",
        "raisin muscat": "Raisin muscat",
        "figues": "Figues",
        "melon": "Melon",
        "fraises": "Fraises",
        "miel de garrigue": "Miel de garrigue",
        "miel de châtaignier": "Miel de châtaignier",
        "pollen": "Pollen",
        "confiture d'abricot": "Confiture d'abricot",
        "huile d'olive": "Huile d'olive",
        "olives vertes": "Olives vertes",
        "tapenade noire": "Tapenade noire",
        "vin rouge du domaine": "Vin rouge du Domaine",
        "jus de pomme": "Jus de pomme",
        "pélardon": "Pélardon",
        "roquefort": "Roquefort",
        "tomme de brebis": "Tomme de brebis",
        "yaourt brebis": "Yaourt brebis",
        "fromage blanc": "Fromage blanc",
        "pain de campagne": "Pain de campagne",
        "pain aux céréales": "Pain aux céréales",
        "fougasse aux olives": "Fougasse aux olives",
        "brioche": "Brioche",
        "œufs plein air x6": "Œufs plein air x6",
        "œufs bio x12": "Œufs bio x12",
        "riz de camargue": "Riz de Camargue",
        "sel de camargue": "Sel de Camargue",
    }

    return produits.get(produit, produit)


# -------------------------------------------------------------------------------
# Fonction pour normaliser catégories
# -------------------------------------------------------------------------------
def normaliser_categorie(categorie):
    if not isinstance(categorie, str):
        return categorie

    categorie = categorie.strip().lower()

    categories = {
        "légumes": "Légumes",
        "legumes": "Légumes",
        "fruits": "Fruits",
        "épicerie": "Épicerie",
        "epicerie": "Épicerie",
        "boissons": "Boissons",
        "crèmerie": "Crèmerie",
        "cremerie": "Crèmerie",
        "boulangerie": "Boulangerie",
    }

    return categories.get(categorie, categorie)


# -------------------------------------------------------------------------------
# Fonction de chargement du fichier JSON
# -------------------------------------------------------------------------------


def load_data():
    try:
        donnees_approvisionnement, donnees_producteurs, donnees_produits = (
            charger_sqlite()
        )

        logger.info(
            "Récupération réussie des produits : %d enregistrements lus",
            len(donnees_produits),
        )
        return donnees_produits

    except FileNotFoundError:
        logger.error(
            "Erreur sur la récuperation des données produits sur la base source_catalogue.db"
        )
        raise


# -------------------------------------------------------------------------------
# Programme principal
# -------------------------------------------------------------------------------

try:

    logger.info("===== Début du chargement des produits =====")

    # Lecture des données
    df = load_data()

    nombre_lus = len(df)

    print("Nombre de lignes lues :", nombre_lus)

    # ---------------------------------------------------------------------------
    # Normalisation des libelle produit
    # ---------------------------------------------------------------------------

    if "libelle" in df.columns:

        df["libelle"] = df["libelle"].apply(normaliser_produit)

    # ---------------------------------------------------------------------------
    # Normalisation des categories produit
    # ---------------------------------------------------------------------------

    if "categorie" in df.columns:

        df["categorie"] = df["categorie"].astype("string").str.strip()
        df["categorie"] = df["categorie"].apply(normaliser_categorie)

    # ---------------------------------------------------------------------------
    # Vérification des données
    # ---------------------------------------------------------------------------

    nombre_rejetes = 0

    if "libelle" in df.columns:

        nombre_rejetes = df["libelle"].isna().sum()

        if nombre_rejetes > 0:

            logger.warning("%d libelle(s) invalide(s)", nombre_rejetes)

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

    df.to_sql("clean_produits", conn, if_exists="replace", index=False)

    conn.close()

    logger.info("Chargement SQLite réussi : table clean_produits (%d lignes)", len(df))

    logger.info("===== Fin du chargement clean_produits =====")

    print(f"Données enregistrées dans {DATABASE_FILE}")

    print(
        f"Lues : {nombre_lus} | "
        f"Acceptées : {nombre_acceptes} | "
        f"Rejetées : {nombre_rejetes}"
    )


except Exception as e:

    logger.exception("Erreur lors du chargement des clients : %s", e)

    print("Une erreur est survenue. Consultez le fichier de log :", LOG_FILE)
