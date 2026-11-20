from pathlib import Path

import pandas as pd

ORDER_DATE_COLUMNS = (
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
)


class OlistDataLoader:
    def __init__(self, raw_dir: Path) -> None:
        self.raw_dir = raw_dir

    def load_orders(self) -> pd.DataFrame:
        orders_path = self.raw_dir / "olist_orders_dataset.csv"
        commandes = pd.read_csv(orders_path)

        if "order_id" not in commandes.columns:
            raise ValueError("olist_orders_dataset.csv : colonne order_id manquante")

        if commandes["order_id"].isna().any():
            raise ValueError(
                "olist_orders_dataset.csv : au moins un order_id est manquant"
            )

        if commandes["order_id"].duplicated().any():
            raise ValueError(
                "olist_orders_dataset.csv : au moins un order_id est en double"
            )

        for column in ORDER_DATE_COLUMNS:
            if column not in commandes.columns:
                raise ValueError(
                    f"olist_orders_dataset.csv : colonne {column} manquante"
                )

            commandes[column] = pd.to_datetime(
                commandes[column],
                format="%Y-%m-%d %H:%M:%S",
                errors="raise",
            )

        if commandes["order_purchase_timestamp"].isna().any():
            raise ValueError("olist_orders_dataset.csv : date d’achat manquante")

        return commandes

    def load_order_items(self) -> pd.DataFrame:
        items_path = self.raw_dir / "olist_order_items_dataset.csv"

        items = pd.read_csv(items_path)
        cle = ["order_id", "order_item_id"]

        for colonne in cle:
            if colonne not in items.columns:
                raise ValueError(
                    f"olist_order_items_dataset.csv : colonne {colonne} manquante"
                )

        if items[cle].isna().any(axis=1).any():
            raise ValueError("olist_order_items_dataset.csv : clé de ligne incomplète")

        if items.duplicated(subset=cle).any():
            raise ValueError("olist_order_items_dataset.csv : clé de ligne en double")

        return items

    @staticmethod
    def validate_order_links(commandes: pd.DataFrame, items: pd.DataFrame) -> None:
        articles_orphelins = items.loc[~items["order_id"].isin(commandes["order_id"])]

        if not articles_orphelins.empty:
            article = articles_orphelins.iloc[0]
            raise ValueError(
                f"Commande introuvable pour l’article : "
                f"order_id={article['order_id']}, order_item_id={article['order_item_id']}"
            )
