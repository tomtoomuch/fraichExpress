FraîchExpress est une coopérative de 8 producteurs locaux (Hérault, Gard, Aveyron) qui livre des paniers de produits frais à ses clients : à domicile, en point relais ou par retrait à la ferme.
Après deux ans de croissance, la directrice, Camille Roussel, a un constat simple : « Personne ne fait confiance aux chiffres. » Les données sont dispersées entre un export de commandes, un fichier clients, un catalogue produits et un relevé météo. Chaque service en tire des totaux différents.
Elle vous confie, en tant que prestataires Data, une mission de deux jours avec trois objectifs :
Fiabiliser les données (ETL) ;
Structurer un entrepôt décisionnel pour répondre à ses questions (modélisation + SQL) ;
Anticiper les commandes qui seront annulées avant livraison (machine learning), et lui remettre une note de veille sur les technologies qui pourraient faire évoluer son dispositif.


Référentiels

    [2023] Certification RNCP Développeur.se en intelligence artificielle
    Compétences transversales

Ressources

    fraichexpress_sources.zip

Contexte du projet

    Règle du jeu. Les données fournies sont réelles au sens où elles sont imparfaites. Personne ne vous dira où sont les problèmes : les trouver, les documenter et décider quoi en faire fait partie de la mission.

Seul ou en binôme
Données fournies

commandes_2025.csv Une ligne par produit commandé, année 2025

clients.json JS Fichier clients issu du site web

meteo.csv Météo journalière par ville de livraison

source_catalogue.db Tables producteurs, produits, approvisionnement

Aucun dictionnaire de données n'est fourni : explorez.
Les notions

Quiz :
Quelle est la différence entre une clé primaire et une clé étrangère ?
Qu'est-ce qu'un LEFT JOIN retourne de plus qu'un INNER JOIN ?
OLTP et OLAP : donnez un exemple de chaque pour FraîchExpress.
Que signifie la « granularité » d'une table de faits ?
Quelle est la différence entre WHERE et HAVING ?
En pandas, quelle est la différence entre merge et concat ?
Qu'est-ce que le surapprentissage ? Comment le détecter ?
Pourquoi ne mesure-t-on pas la performance d'un modèle sur ses données d'entraînement ?
Qu'est-ce qu'une clé de substitution (surrogate key) et pourquoi l'utiliser dans une dimension ?
À quoi sert la troisième forme normale ?
À quoi sert un index ? Quel est son coût ?
Débug

Trois scripts, trois problèmes. Pour chacun : reproduire, expliquer la cause, corriger, écrire un test qui aurait détecté le problème.

Script 1 : lecture du fichier commandes

import pandas as pd

df = pd.readcsv("commandes2025.csv")

print(df.shape)

print(df["quantite"].sum())

Script 2 : chiffre d'affaires

import pandas as pd

lignes = pd.DataFrame({

    "id_commande": ["A", "A", "B"],

    "id_produit": [1, 2, 1],

    "quantite": [2, 1, 3],

})

produits = pd.DataFrame({

    "id_produit": [1, 1, 2],

    "libelle": ["Tomates", "Tomates ", "Miel"],

    "prix_unitaire": [4.2, 4.2, 7.5],

})

df = lignes.merge(produits, on="id_produit")

print("CA total :", df["prix_unitaire"].sum())

Script 3 : panier moyen

def moyenne_panier(commandes):

    total = 0

    for c in commandes:

        total += c["montant"]

    return total / len(commandes)

print(moyenne_panier([]))

print(moyenne_panier([{"montant": "12.5"}, {"montant": "8"}]))

ETL

Mission

Construire un pipeline Python qui lit les 4 sources et produit une couche propre dans une base SQLite fraichexpress.db.

Tables cibles (contrat d'interface)

clean_clients Un client réel = une ligne. Dates au format ISO, code postal texte, ville normalisée

cleanclientmapping Correspondance idsource → idclient retenu

clean_produits Libellés et catégories normalisés

clean_producteurs Producteurs du catalogue

clean_approvisionnement Qui fournit quoi, et quand

cleancommandelignes Une ligne = un produit dans une commande. Types corrects (dates, réels), statuts et modes normalisés

clean_meteo Une ligne par ville et par jour. Valeur manquante = NULL

rejets Chaque ligne écartée : source, contenu brut, motif, date de traitement

Explorez chaque source. Rédigez docs/qualitedonnees.md : pour chaque anomalie, indiquez la source, la colonne, le nombre de lignes touchées, la règle de traitement retenue et pourquoi cette règle (corriger, rejeter, ou laisser vide)._

Contraintes :

-Sources intouchables : aucun fichier de data/sources/ n'est modifié.

-Traçable : un fichier de logs par exécution, avec les volumes lus, acceptés et rejetés.

-Aucune commande sans client existant dans clean_clients ;

-Aucune date hors de l'année 2025 dans les commandes ;

À la fin de ce bloc, calculez le chiffre d'affaires livré 2025 et le nombre de clients. Comparez entre vous.
Modalités pédagogiques
Modélisation

Partie A :

Voici le cahier des charges tel que la directrice l'a rédigé :

« FraîchExpress vend des produits issus de producteurs partenaires. Un client passe des commandes, chaque commande contenant un ou plusieurs produits en certaines quantités. Les prix évoluent au cours de l'année : ce que paie le client doit rester celui du jour de la commande. Une commande est livrée à domicile, dans un point relais, ou retirée à la ferme. Certains produits peuvent provenir de plusieurs producteurs selon la saison. Nous voulons connaître, pour chaque commande, si elle a été livrée ou annulée, et pourquoi. »

Ce texte est volontairement incomplet et ambigu.

    Lister au moins 5 hypothèses ou questions que vous poseriez à la directrice, et la réponse que vous retenez pour avancer.
    Établir les règles de gestion numérotées.
    Produire le MCD (entités, associations, cardinalités, associations porteuses de propriétés).
    En déduire le MLD, puis le MPD sous forme de script SQL avec contraintes (PRIMARY KEY, FOREIGN KEY, CHECK, NOT NULL).
    Répondre en 3 lignes : où faut-il conserver le prix, et pourquoi ?

Partie B : modèle en étoile

La directrice veut répondre à ces questions sans écrire de SQL compliqué :

    Quel est le CA par catégorie de produit et par mois ?
    Quel est le taux d'annulation selon le mode de livraison et la météo ?
    Quels sont les produits les plus vendus par producteur ?
    Les clients récents ont-ils un panier moyen différent des clients anciens ?
    Quelle part du CA vient de producteurs certifiés bio ?

Travail demandé :

Choisir et justifier la granularité de la table de faits.

Identifier les mesures (additives, semi-additives, non additives) et les dimensions, avec leurs attributs.

Dessiner le schéma en étoile.

Écrire le script SQL de création et de chargement à partir des tables

Valider : le CA de l'étoile est égal au CA de la couche métier.
Répondre en quelques lignes : pourquoi ne pas normaliser les dimensions (flocon) ici ? Quelles mesures ne peuvent pas être additionnées sans précaution ?

Hypothèses documentées, MCD/MLD/MPD cohérents entre eux
SQL

Répondez aux questions sur votre entrepôt en étoile.
Chiffre d'affaires livré par mois en 2025.
Top 5 des produits par chiffre d'affaires livré.
Panier moyen par mode de livraison (commandes livrées).
Taux d'annulation par mode de livraison.
Liste des clients n'ayant passé qu'une seule commande.
Pour chaque catégorie, le produit qui génère le plus de CA.

Défis
Évolution du CA d'un mois sur l'autre, en pourcentage.
Clients dont le dernier achat livré date de plus de 60 jours avant le 31/12/2025.
CA cumulé par producteur, mois après mois.
Taux d'annulation selon qu'il a plu plus de 5 mm ou non le jour de la commande (météo de la ville du client), par mode de livraison.

Optimisation

Un stagiaire a écrit cette requête. Elle « marche » mais devient lente quand la base grossit. Les noms de tables sont ceux d'un schéma classique : adaptez-les au vôtre.

SELECT c.ville,

  (SELECT COUNT(*) FROM fact_ligne_commande f2

   WHERE f2.clientsk = c.clientsk

     AND strftime('%m', (SELECT d.date FROM dim_date d

                         WHERE d.datekey = f2.datekey)) = '07') AS nblignesjuillet

FROM dim_client c

ORDER BY nblignesjuillet DESC;

Lisez le plan d'exécution (EXPLAIN QUERY PLAN) et expliquez ce qui coûte cher.

Proposez une réécriture et, si utile, un index.

Mesurez le temps avant/après (répétez la requête plusieurs fois pour lisser).

Piège à surveiller : avant de rendre un chiffre, demandez-vous ce qu'on compte exactement (des lignes ? des commandes ? des clients ?).
ML

La logistique perd de l'argent quand une commande est annulée au dernier moment (tournée à vide, produits périssables). Elle peut appeler le client la veille pour vérifier qu'il sera présent.

Prédire, pour chaque commande, la probabilité qu'elle soit annulée, afin de décider qui appeler.

Coûts métier :

Situation Coût

Annulation non anticipée 14 €

Appel de vérification inutile 2 €

Appel utile ou absence d'annulation sans appel 0 €

(On simplifie : un appel utile évite complètement l'annulation.)

Étapes
Construire le jeu de données : une ligne par commande, à partir de votre entrepôt (agrégats de lignes, informations client, mode de livraison, météo de la ville du client, calendrier). Justifiez chaque variable retenue.
Modèles : au moins une régression et un modèle à base d'arbres, dans un Pipeline scikit-learn.
Évaluer

Choisir un seuil de décision qui minimise le coût total sur le jeu de test, puis chiffrer le gain par rapport à « ne rien faire ».

Interpréter : quelles variables comptent le plus ? Est-ce cohérent avec ce que vous savez du métier ?

Note d'une page à la directrice (docs/note_direction.md) : que recommandez-vous, avec quels chiffres, et quelles limites ?
Sujets ouverts et veille

La directrice veut aussi savoir « ce qui existe et ce qui vaut le coup ». Choisir un sujet :

RAG : un assistant pourrait-il répondre aux questions du service client à partir des données de la coopérative ? À quelles conditions ?

RGPD : que faut-il anonymiser ou pseudonymiser dans notre base clients ? Quelle différence, et quelles limites ?

Biais et équité : notre modèle d'annulation pourrait-il pénaliser certains clients (zones géographiques, nouveaux clients) ? Comment le vérifier ?

Qualité et observabilité des données : contrats de données, tests automatiques, alertes. Comment éviter de retomber dans la situation de départ ?
Modalités d'évaluation

Rendu
Livrables
Lien github du projet avec documentation