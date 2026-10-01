# -------------------------------------------------------------------------------
# ETL DE CHARGEMENT DE LA BASE ANALYTIQUE
#
# Source : données clean présentes dans SQLite
# Destination :
#   - DIM_CLIENT
#   - DIM_DATE
#   - DIM_PRODUIT
#   - DIM_PRODUCTEUR
#   - DIM_LIVRAISON
#   - DIM_METEO
#   - FAIT_VENTES
# -------------------------------------------------------------------------------

import pandas as pd
import sqlite3
import logging


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATABASE_FILE = "data/fraichexpress.db"
LOG_FILE = "load_base_analytique.log"


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
# Lecture des données clean
# -------------------------------------------------------------------------------

def charger_table(conn, nom_table):

    try:

        df = pd.read_sql_query(
            f"SELECT * FROM {nom_table}",
            conn
        )

        logger.info(
            "Lecture de %s réussie : %d lignes",
            nom_table,
            len(df)
        )

        return df

    except Exception as e:

        logger.error(
            "Erreur lors de la lecture de %s : %s",
            nom_table,
            e
        )

        raise


# -------------------------------------------------------------------------------
# Création DIM_CLIENT
# -------------------------------------------------------------------------------

def creer_dim_client(df_clients):

    dim_client = df_clients[
        [
            "id_client",
            "ville",
            "code_postal",
            "date_inscription"
        ]
    ].copy()

    dim_client = dim_client.drop_duplicates(
        subset=["id_client"]
    )

    return dim_client


# -------------------------------------------------------------------------------
# Création DIM_DATE
# -------------------------------------------------------------------------------

def creer_dim_date(df_commandes):

    dates = pd.to_datetime(
        df_commandes["date_commande"],
        errors="coerce"
    )

    dim_date = pd.DataFrame()

    dim_date["date"] = dates.dt.date

    dim_date = dim_date.drop_duplicates()

    dim_date = dim_date.dropna(
        subset=["date"]
    )

    dim_date["jour"] = pd.to_datetime(
        dim_date["date"]
    ).dt.day

    dim_date["mois"] = pd.to_datetime(
        dim_date["date"]
    ).dt.month

    dim_date["annee"] = pd.to_datetime(
        dim_date["date"]
    ).dt.year

    dim_date["saison"] = pd.to_datetime(
        dim_date["date"]
    ).dt.month.map({
        12: "Hiver",
        1: "Hiver",
        2: "Hiver",
        3: "Printemps",
        4: "Printemps",
        5: "Printemps",
        6: "Été",
        7: "Été",
        8: "Été",
        9: "Automne",
        10: "Automne",
        11: "Automne"
    })

    # Création de la clé id_date
    dim_date["id_date"] = (
        pd.to_datetime(dim_date["date"])
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dim_date = dim_date[
        [
            "id_date",
            "jour",
            "mois",
            "annee",
            "saison"
        ]
    ]

    return dim_date


# -------------------------------------------------------------------------------
# Création DIM_PRODUIT
# -------------------------------------------------------------------------------

def creer_dim_produit(df_produits):

    dim_produit = df_produits[
        [
            "id_produit",
            "libelle",
            "categorie",
            "unite"
        ]
    ].copy()

    dim_produit = dim_produit.drop_duplicates(
        subset=["id_produit"]
    )

    return dim_produit


# -------------------------------------------------------------------------------
# Création DIM_PRODUCTEUR
# -------------------------------------------------------------------------------

def creer_dim_producteur(df_producteurs):

    dim_producteur = df_producteurs[
        [
            "id_producteur",
            "nom",
            "certification_bio"
        ]
    ].copy()

    dim_producteur = dim_producteur.drop_duplicates(
        subset=["id_producteur"]
    )

    return dim_producteur


# -------------------------------------------------------------------------------
# Création DIM_LIVRAISON
# -------------------------------------------------------------------------------

def creer_dim_livraison(df_commandes):

    dim_livraison = df_commandes[
        [
            "mode_livraison"
        ]
    ].drop_duplicates().reset_index(drop=True)

    # Création d'un identifiant
    dim_livraison.insert(
        0,
        "id_livraison",
        range(1, len(dim_livraison) + 1)
    )

    return dim_livraison


# -------------------------------------------------------------------------------
# Création DIM_METEO
# -------------------------------------------------------------------------------

def creer_dim_meteo(df):
    dim = df.copy()

    dim["date"] = pd.to_datetime(
        dim["date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    dim["temp_max"] = pd.to_numeric(
        dim["temp_max"],
        errors="coerce"
    )

    dim["pluie_mm"] = pd.to_numeric(
        dim["pluie_mm"],
        errors="coerce"
    ).fillna(0)

    dim = dim.drop_duplicates(
        subset=["date", "ville"]
    ).reset_index(drop=True)

    dim["id_meteo"] = range(1, len(dim) + 1)

    dim = dim[
        [
            "id_meteo",
            "date",
            "ville",
            "temp_max",
            "pluie_mm"
        ]
    ]

    return dim


def creer_fait_ventes(
    df_commandes,
    df_clients,
    df_produits,
    dim_date,
    dim_livraison,
    dim_meteo
):

    fact = df_commandes.copy()

    # ---------------------------------------------------------------------------
    # Conversion de la date
    # ---------------------------------------------------------------------------

    fact["date_commande"] = pd.to_datetime(
        fact["date_commande"],
        errors="coerce"
    )

    # ---------------------------------------------------------------------------
    # Conversion des valeurs numériques
    # ---------------------------------------------------------------------------

    fact["quantite"] = pd.to_numeric(
        fact["quantite"],
        errors="coerce"
    )

    fact["prix_unitaire_applique"] = pd.to_numeric(
        fact["prix_unitaire_applique"]
        .astype(str)
        .str.replace(",", ".", regex=False),
        errors="coerce"
    )

    # ---------------------------------------------------------------------------
    # Calcul du montant de la vente
    # ---------------------------------------------------------------------------

    fact["montant_vente"] = (
        fact["quantite"]
        * fact["prix_unitaire_applique"]
    )

    # ---------------------------------------------------------------------------
    # Création de id_date
    # ---------------------------------------------------------------------------

    fact["id_date"] = (
        fact["date_commande"]
        .dt.strftime("%Y%m%d")
        .astype("Int64")
    )

    # ---------------------------------------------------------------------------
    # Récupération de id_producteur depuis clean_produits
    # ---------------------------------------------------------------------------

    produit_producteur = df_produits[
        [
            "id_produit",
            "id_producteur"
        ]
    ].drop_duplicates(
        subset=["id_produit"]
    )

    fact = fact.merge(
        produit_producteur,
        on="id_produit",
        how="left"
    )

    # ---------------------------------------------------------------------------
    # Récupération de la ville depuis clean_clients
    # ---------------------------------------------------------------------------

    client_ville = df_clients[
        [
            "id_client",
            "ville"
        ]
    ].drop_duplicates(
        subset=["id_client"]
    )

    fact = fact.merge(
        client_ville,
        on="id_client",
        how="left"
    )

    # ---------------------------------------------------------------------------
    # Jointure avec DIM_LIVRAISON
    # ---------------------------------------------------------------------------

    fact = fact.merge(
        dim_livraison[
            [
                "id_livraison",
                "mode_livraison"
            ]
        ],
        on="mode_livraison",
        how="left"
    )

    # ---------------------------------------------------------------------------
    # Préparation de la météo
    # ---------------------------------------------------------------------------

    meteo = dim_meteo.copy()

    meteo["date"] = pd.to_datetime(
        meteo["date"],
        errors="coerce"
    )

    fact["ville"] = (
        fact["ville"]
        .astype(str)
        .str.strip()
    )

    meteo["ville"] = (
        meteo["ville"]
        .astype(str)
        .str.strip()
    )

    # ---------------------------------------------------------------------------
    # Jointure météo : date + ville
    # ---------------------------------------------------------------------------

    fact = fact.merge(
        meteo[
            [
                "id_meteo",
                "date",
                "ville"
            ]
        ],
        left_on=[
            "date_commande",
            "ville"
        ],
        right_on=[
            "date",
            "ville"
        ],
        how="left"
    )

    # ---------------------------------------------------------------------------
    # Suppression des colonnes temporaires
    # ---------------------------------------------------------------------------

    fact = fact.drop(
        columns=[
            "date",
            "ville"
        ],
        errors="ignore"
    )

    # ---------------------------------------------------------------------------
    # Création de la clé de la table de faits
    # ---------------------------------------------------------------------------

    fact.insert(
        0,
        "id_fait_vente",
        range(1, len(fact) + 1)
    )

    # ---------------------------------------------------------------------------
    # Sélection des colonnes finales
    # ---------------------------------------------------------------------------

    colonnes = [
        "id_fait_vente",
        "quantite",
        "prix_unitaire_applique",
        "montant_vente",
        "statut",
        "id_client",
        "id_meteo",
        "id_producteur",
        "id_date",
        "id_produit",
        "id_livraison"
    ]

    fact = fact[colonnes]

    # ---------------------------------------------------------------------------
    # Renommage
    # ---------------------------------------------------------------------------

    fact = fact.rename(
        columns={
            "prix_unitaire_applique": "prix_unitaire"
        }
    )

    return fact

# -------------------------------------------------------------------------------
# PROGRAMME PRINCIPAL
# -------------------------------------------------------------------------------

try:

    logger.info(
        "===== Début ETL base analytique ====="
    )

    # ---------------------------------------------------------------------------
    # Connexion SQLite
    # ---------------------------------------------------------------------------

    conn = sqlite3.connect(
        DATABASE_FILE
    )

    # ---------------------------------------------------------------------------
    # Lecture des tables clean
    # ---------------------------------------------------------------------------

    df_commandes = charger_table(
        conn,
        "clean_commandes"
    )

    df_clients = charger_table(
        conn,
        "clean_clients"
    )

    df_produits = charger_table(
        conn,
        "clean_produits"
    )

    df_producteurs = charger_table(
        conn,
        "clean_producteurs"
    )

    df_meteo = charger_table(
        conn,
        "clean_meteo"
    )

    # ---------------------------------------------------------------------------
    # Création des dimensions
    # ---------------------------------------------------------------------------

    dim_client = creer_dim_client(
        df_clients
    )

    dim_date = creer_dim_date(
        df_commandes
    )

    dim_produit = creer_dim_produit(
        df_produits
    )

    dim_producteur = creer_dim_producteur(
        df_producteurs
    )

    dim_livraison = creer_dim_livraison(
        df_commandes
    )

    dim_meteo = creer_dim_meteo(
        df_meteo
    )

    logger.info(
        "Dimensions créées"
    )

    # ---------------------------------------------------------------------------
    # Création de la table de faits
    # ---------------------------------------------------------------------------

    fait_ventes = creer_fait_ventes(
    df_commandes,
    df_clients,
    df_produits,
    dim_date,
    dim_livraison,
    dim_meteo
)

    logger.info(
        "FAIT_VENTES créée : %d lignes",
        len(fait_ventes)
    )

    # ---------------------------------------------------------------------------
    # Chargement SQLite
    # ---------------------------------------------------------------------------

    dim_client.to_sql(
        "DIM_CLIENT",
        conn,
        if_exists="replace",
        index=False
    )

    dim_date.to_sql(
        "DIM_DATE",
        conn,
        if_exists="replace",
        index=False
    )

    dim_produit.to_sql(
        "DIM_PRODUIT",
        conn,
        if_exists="replace",
        index=False
    )

    dim_producteur.to_sql(
        "DIM_PRODUCTEUR",
        conn,
        if_exists="replace",
        index=False
    )

    dim_livraison.to_sql(
        "DIM_LIVRAISON",
        conn,
        if_exists="replace",
        index=False
    )

    dim_meteo.to_sql(
        "DIM_METEO",
        conn,
        if_exists="replace",
        index=False
    )

    fait_ventes.to_sql(
        "FAIT_VENTES",
        conn,
        if_exists="replace",
        index=False
    )

    # ---------------------------------------------------------------------------
    # Fermeture
    # ---------------------------------------------------------------------------

    conn.close()

    logger.info(
        "===== Fin ETL base analytique ====="
    )

    print(
        "Base analytique chargée avec succès."
    )

except Exception as e:

    logger.exception(
        "Erreur lors du chargement de la base analytique : %s",
        e
    )

    print(
        "Une erreur est survenue. Consultez le fichier de log :",
        LOG_FILE
    )