from pathlib import Path

# 1. Définir le chemin de la racine du projet
BASE_DIR = Path(__file__).resolve().parent

# 2. Définir les chemins vers les sources et stockages de données
DATA_DIR = BASE_DIR / "data"
SOURCES_DIR = DATA_DIR / "sources"

# 3. Définir les chemins vers les modules
ETL_DIR = BASE_DIR / "etl"
ML_DIR = BASE_DIR / "ml"

# . Définir les chemins vers les fichiers de journalisation (logs)
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
