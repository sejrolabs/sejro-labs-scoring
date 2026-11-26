import pytest

from mktscore.ab_stats import p_valeur_srm, ratio_et_erreur, taille_par_groupe


def test_dimensionnement_augmente_quand_effet_diminue() -> None:
    assert taille_par_groupe(0.5, 0.6) == 388
    assert taille_par_groupe(0.5, 0.55) > 388


def test_srm_compare_les_effectifs_au_plan() -> None:
    assert p_valeur_srm(500, 500) == 1
    assert p_valeur_srm(800, 200, part_controle=0.8) == pytest.approx(1)
    assert p_valeur_srm(600, 400) < 0.001


def test_ratio_tient_compte_des_paires_client() -> None:
    ratio, erreur = ratio_et_erreur([0, 4], [1, 1])
    assert ratio == 2
    assert erreur == pytest.approx(2)


def test_ratio_refuse_un_denominateur_total_nul() -> None:
    with pytest.raises(ValueError, match="dénominateur total"):
        ratio_et_erreur([0, 0], [0, 0])
