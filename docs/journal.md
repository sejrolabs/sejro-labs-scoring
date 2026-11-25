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
