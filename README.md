# FraichExpress

## Cahier des charges proposé par la directrice de Fraich'Express

```txt
FraîchExpress vend des produits issus de producteurs partenaires. Un client passe des commandes, chaque commande contenant un ou plusieurs produits en certaines quantités. Les prix évoluent au cours de l'année : ce que paie le client doit rester celui du jour de la commande. Une commande est livrée à domicile, dans un point relais, ou retirée à la ferme. Certains produits peuvent provenir de plusieurs producteurs selon la saison. Nous voulons connaître, pour chaque commande, si elle a été livrée ou annulée, et pourquoi.
```

```mermaid
---
config:
    layout:elk
---
graph TD
    A[Client passe la commande] --> B{Collecte des articles et des quantités};

    subgraph Traitement de la commande
        B --> C{Validation produit/fournisseur};
        C --> D{Produits multiples producteurs ?};
        D -- Oui --> E[Déterminer la source/saisonnalité];
        D -- Non --> F[Vérification stock et disponibilité];
        E --> F;
        F --> G{Calcul du prix de vente};
        G --> H[Fixation du prix au jour de la commande];
    end

    H --> I{Méthode de livraison choisie};

    subgraph Traitement de l'expédition
        I -- Domicile --> J[Livraison à Domicile];
        I -- Point Relais --> K[Livraison en Point Relais];
        I -- Ferme --> L[Retrait à la Ferme];
    end

    J --> M(Commande Prête);
    K --> M;
    L --> M;

    M --> N{Statut Final de la Commande};
    
    N --> |Annulée| O{Motif d'annulation ?};
    O --> O1[Logique de motif _ex: Indisponibilité, Paiement échoué, etc._];
    O1 --> Z_Annule(Statut: Annulée);
    
    N --> |Livrée| P[Confirmation de livraison];
    P --> Z_Livree(Statut: Livrée);
```

## Règles de gestion

* 1 client commande 1 ou plusieurs produits en 1 ou plusieurs exemplaires à 1 date précise, qui conditionne le prix retenu pour la facturation

* 1 produit peut être fourni par 1 ou plusieurss producteurs en fonction de la saison

* 1 commande enregistre 1 ligne par client, par produit

* 1 commande ne peut exister que si le client existe dans clean_clients - CONTRAINTE

* la disponibilité des produits est conditionnée par les producteurs et la saisonnalité.

## Modélisations des données

### Dictionnaire de données 'métiers'

> Se préoccuper des surrogate_key à l'insertion des données

#### Table : ```clients```

| Nom de la colonne | Type de donnée |   Contraintes    |              Description              |
| :---------------: | :------------: | :--------------: | :-----------------------------------: |
|    uid_client     | INTEGER<br>AI  |   PRIMARY KEY    | Identifiant interne unique du client. |
|     id_client     |  VARCHAR(30)   | NOT NULL, UNIQUE |    Identifiant externe du client.     |
|        nom        |  VARCHAR(50)   |     NOT NULL     |       Nom de famille du client.       |
|      prenom       |  VARCHAR(30)   |     NOT NULL     |           Prénom du client.           |
|       email       |  VARCHAR(30)   |     NOT NULL     |       Adresse e-mail du client.       |
| date_inscription  |      DATE      |     NOT NULL     |     Date d'inscription du client.     |
|       ville       |  VARCHAR(30)   |     NOT NULL     |          Ville de résidence.          |
|    code_postal    |  VARCHAR(10)   |     NOT NULL     |       Code postal de résidence.       |

#### Table : ```produits```

| Nom de la colonne | Type de donnée |   Contraintes    |                      Description                       |
| :---------------: | :------------: | :--------------: | :----------------------------------------------------: |
|    uid_produit    |   INTEGER AI   |   PRIMARY KEY    |         Identifiant interne unique du produit.         |
|    id_produit     |    INTEGER     | NOT NULL, UNIQUE |         Identifiant externe unique du produit.         |
|      libelle      |  VARCHAR(50)   |     NOT NULL     |             Nom ou description du produit.             |
|     categorie     |  VARCHAR(50)   |     NOT NULL     |      Catégorie de produit (ex : Fruits, Légumes).      |
|       unite       |  VARCHAR(10)   |     NOT NULL     |           Unité de mesure (ex : kg, pièce).            |
|   prix_unitaire   |      REAL      |     NOT NULL     |                Prix standard par unité.                |
|      saison       |  VARCHAR(30)   |     NOT NULL     | Saison de pointe du produit (toute_annee, ete, hiver). |

#### Table : ```producteurs```

| Nom de la colonne | Type de donnée | Contraintes           | Description                               |
| :---------------- | :------------- | :-------------------- | :---------------------------------------- |
| uid_producteur    | INTEGER<br>AI  | PRIMARY KEY           | Identifiant interne unique du producteur. |
| id_producteur     | INTEGER        | NOT NULL, UNIQUE      | Identifiant externe unique du producteur. |
| nom               | VARCHAR(30)    | NOT NULL              | Nom du producteur.                        |
| commune           | VARCHAR(30)    | NOT NULL              | Commune/Municipalité du producteur.       |
| certification_bio | INTEGER        | NOT NULL, CHECK(0, 1) | Statut de certification bio (0 ou 1).     |
| date_adhesion     | DATE           | NOT NULL              | Date d'adhésion du producteur.            |

#### Table : ```commandes```

| Nom de la colonne | Type de donnée | Contraintes                     | Description                                                   |
| :---------------- | :------------- | :------------------------------ | :------------------------------------------------------------ |
| uid_commande      | INTEGER<br>AI  | PRIMARY KEY                     | Identifiant interne unique de la commande.                    |
| id_commande       | VARCHAR(10)    | NOT NULL, UNIQUE                | Identifiant externe unique de la commande.                    |
| date_commande     | DATE           | NOT NULL                        | Date de passation de la commande.                             |
| statut            | VARCHAR(30)    | NOT NULL                        | Statut actuel de la commande (Livrée, Annulée).               |
| mode_livraison    | VARCHAR(30)    | NOT NULL                        | Méthode de livraison (Domicile, Point relais, Retrait ferme). |
| id_client         | VARCHAR(30)    | FOREIGN KEY (clients.id_client) | Lien vers la table `clients`.                                 |

#### Table : ```annulations```

| Nom de la colonne  | Type de donnée | Contraintes                         | Description                                                |
| :----------------- | :------------- | :---------------------------------- | :--------------------------------------------------------- |
| uid_annulation     | INTEGER<br>AI  | PRIMARY KEY                         | Identifiant interne unique de l'annulation.                |
| id_annulation      | INTEGER        | NOT NULL                            | Identifiant externe de l'annulation.                       |
| motif_annulation   | VARCHAR(50)    | NULL                                | Motif de l'annulation.                                     |
| date_annulation    | DATE           | NOT NULL                            | Date de l'annulation.                                      |
| id_commande        | VARCHAR(10)    | FOREIGN KEY (commandes.id_commande) | Lien vers la commande annulée.                             |
| **Unique combiné** |                | UNIQUE(id_annulation, id_commande)  | Assure un enregistrement unique d'annulation par commande. |

#### Table : ```lignes_commande```

| Nom de la colonne | Type de donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| uid_ligne_commande | INTEGER | PRIMARY KEY | Identifiant unique interne de la ligne de commande. |
| id_produit | INTEGER | FOREIGN KEY (produits.id_produit) | Lien vers le produit commandé. |
| id_commande | VARCHAR(10) | FOREIGN KEY (commandes.id_commande) | Lien vers la commande contenant la ligne. |
| quantite_commandee | REAL | NOT NULL | Quantité commandée pour ce produit/commande. |
| prix_unitaire_applique | REAL | NOT NULL | Prix appliqué au moment de la commande. |
| **Unique Combiné** | | UNIQUE(id_produit, id_commande) | Empêche les entrées de produits en double par commande. |

#### Table : ```livraisons```

| Nom de la colonne | Type de donnée | Contraintes | Description |
| :--- | :--- | :--- | :--- |
| uid_livraison | INTEGER | PRIMARY KEY | Identifiant interne unique de la livraison. |
| id_produit | INTEGER | FOREIGN KEY (produits.id_produit) | Le produit livré. |
| id_producteur | INTEGER | FOREIGN KEY (producteurs.id_producteur) | Le producteur associé au produit livré. |
| date_livraison | DATE | NOT NULL | Date effective de la livraison. |
| quantite_livree | REAL | NOT NULL | Quantité livrée avec succès. |

### Dictionnaire de données 'datalake'

> Nous évitons la couche de stockage de données brutes. Nous conservons les fichiers sources d'origine inchangés. Nous pouvons donc les utiliser comme référence le moment voulu.

### Dictionnaire de données 'analytique'

