import pandas as pd
# on ajoute un bloc try/except pour gérer les erreurs potentielles lors de la lecture du fichier CSV
try:
    df = pd.read_csv("./data/commandes2025.csv", sep=";", encoding="latin-1")
    # 1. Une erreur dans le nom de fichier (underscore entre commandes et 2025 empêchait le script de trouver le fichier
    #
    # 2. Le séparateur dans le fichier CSV est un 'point virgule', or la fonction read_csv() utilise le séparateur 'virgule' par défaut.
    # Il était donc nécessaire de préciser le séparateur en paramètre de la fonction.
    #
    # 3. Le fichier CSV est encodé en latin-1.
    # Il était donc également indispensable de préciser l'encodage du fichier dans les paramètres de la fonction.
    print(df.shape)
    print(df["quantite"].sum())
except FileNotFoundError:
    print("Fichier non trouvé.")
except Exception as error:
    print(f"Une erreur s'est produite : {error}")