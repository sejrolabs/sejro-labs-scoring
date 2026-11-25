from pathlib import Path

import pandas as pd
import pytest

from mktscore.data.loader import OlistDataLoader


@pytest.fixture(scope="session")
def commandes_csv() -> str:
    return (
        "order_id,order_purchase_timestamp,order_approved_at,"
        "order_delivered_carrier_date,order_delivered_customer_date,"
        "order_estimated_delivery_date\n"
        "cmd-1,2017-12-28 10:00:00,2017-12-28 10:05:00,"
        ",,2018-01-05 00:00:00\n"
    )


@pytest.fixture
def fichier_commandes(tmp_path: Path, commandes_csv: str) -> Path:
    fichier = tmp_path / "olist_orders_dataset.csv"
    fichier.write_text(commandes_csv, encoding="utf-8")
    return fichier


def test_charge_une_commande_en_cours(fichier_commandes: Path) -> None:
    commandes = OlistDataLoader(fichier_commandes.parent).load_orders()

    assert commandes["order_id"].tolist() == ["cmd-1"]
    assert commandes.loc[0, "order_purchase_timestamp"] == pd.Timestamp(
        "2017-12-28 10:00:00"
    )
    assert commandes["order_delivered_customer_date"].isna().iloc[0]


def test_rejette_un_csv_sans_colonne_order_id(fichier_commandes: Path) -> None:
    commandes = pd.read_csv(fichier_commandes).drop(columns="order_id")
    commandes.to_csv(fichier_commandes, index=False)

    with pytest.raises(ValueError, match="colonne order_id manquante"):
        OlistDataLoader(fichier_commandes.parent).load_orders()


def test_rejette_un_article_sans_commande(fichier_commandes: Path) -> None:
    dossier = fichier_commandes.parent
    fichier_articles = dossier / "olist_order_items_dataset.csv"
    fichier_articles.write_text(
        "order_id,order_item_id\ncmd-1,1\ncmd-absente,1\n",
        encoding="utf-8",
    )

    chargeur = OlistDataLoader(dossier)
    commandes = chargeur.load_orders()
    articles = chargeur.load_order_items()

    with pytest.raises(ValueError, match="order_id=cmd-absente"):
        chargeur.validate_order_links(commandes, articles)


def test_accepte_plusieurs_articles_pour_une_commande(
    fichier_commandes: Path,
) -> None:
    dossier = fichier_commandes.parent
    fichier_articles = dossier / "olist_order_items_dataset.csv"
    fichier_articles.write_text(
        "order_id,order_item_id\ncmd-1,1\ncmd-1,2\n",
        encoding="utf-8",
    )

    chargeur = OlistDataLoader(dossier)
    commandes = chargeur.load_orders()
    articles = chargeur.load_order_items()

    chargeur.validate_order_links(commandes, articles)

    assert len(commandes) == 1
    assert list(zip(articles["order_id"], articles["order_item_id"], strict=True)) == [
        ("cmd-1", 1),
        ("cmd-1", 2),
    ]


@pytest.mark.parametrize(
    ("lignes", "message"),
    [
        pytest.param(
            "cmd-1,\n",
            "clé de ligne incomplète",
            id="numero-article-manquant",
        ),
        pytest.param(
            "cmd-1,1\ncmd-1,1\n",
            "clé de ligne en double",
            id="article-duplique",
        ),
    ],
)
def test_rejette_une_cle_article_invalide(
    tmp_path: Path, lignes: str, message: str
) -> None:
    fichier = tmp_path / "olist_order_items_dataset.csv"
    fichier.write_text(f"order_id,order_item_id\n{lignes}", encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        OlistDataLoader(tmp_path).load_order_items()


def test_rejette_une_commande_sans_date_achat(
    fichier_commandes: Path,
) -> None:
    commandes = pd.read_csv(fichier_commandes)
    commandes["order_purchase_timestamp"] = ""
    commandes.to_csv(fichier_commandes, index=False)

    with pytest.raises(ValueError, match="date d’achat manquante"):
        OlistDataLoader(fichier_commandes.parent).load_orders()


def test_signale_un_fichier_commandes_inaccessible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fichier_attendu = tmp_path / "olist_orders_dataset.csv"

    def lecture_refusee(chemin: Path) -> pd.DataFrame:
        assert chemin == fichier_attendu
        raise PermissionError("Accès refusé au fichier des commandes")

    monkeypatch.setattr(pd, "read_csv", lecture_refusee)

    with pytest.raises(PermissionError, match="Accès refusé"):
        OlistDataLoader(tmp_path).load_orders()
