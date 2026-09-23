CREATE TABLE clean_clients(
   uid_client INTEGER PRIMARY KEY,
   id_client VARCHAR(30) NOT NULL UNIQUE,
   nom VARCHAR(50) NOT NULL,
   prenom VARCHAR(30) NOT NULL,
   email VARCHAR(30) NOT NULL,
   date_inscription DATE NOT NULL,
   ville VARCHAR(30) NOT NULL,
   code_postal VARCHAR(10) NOT NULL
);

CREATE TABLE clean_produits(
   uid_produit INTEGER PRIMARY KEY,
   id_produit INTEGER NOT NULL UNIQUE,
   libelle VARCHAR(50) NOT NULL,
   categorie VARCHAR(50) NOT NULL
      CHECK,
   unite VARCHAR(10) NOT NULL,
   prix_unitaire REAL NOT NULL,
   saison VARCHAR(30) NOT NULL
      CHECK (saison IN ("toute_annee","ete","hiver"))
);

CREATE TABLE clean_producteurs(
   uid_producteur INTEGER PRIMARY KEY,
   id_producteur INTEGER NOT NULL UNIQUE,
   nom VARCHAR(30) NOT NULL,
   commune VARCHAR(30) NOT NULL,
   certification_bio INTEGER NOT NULL
      CHECK (certification_bio IN (0,1)),
   date_adhesion DATE NOT NULL
);

CREATE TABLE clean_commandes(
   uid_commande INTEGER PRIMARY KEY,
   id_commande VARCHAR(10) NOT NULL UNIQUE,
   date_commande DATE NOT NULL
      CHECK (strftime("%Y", date_commande) = "2025"),
   statut VARCHAR(30) NOT NULL
      CHECK (statut IN ("Livrée","Annulée")),
   mode_livraison VARCHAR(30) NOT NULL
      CHECK (mode_livraison IN ("Domicile","Point relais","Retrait ferme")),
   id_client VARCHAR(30) NOT NULL,
   
   FOREIGN KEY(id_client)
      REFERENCES clients(id_client)
);

CREATE TABLE clean_annulations(
   uid_annulation INTEGER PRIMARY KEY,
   id_annulation INTEGER NOT NULL,
   motif_annulation VARCHAR(50),
   date_annulation DATE NOT NULL,
   id_commande VARCHAR(10) NOT NULL,

   UNIQUE(id_annulation,id_commande),

   FOREIGN KEY(id_commande)
      REFERENCES commandes(id_commande)
);

CREATE TABLE clean_lignes_commande(
   uid_ligne_commande INTEGER PRIMARY KEY,
   id_produit INTEGER NOT NULL,
   id_commande VARCHAR(10) NOT NULL,
   quantite_commandee REAL NOT NULL,
   prix_unitaire_applique REAL NOT NULL,

   UNIQUE(id_produit, id_commande),

   FOREIGN KEY(id_produit)
      REFERENCES produits(id_produit),
   
   FOREIGN KEY(id_commande)
      REFERENCES commandes(id_commande)
);

CREATE TABLE clean_livraisons(
   uid_livraison INTEGER PRIMARY KEY,
   id_produit INTEGER NOT NULL,
   id_producteur INTEGER NOT NULL,
   date_livraison DATE NOT NULL,
   quantite_livree REAL NOT NULL,

   FOREIGN KEY(id_produit)
      REFERENCES produits(id_produit),
   
   FOREIGN KEY(id_producteur)
      REFERENCES producteurs(id_producteur)
);
