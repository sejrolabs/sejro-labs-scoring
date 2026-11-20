from collections.abc import Sequence
from typing import Protocol, Self


class RecencyTransformer(Protocol):
    def fit(self, values: Sequence[float]) -> Self: ...

    def transform(self, values: Sequence[float]) -> list[float]: ...
