import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema
from pandera.engines import pandas_engine
from sqlalchemy import create_engine

# Définition du schéma dim_client
schema_dim_client = DataFrameSchema(
    columns={
        "id_client": Column(str, Check.str_startswith("C"), unique=True),
        "ville": Column(str),
        "code_postal": Column(str, Check.str_length(5)),
        "date_inscription": Column(pandas_engine.Date())
    },
    coerce=True,
    strict=True,
)

# Définition du schéma dim_commande
schema_dim_commande = DataFrameSchema(
    columns={
        "id_commande": Column(str, Check.str_startswith("CMD")),
        "statut": Column(str, Check.isin("Livrée","Annulée"))
    },
    coerce=True,
    strict=True,
)

# Définition du schéma dim_livraison
schema_dim_livraison = DataFrameSchema(
    columns={
        "id_livraison": Column(int, unique=True),
        "mode_livraison": Column(str, Check.isin("Domicile","Point relais","Retrait ferme"))
    },
    coerce=True,
    strict=True,
)

# Définition du schéma dim_meteo
schema_dim_meteo = DataFrameSchema(
    columns={
        "id_meteo": Column(int, unique=True), # N'est-il pass pertinent de stocker une date
        "ville": Column(str),
        "temp_max": Column(float),
        "pluie_mm": Column(float)
    },
    coerce=True,
    strict=True,
)

# Définition du schéma dim_temps
schema_dim_temps = DataFrameSchema(
    columns={
        "id_temps": Column(int, nullable=False, unique=True),
        "annee": Column(int),
        "mois": Column(int),
        "jour": Column(int),
        "saison": Column(str, Check.isin("toute_anne","ete","hiver"))
    },
    coerce=True,
    strict=True,
)

# Définition du schéma dim_produit
schema_dim_produit = DataFrameSchema(
    columns={
        "id_produit": Column(int, nullable=False, unique=True),
        "libelle": Column(str),
        "categorie": Column(str),
        "unite": Column(str),
    },
    coerce=True,
    strict=True,
)

# Définition du schéma dim_producteur
schema_dim_producteur = DataFrameSchema(
    columns={
        "id_producteur": Column(int, nullable=False, unique=True),
        "nom_producteur": Column(str),
        "certifie_bio": Column(int, Check.in_range(0, 1)),
    },
    coerce=True,
    strict=True,
)


# Définition du schéma de la table des faits de ventes
schema_faits_ventes = DataFrameSchema(
    columns={
    "uid_fait_vente": Column(int, pa.Field(ge=0), unique=True),  # PRIMARY KEY
    "id_fait_vente": Column(int, pa.Field(ge=0), unique=True),  # UNIQUE
    "quantite": Column(float, pa.Field(ge=0)),
    "prix_unitaire": Column(float, pa.Field(ge=0)),
    "montant_vente": Column(float, pa.Field(ge=0)),
    "uid_dim_meteo": Column(int, pa.Field(ge=0)),
    "uid_dim_commande": Column(int, pa.Field(ge=0)),
    "uid_dim_producteur": Column(int, pa.Field(ge=0)),
    "uid_dim_produit": Column(int, pa.Field(ge=0)),
    "uid_dim_temps": Column(int, pa.Field(ge=0)),
    "uid_dim_client": Column(int, pa.Field(ge=0)),
    "uid_dim_livraison": Column(int, pa.Field(ge=0)),
    },
    strict = True,
    coerce = True,
)

# Définition du schéma de la table des faits d'annulations
schema_faits_annulations = DataFrameSchema(
    columns={
    "uid_fait_annulation": Column(int, pa.Field(ge=0), unique=True),  # PRIMARY KEY
    "id_fait_annulation": Column(int, pa.Field(ge=0), unique=True),  # UNIQUE
    "date_annulation": Column(pandas_engine.Date()),
    "motif_annulation": Column(str),
    "montant_annulation": Column(float, pa.Field(ge=0)),
    "quantite_annulee": Column(float, pa.Field(ge=0)),
    "uid_dim_meteo": Column(int, pa.Field(ge=0)),
    "uid_dim_commande": Column(int, pa.Field(ge=0)),
    "uid_dim_producteur": Column(int, pa.Field(ge=0)),
    "uid_dim_produit": Column(int, pa.Field(ge=0)),
    "uid_dim_temps": Column(int, pa.Field(ge=0)),
    "uid_dim_client": Column(int, pa.Field(ge=0)),
    "uid_dim_livraison": Column(int, pa.Field(ge=0)),
    },
    strict = True,
    coerce = True,
)




