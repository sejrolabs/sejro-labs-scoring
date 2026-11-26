"""Statistiques pour une expérience CRM randomisée au niveau client."""

from collections.abc import Sequence
from math import ceil, erfc, sqrt
from statistics import NormalDist, mean, stdev


def taille_par_groupe(
    taux_reference: float,
    taux_attendu: float,
    *,
    alpha: float = 0.05,
    puissance: float = 0.8,
) -> int:
    """Approximation normale pour deux proportions et des groupes de même taille."""
    if not 0 < taux_reference < taux_attendu < 1:
        raise ValueError("Les taux doivent vérifier 0 < référence < attendu < 1.")
    if not 0 < alpha < 1 or not 0.5 < puissance < 1:
        raise ValueError("Le risque alpha ou la puissance est hors limites.")

    normale = NormalDist()
    taux_moyen = (taux_reference + taux_attendu) / 2
    seuil = normale.inv_cdf(1 - alpha / 2)
    quantile = normale.inv_cdf(puissance)
    variance_nulle = 2 * taux_moyen * (1 - taux_moyen)
    variance_alternative = taux_reference * (1 - taux_reference) + taux_attendu * (
        1 - taux_attendu
    )
    ecart = taux_attendu - taux_reference
    return ceil(
        ((seuil * sqrt(variance_nulle) + quantile * sqrt(variance_alternative)) / ecart)
        ** 2
    )


def p_valeur_srm(
    controle: int, traitement: int, *, part_controle: float = 0.5
) -> float:
    """Test du chi carré sur les effectifs assignés dans deux groupes."""
    if controle < 0 or traitement < 0 or not 0 < part_controle < 1:
        raise ValueError("Effectifs ou proportion d'assignation invalides.")
    total = controle + traitement
    attendu_controle = total * part_controle
    attendu_traitement = total * (1 - part_controle)
    if min(attendu_controle, attendu_traitement) < 5:
        raise ValueError("Le test requiert au moins cinq clients attendus par groupe.")

    chi2 = (controle - attendu_controle) ** 2 / attendu_controle + (
        traitement - attendu_traitement
    ) ** 2 / attendu_traitement
    return erfc(sqrt(chi2 / 2))


def ratio_et_erreur(
    numerateurs: Sequence[float], denominateurs: Sequence[float]
) -> tuple[float, float]:
    """Ratio des totaux et erreur standard Delta, avec une paire par client."""
    if len(numerateurs) != len(denominateurs) or len(numerateurs) < 2:
        raise ValueError("Deux observations appariées ou plus sont nécessaires.")
    if any(valeur < 0 for valeur in denominateurs):
        raise ValueError("Les dénominateurs doivent être positifs ou nuls.")
    denominateur_moyen = mean(denominateurs)
    if denominateur_moyen <= 0:
        raise ValueError("Le dénominateur total doit être strictement positif.")

    ratio = mean(numerateurs) / denominateur_moyen
    residus = [
        numerateur - ratio * denominateur
        for numerateur, denominateur in zip(numerateurs, denominateurs, strict=True)
    ]
    erreur = stdev(residus) / (sqrt(len(residus)) * denominateur_moyen)
    return ratio, erreur
