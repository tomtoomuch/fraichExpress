import sqlite3
import pandas as pd
import numpy as np
from chemins import *
import logging
from datetime import datetime

DB_CIBLE = DATA_DIR / "entrepot_final.db"

LOG_FILE = "load_datalake.log"

CONNEXION_ENTREPOT = sqlite3.connect(DB_CIBLE, check_same_thread=False)

# Génération d"un horodatage pour le nom du fichier de journalisation
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = LOGS_DIR / f"{timestamp}_{LOG_FILE}"

# -------------------------------------------------------------------------------
# Configuration du logging
# -------------------------------------------------------------------------------

logging.basicConfig(
    filename=f"{LOG_FILE}",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)

# Création de la BDD et du schéma en étoile si elle n"existe pas déjà
def creation_datalake():
    cursor = CONNEXION_ENTREPOT.cursor()

    # Activation des clés étrangères pour la base finale
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Création des tables de Dimension et de Faits avec Clés Surrogate séquentielles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_client
    (
        uid_dim_client INTEGER PRIMARY KEY,
        id_client VARCHAR(50) NOT NULL UNIQUE,
        ville VARCHAR(50),
        code_postal VARCHAR(50),
        date_inscription VARCHAR(50)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_commande
    (
        uid_dim_commande INTEGER PRIMARY KEY,
        id_commande VARCHAR(30) NOT NULL,
        statut VARCHAR(30) NOT NULL
            CHECK (statut IN ("Livrée","Annulée")),
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_livraison
    (
        uid_dim_livraison INTEGER PRIMARY KEY,
        id_livraison INTEGER NOT NULL UNIQUE,
        mode_livraison VARCHAR(30) NOT NULL
            CHECK (mode_livraison IN ("Domicile","Point relais","Retrait ferme"))
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_meteo
    (
        uid_dim_meteo INTEGER PRIMARY KEY,
        id_meteo DATE NOT NULL,
        ville VARCHAR(50),
        temp_max REAL,
        pluie_mm REAL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_temps
    (
        uid_dim_temps INTEGER PRIMARY KEY,
        id_temps DATE NOT NULL,
        annee VARCHAR(50),
        mois VARCHAR(50),
        jour VARCHAR(50),
        saison VARCHAR(50)
            CHECK (saison IN ("toute_annee","ete","hiver"))
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_produit
    (
        uid_dim_produit INTEGER PRIMARY KEY,
        id_produit INTEGER NOT NULL UNIQUE,
        libelle VARCHAR(50),
        categorie VARCHAR(50)
            CHECK (categorie IN ("Légumes","Fruits","Épicerie","Crèmerie","Boulangerie")),
        unite VARCHAR(50)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_producteur
    (
        uid_dim_producteur INTEGER PRIMARY KEY,
        id_producteur INTEGER NOT NULL UNIQUE,
        nom_producteur VARCHAR(50),
        certifie_bio INTEGER NOT NULL
            CHECK (certifie_bio IN (0,1))
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faits_annulations
    (
        uid_fait_annulation INTEGER PRIMARY KEY,
        id_fait_annulation INTEGER NOT NULL UNIQUE,
        date_annulation DATE NOT NULL,
        motif_annulation VARCHAR(50) NOT NULL,
        montant_annulation REAL NOT NULL,
        quantite_annulee REAL NOT NULL,
        uid_dim_commande INTEGER NOT NULL,
        uid_dim_client INTEGER NOT NULL,
        uid_dim_meteo INTEGER NOT NULL,
        uid_dim_producteur INTEGER NOT NULL,
        uid_dim_temps INTEGER NOT NULL,
        uid_dim_produit INTEGER NOT NULL,
        uid_dim_livraison INTEGER NOT NULL,
        
        FOREIGN KEY(uid_dim_commande)
            REFERENCES dim_commande(uid_dim_commande),
        
        FOREIGN KEY(uid_dim_client)
            REFERENCES dim_client(uid_dim_client),
        
        FOREIGN KEY(uid_dim_meteo)
            REFERENCES dim_meteo(uid_dim_meteo),

        FOREIGN KEY(uid_dim_producteur)
            REFERENCES dim_producteur(uid_dim_producteur),
        
        FOREIGN KEY(uid_dim_temps)
            REFERENCES dim_temps(uid_dim_temps),
        
        FOREIGN KEY(uid_dim_produit)
            REFERENCES dim_producteur(uid_dim_produit),
        
        FOREIGN KEY(uid_dim_livraison)
            REFERENCES dim_livraison(uid_dim_livraison)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faits_ventes
    (
        uid_fait_vente INTEGER PRIMARY KEY,
        id_fait_vente INTEGER NOT NULL UNIQUE,
        quantite REAL NOT NULL,
        prix_unitaire REAL NOT NULL,
        montant_vente REAL NOT NULL,
        uid_dim_meteo INTEGER NOT NULL,
        uid_dim_commande INTEGER NOT NULL,
        uid_dim_producteur INTEGER NOT NULL,
        uid_dim_produit INTEGER NOT NULL,
        uid_dim_temps INTEGER NOT NULL,
        uid_dim_client INTEGER NOT NULL,
        uid_dim_livraison INTEGER NOT NULL,
        
        FOREIGN KEY(uid_dim_meteo)
            REFERENCES dim_meteo(uid_dim_meteo),

        FOREIGN KEY(uid_dim_commande)
            REFERENCES dim_commande(uid_dim_commande),

        FOREIGN KEY(uid_dim_producteur)
            REFERENCES dim_producteur(uid_dim_producteur),

        FOREIGN KEY(uid_dim_produit)
            REFERENCES dim_produit(uid_dim_produit),

        FOREIGN KEY(uid_dim_temps)
            REFERENCES dim_temps(uid_dim_temps),

        FOREIGN KEY(uid_dim_client)
            REFERENCES dim_client(uid_dim_client),

        FOREIGN KEY(uid_dim_livraison)
            REFERENCES dim_livraison(uid_dim_livraison)
    );
    """)
    CONNEXION_ENTREPOT.commit()
    logger.info("✔ Base de données cible et schéma en étoile initialisés.")

def extract():
    # ==========================================
    # 2. EXTRACTION (E)
    # ==========================================
    logger.info('PHASE DE L"EXTRACTION')

    # Source 1: Fichier JSON des clients
    df_clients_raw = pd.read_json(SOURCES_DIR / "clients.json")

    logger.info(f"Source 1 (JSON Clients) : {len(df_clients_raw)} lignes extraites.")

    # Source 2: Fichier CSV des commandes (délimiteur ";")
    df_commandes_raw = pd.read_csv(SOURCES_DIR / "commandes_2025.csv", sep=";", encoding="latin-1")

    logger.info(f"Source 2 (CSV Commandes) : {len(df_commandes_raw)} lignes extraites.")

    # Source 3: Fichier CSV de la météo (délimiteur ";")
    df_meteo_raw = pd.read_csv(SOURCES_DIR / "meteo.csv", sep=";")

    logger.info(f"Source 3 (CSV Météo) : {len(df_meteo_raw)} lignes extraites.")

    # Source 4: Base SQLite du catalogue
    conn_catalogue = sqlite3.connect(SOURCES_DIR / "source_catalogue.db")
    df_producteurs_raw = pd.read_sql("SELECT * FROM producteurs", conn_catalogue)
    df_produits_raw = pd.read_sql("SELECT * FROM produits", conn_catalogue)
    df_approvisionnement_raw = pd.read_sql("SELECT * FROM approvisionnement", conn_catalogue)
    conn_catalogue.close()

    logger.info("Source 4 (SQLite Catalogue) : Tables produits et producteurs extraites.")

    return df_clients_raw, df_commandes_raw, df_meteo_raw, df_producteurs_raw, df_produits_raw, df_approvisionnement_raw


def transform(df_clients_raw, df_commandes_raw, df_meteo_raw, df_producteurs_raw, df_produits_raw):
    # ==========================================
    # 3. TRANSFORMATION & NETTOYAGE (T)
    # ==========================================
    logger.info("\n--- 🛠 PHASE DE LA TRANSFORMATION ---")

    # --- A. Transformation DIM_CLIENT ---
    df_clients_clean = pd.DataFrame()
    df_clients_clean = df_clients_raw.copy()
    df_clients_clean["id_client"] = df_clients_clean["id_client"].str.strip().upper()
    df_clients_clean["ville"] = df_clients_clean["adresse"].apply(lambda x: x.get("ville", "").strip().upper() if isinstance(x, dict) else "")
    df_clients_clean["code_postal"] = df_clients_clean["adresse"].apply(lambda x: str(x.get("code_postal", "")).strip() if isinstance(x, dict) else "")

    # Normalisation des formats de dates hétérogènes (YYYY-MM-DD et DD/MM/YYYY)
    df_clients_clean["date_inscription"] = pd.to_datetime(df_clients_raw["date_inscription"], format="mixed").dt.strftime("%Y-%m-%d")

    # Suppression des doublons naturels
    df_clients_clean = df_clients_clean.drop_duplicates(subset=["id_client"])
    logger.info("✔ Dimension Clients nettoyée et normalisée.")

    # --- D. Transformation DIM_COMMANDE ---
    df_commandes_clean = pd.DataFrame()
    df_commandes_clean = df_commandes_raw.copy()
    df_commandes_clean["date_commande"] = pd.to_datetime(df_commandes_clean["date_commande"], format="mixed").dt.strftime("%Y-%m-%d")
    df_commandes_clean["quantite"] = df_commandes_clean["quantite"].str.replace(",", ".").astype(float)
    df_commandes_clean["prix_unitaire_applique"] = df_commandes_clean["prix_unitaire_applique"].str.replace(",", ".").astype(float)

    # Nettoyage des chaînes textuelles
    df_commandes_clean["statut"] = df_commandes_clean["statut"].str.strip().str.capitalize()
    df_commandes_clean["mode_livraison"] = df_commandes_clean["mode_livraison"].str.strip().str.capitalize()
    df_commandes_clean["id_client"] = df_commandes_clean["id_client"].str.strip().upper()
    ids_produits = pd.to_numeric(
        df_commandes_clean["id_produit"],
        errors="coerce"
        )
    ids_produits = ids_produits.replace([np.inf, -np.inf], np.nan)
    df_commandes_clean["id_produit"] = ids_produits.astype("Int64")

    # Élimination des lignes sans quantité valide (ex: les "N/A" présents dans vos sources)
    df_commandes_clean = df_commandes_clean.dropna(subset=["quantite", "prix_unitaire_applique"])

    # --- Transformation DIM_LIVRAISON ---
    df_livraisons_clean = pd.DataFrame()
    df_livraisons_clean["id_livraison"]



    # --- B. Transformation DIM_PRODUIT ---
    # Correction de l"encodage brisé (Ex: "Ã‰picerie" -> "Épicerie")
    df_catalogue_merged = pd.merge(df_produits_raw, df_producteurs_raw, on="id_producteur", how="left")

    df_produits_clean = pd.DataFrame()
    df_produits_clean["id_produit"] = df_catalogue_merged["id_produit"]
    df_produits_clean["libelle"] = df_catalogue_merged["libelle"].str.encode("utf-8", errors="ignore").str.decode("utf-8", errors="ignore")
    df_produits_clean["categorie"] = df_catalogue_merged["categorie"].str.encode("utf-8", errors="ignore").str.decode("utf-8", errors="ignore").str.capitalize()
    df_produits_clean["unite"] = df_catalogue_merged["unite"].str.encode("utf-8", errors="ignore").str.decode("utf-8", errors="ignore")
    df_produits_clean["prix_unitaire_catalogue"] = df_catalogue_merged["prix_unitaire"]
    df_produits_clean["nom_producteur"] = df_catalogue_merged["nom"].str.encode("utf-8", errors="ignore").str.decode("utf-8", errors="ignore")
    df_produits_clean["commune_producteur"] = df_catalogue_merged["commune"].str.encode("utf-8", errors="ignore").str.decode("utf-8", errors="ignore")
    df_produits_clean["certification_bio_producteur"] = df_catalogue_merged["certification_bio"]

    df_produits_clean = df_produits_clean.drop_duplicates(subset=["id_produit"])
    logger.info("✔ Dimension Produits nettoyée (encodages UTF-8 réparés).")

    # --- C. Transformation DIM_METEO ---
    df_meteo_clean = pd.DataFrame()
    df_meteo_clean["date_meteo"] = pd.to_datetime(df_meteo_raw["date"], format="mixed").dt.strftime("%Y-%m-%d")
    df_meteo_clean["ville"] = df_meteo_raw["ville"].str.strip().str.upper()

    # Remplacement des virgules par des points pour les décimaux et nettoyage des valeurs aberrantes (-999)
    df_meteo_clean["temp_max"] = df_meteo_raw["temp_max"].str.replace(",", ".").astype(float)
    df_meteo_clean["temp_max"] = df_meteo_clean["temp_max"].replace(-999, np.nan) 
    df_meteo_clean["pluie_mm"] = df_meteo_raw["pluie_mm"].str.replace(",", ".").astype(float)

    # Gestion des valeurs manquantes (imputation par la moyenne de la ville)
    df_meteo_clean["temp_max"] = df_meteo_clean.groupby("ville")["temp_max"].transform(lambda x: x.fillna(x.mean()))
    df_meteo_clean["pluie_mm"] = df_meteo_clean["pluie_mm"].fillna(0.0) # S"il ne pleut pas, on met 0

    df_meteo_clean = df_meteo_clean.dropna(subset=["date_meteo", "ville"]).drop_duplicates(subset=["date_meteo", "ville"])
    logger.info("✔ Dimension Météo nettoyée (valeurs aberrantes -999 supprimées et imputées).")


    # --- D. Transformation FAIT_COMMANDE ---
    df_commandes_clean = pd.DataFrame()
    df_commandes_clean = df_commandes_raw.copy()
    df_commandes_clean["date_commande"] = pd.to_datetime(df_commandes_clean["date_commande"], format="mixed").dt.strftime("%Y-%m-%d")
    df_commandes_clean["quantite"] = df_commandes_clean["quantite"].str.replace(",", ".").astype(float)
    df_commandes_clean["prix_unitaire_applique"] = df_commandes_clean["prix_unitaire_applique"].str.replace(",", ".").astype(float)

    # Nettoyage des chaînes textuelles
    df_commandes_clean["statut"] = df_commandes_clean["statut"].str.strip().str.capitalize()
    df_commandes_clean["mode_livraison"] = df_commandes_clean["mode_livraison"].str.strip().str.lower()
    df_commandes_clean["id_client"] = df_commandes_clean["id_client"].str.strip()
    ids_produits = pd.to_numeric(
        df_commandes_clean["id_produit"],
        errors="coerce"
        )
    ids_produits = ids_produits.replace([np.inf, -np.inf], np.nan)
    df_commandes_clean["id_produit"] = ids_produits.astype("Int64")

    # Élimination des lignes sans quantité valide (ex: les "N/A" présents dans vos sources)
    df_commandes_clean = df_commandes_clean.dropna(subset=["quantite", "prix_unitaire_applique"])

    return df_clients_clean, df_produits_clean, df_meteo_clean, df_commandes_clean


def load(df_clients_clean, df_produits_clean, df_meteo_clean, df_commandes_clean):
    # ==========================================
    # 4. CHARGEMENT & ET MAPPING DES CLÉS SURROGATE (L)
    # ==========================================
    logger.info("\n--- 💾 PHASE DU CHARGEMENT (Génération Clés Surrogate) ---")

    # Étape 1 : Insertion des dimensions pour générer les clés surrogate auto-incrémentées dans SQLite
    #df_clients_clean.to_sql("dim_client", conn_entrepot, if_exists="append", index=False)
    upsert_dimension("dim_client", df_clients_clean)
    upsert_dimension("dim_produit", df_produits_clean)
    upsert_dimension("dim_meteo", df_meteo_clean)
    
    # Étape 2 : Récupération des tables de correspondance (Clé Naturelle <-> Clé Surrogate) fraîchement créées
    map_clients = pd.read_sql("SELECT uid_dim_client, id_client FROM dim_client", CONNEXION_ENTREPOT)
    map_produits = pd.read_sql("SELECT uid_dim_produit, id_produit FROM dim_produit", CONNEXION_ENTREPOT)
    map_meteo = pd.read_sql("SELECT uid_dim_meteo, date_meteo, ville FROM dim_meteo", CONNEXION_ENTREPOT)

    # Étape 3 : Mapping des clés surrogate sur la table de faits
    # Jointure Client
    df_faits = pd.merge(df_commandes_clean, map_clients, on="id_client", how="inner")

    # Jointure Produit
    df_faits = pd.merge(df_faits, map_produits, on="id_produit", how="inner")

    df_client_villes = df_clients_clean[["id_client", "ville"]]
    df_faits = pd.merge(df_faits, df_client_villes, on="id_client", how="left")
    # Jointure Météo (basée sur Date de commande et Ville du client)
    df_faits = pd.merge(df_faits, map_meteo, left_on=["date_commande", "ville"], right_on=["date_meteo", "ville"], how="left")

    # Étape 4 : Sélection et ordonnancement final des colonnes pour la table de faits
    df_faits_final = df_faits[["id_commande", "uid_dim_client", "uid_dim_produit", "uid_dim_meteo","date_commande", "quantite", "prix_unitaire_applique","statut", "mode_livraison", "motif_annulation"]]

    # Insertion de la table de faits
    upsert_dimension("dim_commande", df_faits_final)

    logger.info("✔ Table de Faits "fait_commande" alimentée avec succès avec toutes les Clés Surrogate.")

    # --- VERIFICATION ---
    logger.info("\n--- 🔍 APERÇU RAPIDE DE LA TABLE DE FAITS CRÉÉE ---")
    df_verif = pd.read_sql("SELECT * FROM dim_commande LIMIT 5", CONNEXION_ENTREPOT)
    logger.info(df_verif.to_string())

    logger.info("\n🎉 Processus ETL terminé. Le fichier "entrepot_final.db" est prêt pour l"analyse analytique.")


# Fonction qui permet de vérifier l"existence d"une clé naturelle dans la table
# et de mettre à jour plutôt que d"insérer une nouvelle ligne si la clé existe déjà.
def upsert_dimension(table_name, df):
    
    cursor = CONNEXION_ENTREPOT.cursor()
    # Définir les colonnes à insérer ou mettre à jour
    columns_to_insert = list(df.columns)

    # Nettoyage des noms de colonnes pour le SQL
    columns_sql = ", ".join(column.replace(" ", "_").replace("-", "_") for column in columns_to_insert)
    placeholders = []
    for i in range(len(columns_to_insert)):
        placeholders.append("?")
            
    placeholders = ", ".join(placeholders)
    print(placeholders)

    # Exécution de l"upsert
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        requete = f"""
            INSERT OR REPLACE INTO
                {table_name} (
                    {columns_sql}
                ) 
                VALUES (
                    {placeholders}
                )
        """

        data_to_insert = [tuple(row) for row in df[columns_to_insert].values]
        cursor.executemany(requete, data_to_insert)
        print(f"Upsert effectué pour la table {table_name} : {len(data_to_insert)} lignes traitées.")
    except Exception as e:
        print(f"Erreur lors de l"upsert pour la table {table_name} : {e}")
      

def main():

    creation_datalake()

    df_clients_raw, df_commandes_raw, df_meteo_raw, df_producteurs_raw, df_produits_raw = extract()

    df_clients_clean, df_produits_clean, df_meteo_clean, df_commandes_clean = transform(df_clients_raw, df_commandes_raw, df_meteo_raw, df_producteurs_raw, df_produits_raw)

    load(df_clients_clean, df_produits_clean, df_meteo_clean, df_commandes_clean)


if (__name__) == "__main__":
    main()