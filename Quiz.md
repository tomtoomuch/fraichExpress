Quelle est la différence entre une clé primaire et une clé étrangère ?

Une clé primaire identifie de facon unique un ligne dasn une table, clé d'indexation unique.
Clé étrangére est une clé  qui sert de réference dans une autre table 
Qu'est-ce qu'un LEFT JOIN retourne de plus qu'un INNER JOIN ?

Par exemple dans la relation client et commande, left join retourne tous les clients qui ont une commande et ceux qui n'ont pas de comnandes.
Inner Join : retourne que les clients qui ont une commande.
OLTP et OLAP : donnez un exemple de chaque pour FraîchExpress.
OLTP : Online transactionnel processing, gérer les transctions en temps réelles, application bancaire
OLAP : Online analytical processing : permet de gérer les transaction de gros volume de données.
Que signifie la « granularité » d'une table de faits ?

Le niveau de détail le plus fin géré par un systéme. Ex : fruit pour le client et pour le producteur : le panier.
Quelle est la différence entre WHERE et HAVING ? 

Where filtre les données en testant les colonnes avant l'aggregation. Having filtre aprés l'aggregation.
En pandas, quelle est la différence entre merge et concat ?

concat :  fusionne les  dataframes cote à cote.
merge : combine des DataFrames horizontalement selon des valeurs communes dans des colonnes ou des index (comme une jointure SQL).
Qu'est-ce que le surapprentissage ? Comment le détecter ?

Le surapprentissage (ou overfitting) se produit lorsqu'un modèle d'intelligence artificielle mémorise les données d'entraînement au lieu d'en comprendre la logique générale.
Comparaison des erreurs - Courbes d'apprentissage - Validation croisée
Pourquoi ne mesure-t-on pas la performance d'un modèle sur ses données d'entraînement ?

Par ce qu'il les connait déja
Qu'est-ce qu'une clé de substitution (surrogate key) et pourquoi l'utiliser dans une dimension ?


Une clé de substitution (surrogate key) est un identifiant unique artificiel (généralement un entier auto-incrémenté ou un UUID) généré par le système pour chaque ligne d'une table, sans aucune signification métier.
Historisation - performance sur les jointures - stabilité - unicité 

À quoi sert la troisième forme normale ?

3NF : La troisième forme normale (3NF) est une règle de conception de base de données qui élimine les dépendances transitives entre les colonnes.
Moins de redondance - meilleure cohérence - intégrité des données

À quoi sert un index ? Quel est son coût ?

Sert à accelerer les recherches dans une base de données. Manque de souplesse, trop d'index peut ralentir les opérations CRUD.