CREATE TABLE dim_client(
    uid_dim_client INTEGEREGER PRIMARY KEY,
    id_client VARCHAR(50) NOT NULL UNIQUE,
    ville VARCHAR(50),
    code_postal VARCHAR(50),
    date_inscription VARCHAR(50)
);

CREATE TABLE dim_date(
    uid_dim_temps INTEGER PRIMARY KEY,
    id_date INTEGER NOT NULL UNIQUE,
    annee VARCHAR(50),
    mois VARCHAR(50),
    jour VARCHAR(50),
    saison VARCHAR(50)
        CHECK (saison IN ("toute_annee","ete","hiver"))
);

CREATE TABLE dim_produit(
    uid_dim_produit INTEGER PRIMARY KEY,
    id_produit INTEGER NOT NULL UNIQUE,
    libelle VARCHAR(50),
    categorie VARCHAR(50)
        CHECK (saison IN ("Légumes","Fruits","Épicerie","Crèmerie","Boulangerie")),
    unite VARCHAR(50)
);

CREATE TABLE dim_producteur(
    uid_dim_producteur INTEGER PRIMARY KEY,
    id_producteur VARCHAR(50) NOT NULL UNIQUE,
    nom_producteur VARCHAR(50),
    certifie_bio INTEGER NOT NULL
        CHECK (certification_bio IN (0,1))
);

CREATE TABLE dim_livraison(
    uid_dim_livraison INTEGER PRIMARY KEY,
    id_livraison INTEGER NOT NULL UNIQUE,
    mode_livraison VARCHAR(30) NOT NULL,
    PRIMARY KEY(uid_dim_livraison),
    UNIQUE(id_livraison)
);

CREATE TABLE dim_meteo(
    uid_dim_meteo INTEGER PRIMARY KEY,
    id_meteo INTEGER NOT NULL UNIQUE,
    ville VARCHAR(50),
    temp_max REAL,
    pluie_mm DECIMAL(15,2)
);

CREATE TABLE dim_commande(
    uid_dim_commande INTEGER PRIMARY KEY,
    id_commande VARCHAR(30) NOT NULL UNIQUE,
    statut VARCHAR(30) NOT NULL
        CHECK (statut IN ("Livrée","Annulée")),
    mode_livraison VARCHAR(30) NOT NULL
        CHECK (mode_livraison IN ("Domicile","Point relais","Retrait ferme"))
);

CREATE TABLE faits_annulations(
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
        REFERENCES dim_date(uid_dim_temps),
    
    FOREIGN KEY(uid_dim_produit)
        REFERENCES dim_producteur(uid_dim_produit),
    
    FOREIGN KEY(uid_dim_livraison)
        REFERENCES dim_livraison(uid_dim_livraison)
);

CREATE TABLE faits_ventes(
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
        REFERENCES dim_date(uid_dim_temps),

    FOREIGN KEY(uid_dim_client)
        REFERENCES dim_client(uid_dim_client),

    FOREIGN KEY(uid_dim_livraison)
        REFERENCES dim_livraison(uid_dim_livraison)
);
