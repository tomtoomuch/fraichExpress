# Le script chargement_produits.py se connecte à la base de données source_catalogue.db,
# récupère les données, les normalise et les prépare pour l'insertion dans la base de données
# fraichexpress.db
# Importation des moduules nécessaires
from pathlib import Path
import pandas as pd
import sqlite3 as sqlite
import logging
from datetime import datetime

# Déclaration des variables globales
RACINE = Path("./")
DOSSIER_SOURCES = Path("./data/sources/")
DOSSIER_DONNEES = Path("./data/")
CHEMIN_BDD_SOURCE = ""
CHEMIN_BDD_DEST = ""
LOG_FILE = "load_sqlite_data.log"

# Génération d'un horodatage pour le nom du fichier de journalisation
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Initialisation de la journalisation
logging.basicConfig(
    filename=f"{timestamp}_{LOG_FILE}",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


def charger_sqlite():

    logger.info("===== Chargement des données SQLite démarré =====")

    # Initialisation des variables pour le stockage des dataframe retournés
    donnees_approvisionnement = None
    donnees_producteurs = None
    donnees_produits = None

    # Recherche du fichier "source_catalogue.db"
    for chemin in DOSSIER_SOURCES.rglob("source_catalogue.db"):
        # Stockage du chemin trouvé dans une globale
        CHEMIN_BDD_SOURCE = chemin

        try:
            # Stockage de l'uri de la BDD en incluant le paramètre
            # garantissant d'accéder aux données en lecture seule
            uri = f"file:{CHEMIN_BDD_SOURCE}?mode=ro"

            # Connexion à la base de données source_catalogue.db
            connexion = sqlite.connect(uri, uri=True)

            logger.info(
                f"Connexion à la base de données {CHEMIN_BDD_SOURCE} établie..."
                )

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
            #print("Les requêtes sont prêtese à être exécutées.")

            # On charge chacune des tables dans un dataframe
            for requete in requetes:
                #print(f"{requete["code"]} : {requete["req"]}")
                df = pd.read_sql_query(requete["req"], connexion)

                volume_lu = len(df)
                logger.info(f"La récupération des données de la table {requete["code"]} est terminée.")
                logger.info(f"{volume_lu} enregistrements ont été lus :")

                # Vérification des doublons dans le dataframe récupéré
                doublons = df.duplicated()
                nombre_doublons = doublons.sum()

                if nombre_doublons == 0:
                    
                    logger.info("- Auncun doublon n'a été détecté.")

                else:

                    logger.warning(
                        f"- {nombre_doublons} doublon(s) détecté(s)."
                    )

                    # Suppression des doublons dans la table traitée
                    df = df.drop_duplicates()

                    logger.info(
                        f"- {nombre_doublons} doublon(s) supprimé(s)."
                    )

                # Vérification de l'intégrité des données

                # Contrôle des valeurs manquantes
                valeurs_manquantes = df.isna().sum()

                logger.info(
                    f"- Valeurs manquantes :\n"
                    f"{valeurs_manquantes}"
                )

                # Identification des enregistrements rejetés
                # toute ligne qui contieent une valeur manquante
                masque_rejets = df.isna().any(axis=1)

                nombre_rejets = masque_rejets.sum()

                nombre_acceptes = len(df) - nombre_rejets


                if nombre_rejets > 0:

                    logger.warning(
                        f"{nombre_rejets} enregistrement(s) invalide(s)"
                    )

                    rejets = df.loc[masque_rejets]

                    logger.warning(
                        f"Enregistrements rejeté(s) :\n {rejets}"
                    )

                logger.info(
                        f"Volume lu :\n {volume_lu}"
                    )
                
                logger.info(
                    f"Volume accepté :\n {nombre_acceptes}"
                )
            
                logger.info(
                    f"Volume rejeté :\n {nombre_rejets}"
                )

                logger.info(
                    f"Volume après dédoublonnage :\n {len(df)}"
                )

                resultats[requete["code"]] = df
                logger.info(f"Requête terminée. Les données de la table '{requete["code"]}' ont été récupérées.")

            # Fermeture de la connexion à la bdd après récupértion des données
            connexion.close()
            
            # Peuplement de 3 DataFrame avec les données des 3 tables
            donnees_approvisionnement = pd.DataFrame(resultats["approvisionnement"])
            donnees_producteurs = pd.DataFrame(resultats["producteurs"])
            donnees_produits = pd.DataFrame(resultats["produits"])

        except FileNotFoundError:
            logger.error(
                "Fichier introuvable : %s",
                CHEMIN_BDD_SOURCE
            )
            raise

        except sqlite.Error as error:
            # Journalisation de l'erreur - traceback complet
            logger.error(
                f"Erreur de la connexion à la base de données SQLITE : {error}"
            )
            raise RuntimeError(
                f"Impossible de se connecter à la base SQLite : '{CHEMIN_BDD_SOURCE}'"
                ) from error

    logger.info(f"Récupération des données SQLite terminée.")

    # Retour des 3 dataframes
    return donnees_approvisionnement,donnees_producteurs,donnees_produits


def stocker_sqlite(
    donnees_approvisionnement,
    donnees_producteurs,
    donnees_produits
):

    # Recherche du fichier "source_catalogue.db"
    for chemin in DOSSIER_DONNEES.rglob("fraichexpress.db"):
        # Stockage du chemin trouvé dans une globale
        CHEMIN_BDD_DEST = chemin

        try:
            # Stockage de l'uri de la BDD en incluant le paramètre
            # garantissant d'accéder aux données en lecture seule
            uri = f"file:{CHEMIN_BDD_DEST}"

            # Connexion à la base de données source_catalogue.db
            connexion = sqlite.connect(uri, uri=True)

            logger.info(
                f"Connexion à la base de données {CHEMIN_BDD_DEST} établie..."
                )

            donnees_approvisionnement.to_sql(
                "clean_approvisionnement",
                connexion,
                if_exists="replace",
                index=False
            )

            donnees_producteurs.to_sql(
                "clean_producteurs",
                connexion,
                if_exists="replace",
                index=False
            )

            donnees_produits.to_sql(
                "clean_produits",
                connexion,
                if_exists="replace",
                index=False
            )

            connexion.close()

            logger.info(f"Téléversement des données des tables 'clean_approvisionnement', 'clean_producteurs' et 'clean_produits' dans la base SQLite {CHEMIN_BDD_DEST}")
            print(f"Données enregistréeés dans {CHEMIN_BDD_DEST}")

        except FileNotFoundError:
            logger.error(
                "Fichier introuvable : %s",
                CHEMIN_BDD_SOURCE
            )
            raise

        except sqlite.Error as error:
            # Journalisation de l'erreur - traceback complet
            logger.error(
                f"Erreur de la connexion à la base de données SQLITE : {error}"
            )
            raise RuntimeError(
                f"Impossible de se connecter à la base SQLite : '{CHEMIN_BDD_SOURCE}'"
                ) from error

## POINT D'ENTREE SI EXECUTE EN CLI DEPUIS LE TERMINAL
if __name__ == "__main__":
    donnees_approvisionnement, donnees_producteurs, donnees_produits = charger_sqlite()
    stocker_sqlite(donnees_approvisionnement, donnees_producteurs, donnees_produits)