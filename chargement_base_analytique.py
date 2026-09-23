# CREATE TABLE DIM_CLIENT(
#    id_client INT,
#    ville VARCHAR(50),
#    code_postal VARCHAR(50),
#    date_inscription VARCHAR(50),
#    PRIMARY KEY(id_client)
# );

# CREATE TABLE DIM_DATE(
#    id_date INT,
#    jour VARCHAR(50),
#    mois VARCHAR(50),
#    annee VARCHAR(50),
#    saison VARCHAR(50),
#    PRIMARY KEY(id_date)
# );

# CREATE TABLE DIM_PRODUIT(
#    id_produit INT,
#    libelle VARCHAR(50),
#    categorie VARCHAR(50),
#    unite VARCHAR(50),
#    PRIMARY KEY(id_produit)
# );

# CREATE TABLE DIM_PRODUCTEUR(
#    id_producteur VARCHAR(50),
#    nom_producteur VARCHAR(50),
#    certifie_bio VARCHAR(50),
#    PRIMARY KEY(id_producteur)
# );

# CREATE TABLE DIM_LIVRAISON(
#    id_livraison VARCHAR(50),
#    mode_livraison VARCHAR(50),
#    PRIMARY KEY(id_livraison)
# );

# CREATE TABLE DIM_METEO(
#    id_meteo INT,
#    ville VARCHAR(50),
#    temp_max DOUBLE,
#    pluie_mm DECIMAL(15,2),
#    PRIMARY KEY(id_meteo)
# );

# CREATE TABLE FAIT_VENTES(
#    id_fait_vente INT,
#    quantite VARCHAR(50),
#    prix_unitaire VARCHAR(50),
#    montant_vente VARCHAR(50),
#    statut VARCHAR(50),
#    id_client INT NOT NULL,
#    id_meteo INT NOT NULL,
#    id_producteur VARCHAR(50) NOT NULL,
#    id_date INT NOT NULL,
#    id_produit INT NOT NULL,
#    id_livraison VARCHAR(50) NOT NULL,
#    PRIMARY KEY(id_fait_vente),
#    FOREIGN KEY(id_client) REFERENCES DIM_CLIENT(id_client),
#    FOREIGN KEY(id_meteo) REFERENCES DIM_METEO(id_meteo),
#    FOREIGN KEY(id_producteur) REFERENCES DIM_PRODUCTEUR(id_producteur),
#    FOREIGN KEY(id_date) REFERENCES DIM_DATE(id_date),
#    FOREIGN KEY(id_produit) REFERENCES DIM_PRODUIT(id_produit),
#    FOREIGN KEY(id_livraison) REFERENCES DIM_LIVRAISON(id_livraison)
# );
