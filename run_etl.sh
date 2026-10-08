#!/usr/bin/env bash

# Arrêter le script dès qu'une commande échoue
set -e

# Définition des chemins
PROJECT_DIR="."
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/logs/etl_$(date +'%Y%m%d_%H%M%S').log"

# Création du dossier de logs si besoin
mkdir -p "$PROJECT_DIR/logs"

# Début du script
echo "=== Début du pipeline ETL : $(date) ==/=" | tee -w "$LOG_FILE"

# 1. Aller dans le dossier du projet
cd "$PROJECT_DIR" || { echo "Dossier introuvable : $PROJECT_DIR" >&2; exit 1; }

# 2. Activer l'environnement virtuel Python
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Environnement virtuel introuvable à : $VENV_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

# 3. Exécuter les scripts Python dans l'ordre (Extraction -> Transformation -> Chargement)
echo "Lancement de l'extraction..." | tee -a "$LOG_FILE"
python3 extract.py >> "$LOG_FILE" 2>&1

echo "Lancement de la transformation..." | tee -a "$LOG_FILE"
python3 transform.py >> "$LOG_FILE" 2>&1

echo "Lancement du chargement..." | tee -a "$LOG_FILE"
python3 load.py >> "$LOG_FILE" 2>&1

# 4. Désactiver l'environnement virtuel
deactivate

echo "=== Fin réussie du pipeline ETL : $(date) ==/=" | tee -a "$LOG_FILE"
