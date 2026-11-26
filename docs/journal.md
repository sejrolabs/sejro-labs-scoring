## Git et ingénierie Python

J’ai intégré sur `main` le notebook d’analyse exploratoire Olist. Il couvre
la saisonnalité des commandes, les délais de livraison et deux façons de
définir le rachat à 90 jours. En simulant une décision CRM au 1er janvier
2018, j’ai observé 290 rachats parmi 39 964 clients éligibles, soit 0,73 %.

La date de scoring fixe les informations dont l’équipe CRM dispose pour
choisir les clients à contacter. Un délai réel de livraison entre dans les
variables seulement si la livraison a déjà eu lieu. Si aucune commande
du client n’a été livrée à cette date, son délai moyen reste manquant.

Pour évaluer un ciblage limité à 1 000 contacts, je mesurerai la part
des futurs acheteurs retrouvés dans le top 1 000 et la comparerai à une
sélection au hasard. Le rappel du classement par récence reste à mesurer
sur Olist.

En semaine 2, je commence par des fixtures pytest sur des données Olist
synthétiques pour vérifier le chargement et les schémas. Je réutiliserai
cette logique de test pour vérifier les frontières temporelles lors de
la construction des variables RFM et de la cible à 90 jours.

## Semaine 2 · Pytest, BigQuery et A/B testing

Les huit tests d’ingestion Olist couvrent 87,10 % du chargeur, branches
comprises. Ils vérifient notamment les dates, les clés et les articles
orphelins, et simulent un refus d’accès au CSV. Avec le module A/B,
la suite compte douze tests qui passent.

Dans BigQuery, pour la fenêtre de 90 jours étudiée, le partitionnement
par jour d’achat ramène le volume estimé de 776,88 à 165,69 Ko
(−78,7 %), pour les mêmes 21 208 commandes. Le clustering a été étudié
sur le plan conceptuel, sans mesure supplémentaire.

Les requêtes SQL validées dans BigQuery retrouvent 3 345 intervalles
entre commandes, 39 964 clients éligibles au 1er janvier 2018 et
290 clients ayant racheté dans les 90 jours. Le classement par récence
retrouve 13 de ces clients dans le top 1 000, soit 4,48 % de rappel,
contre environ 7,26 clients attendus au hasard. Cette comparaison
repose sur une seule date de scoring.

Le notebook A/B utilise des résultats de campagne simulés. À partir
du taux historique de 0,73 %, détecter une hausse de 0,20 point avec
80 % de puissance et un risque bilatéral de 5 % demande environ
64 268 clients au total. Le notebook illustre aussi le contrôle de
la répartition des groupes (SRM) et la méthode Delta.

En semaine 3, construire des cohortes à plusieurs dates de scoring
avec une fenêtre de suivi complète, puis évaluer une régression
logistique sur une cohorte ultérieure avec la PR-AUC.
