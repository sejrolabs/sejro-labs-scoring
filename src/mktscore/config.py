from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScoringConfig:
    prediction_horizon_days: int = 90
