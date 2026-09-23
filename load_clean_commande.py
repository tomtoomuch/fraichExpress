import json
import pandas as pd
import sqlite3
import logging
from pathlib import Path


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

SOURCE_FILE = "data/sources/commandes_2025.csv"
DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_clean_commande.log"


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
# Fonction pour normaliser les statuts des commandes
# -------------------------------------------------------------------------------

def normaliser_statut(statut):
    if not isinstance(statut, str):
        return statut

    statut = statut.strip().lower()

    statuts = {
        "livree": "Livrée",
        "livrée": "Livrée",
        "annulee": "Annulée",
        "annulée": "Annulée"
    }

    return statuts.get(statut, statut)

# -------------------------------------------------------------------------------
# Fonction pour normaliser les modes de livraison des commandes 
# -------------------------------------------------------------------------------
def normaliser_mode_livraison(mode):
    if not isinstance(mode, str):
        return mode

    mode = mode.strip().lower()

    modes = {
        "domicile": "Domicile",
        "point_relais": "Point relais",
        "retrait_ferme": "Retrait ferme"
    }

    return modes.get(mode, mode)


# -------------------------------------------------------------------------------
# Fonction de chargement du fichier JSON
# -------------------------------------------------------------------------------

def load_data():

    try:
        
        df = pd.read_csv(SOURCE_FILE, sep=";", encoding="latin-1")

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

    logger.info("===== Début du chargement commandes_2025.csv =====")

    # Lecture des données
    data = load_data()
    

    # Création du DataFrame
    df = pd.DataFrame(data)
    
    
    #---------------------------------------------------------------------------
    # Ajout clé primaire 
    df.insert(0, "id", range(1, len(df) + 1))
    # ---------------------------------------------------------------------------
    
    # ---------------------------------------------------------------------------
    # Normalisation des dates
    # ---------------------------------------------------------------------------
        
    if "date_commande" in df.columns:
        
        df["date_commande"] = pd.to_datetime(
            df["date_commande"],
            errors="coerce",
            format="mixed"
        ).dt.strftime("%Y-%m-%d")

    nombre_lus = len(df)

    
    # ---------------------------------------------------------------------------
    # Normalisation des statuts
    # ---------------------------------------------------------------------------

    if "statut" in df.columns:

        df["statut"] = df["statut"].apply(normaliser_statut)

    # ---------------------------------------------------------------------------
    # Normalisation des modes de livraison
    # ---------------------------------------------------------------------------
    
    if "mode_livraison" in df.columns:
    
        df["mode_livraison"] = df["mode_livraison"].apply(normaliser_mode_livraison)

    
    
    # ---------------------------------------------------------------------------
    # Vérification des doublons
    # ---------------------------------------------------------------------------
        colonnes_doublon = [
        "id_commande",
        "id_client",
        "date_commande",
        "id_produit",
        "quantite",
        "prix_unitaire_applique",
        "statut",
        "mode_livraison",
        "motif_annulation"
        ]
        avant = len(df)

        df = df.drop_duplicates(
        subset=colonnes_doublon,
        keep="first"
        )

        apres = len(df)

    # ---------------------------------------------------------------------------
    # Vérification des données
    # ---------------------------------------------------------------------------

    colonnes_obligatoires = [
    "id_commande",
    "id_client",
    "date_commande",
    "id_produit",
    "quantite",
    "prix_unitaire_applique",
    "statut",
    "mode_livraison"
    ]

    df_rejetes = df[df[colonnes_obligatoires].isna().any(axis=1)]

    df = df.dropna(subset=colonnes_obligatoires)
    
    nombre_rejetes = len(df_rejetes)

    if nombre_rejetes > 0:

            logger.warning(
                "%d ligne(s) invalide(s)",
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
        "Lignes rejetées pour valeurs obligatoires manquantes: %d",
        nombre_rejetes
    )
    
    logger.info("Doublons supprimées : %d", avant - apres)
    logger.info("Nombre de lignes restantes : %d", apres)
    
    # ---------------------------------------------------------------------------
    # Connexion à SQLite
    # ---------------------------------------------------------------------------

    conn = sqlite3.connect(DATABASE_FILE)

    # ---------------------------------------------------------------------------
    # Chargement dans SQLite
    # ---------------------------------------------------------------------------

    df.to_sql(
        "clean_commandes",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    logger.info(
        "Chargement SQLite réussi : table clean_commandes (%d lignes)",
        len(df)
    )

    logger.info("===== Fin du chargement clean_commandes =====")

    print(
        f"Données enregistrées dans {DATABASE_FILE}"
    )


except Exception as e:

    logger.exception(
        "Erreur lors du chargement des commandes 2025 : %s",e
    )

    print(
        "Une erreur est survenue. Consultez le fichier de log :",
        LOG_FILE
    )