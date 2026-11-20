from collections.abc import Sequence
from typing import Protocol, Self


class BinaryClassifier(Protocol):
    def fit(
        self, features: Sequence[Sequence[float]], labels: Sequence[int]
    ) -> Self: ...

    def predict(self, features: Sequence[Sequence[float]]) -> list[int]: ...
