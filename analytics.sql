-- BigQuery GoogleSQL. Les tables d'entrée sont orders_raw et customers_raw.
WITH commandes AS (
  SELECT order_id, customer_id, order_purchase_timestamp
  FROM `sejro-olist-lab-scoring.olist_lab.orders_raw`
  WHERE order_id IS NOT NULL AND order_purchase_timestamp IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY order_purchase_timestamp, customer_id
  ) = 1
),
clients AS (
  SELECT customer_id, customer_unique_id
  FROM `sejro-olist-lab-scoring.olist_lab.customers_raw`
  WHERE customer_id IS NOT NULL AND customer_unique_id IS NOT NULL
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY customer_id ORDER BY customer_unique_id
  ) = 1
),
historique AS (
  SELECT
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp AS date_achat,
    LAG(o.order_purchase_timestamp) OVER (
      PARTITION BY c.customer_unique_id
      ORDER BY o.order_purchase_timestamp, o.order_id
    ) AS date_achat_precedent
  FROM commandes AS o
  JOIN clients AS c USING (customer_id)
)
SELECT
  customer_unique_id,
  order_id,
  date_achat_precedent,
  date_achat,
  TIMESTAMP_DIFF(date_achat, date_achat_precedent, HOUR) AS heures_depuis_achat
FROM historique
WHERE date_achat_precedent IS NOT NULL;
