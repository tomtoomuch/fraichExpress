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

* Se préoccuper des surrogate_key à l'insertion des données

## Règles de gestion

* 1 client commande 1 ou plusieurs produits en 1 ou plusieurs exemplaires à 1 date précise, qui conditionne le prix retenu pour la facturation

* 1 produit peut être fourni par 1 ou plusieurss producteurs en fonction de la saison

* 1 commande enregistre 1 ligne par client, par produit, par commande

* 1 commande ne peut exister que si le client existe dans clean_clients