-- BigQuery GoogleSQL. Importer olist_order_items_dataset.csv comme order_items_raw.
-- price représente le prix de l'article hors livraison, en réais.
WITH parametres AS (
  SELECT TIMESTAMP '2018-01-01 00:00:00+00' AS date_scoring
),
commandes_livrees AS (
  SELECT
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp AS date_achat,
    o.order_delivered_customer_date AS date_livraison
  FROM `sejro-olist-lab-scoring.olist_lab.orders_raw` AS o
  JOIN `sejro-olist-lab-scoring.olist_lab.customers_raw` AS c USING (customer_id)
  WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    AND c.customer_unique_id IS NOT NULL
),
montants_par_commande AS (
  SELECT
    order_id,
    IF(COUNTIF(price IS NULL) = 0, SUM(CAST(price AS NUMERIC)), NULL) AS montant
  FROM `sejro-olist-lab-scoring.olist_lab.order_items_raw`
  GROUP BY order_id
),
historique AS (
  SELECT
    o.customer_unique_id,
    p.date_scoring,
    MAX(o.date_achat) AS dernier_achat,
    COUNT(*) AS frequence,
    IF(COUNTIF(m.montant IS NULL) = 0, SUM(m.montant), NULL) AS montant_articles_brl,
    COUNTIF(m.montant IS NULL) AS commandes_sans_montant
  FROM commandes_livrees AS o
  CROSS JOIN parametres AS p
  LEFT JOIN montants_par_commande AS m USING (order_id)
  WHERE o.date_achat <= p.date_scoring
    AND o.date_livraison <= p.date_scoring
  GROUP BY o.customer_unique_id, p.date_scoring
),
rachats AS (
  SELECT DISTINCT o.customer_unique_id
  FROM commandes_livrees AS o
  CROSS JOIN parametres AS p
  WHERE o.date_achat > p.date_scoring
    AND o.date_achat <= TIMESTAMP_ADD(p.date_scoring, INTERVAL 90 DAY)
)
SELECT
  h.customer_unique_id,
  h.date_scoring,
  h.dernier_achat,
  TIMESTAMP_DIFF(h.date_scoring, h.dernier_achat, DAY) AS recence_jours,
  h.frequence,
  h.montant_articles_brl,
  h.commandes_sans_montant,
  IF(r.customer_unique_id IS NULL, 0, 1) AS rachat_90j
FROM historique AS h
LEFT JOIN rachats AS r USING (customer_unique_id);
