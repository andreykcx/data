from __future__ import annotations

import random
from typing import Iterable, Sequence, Tuple

from backend.app.schemas import DataPoint

DEFAULT_SPLIT_SEED = 42
DEFAULT_TEST_RATIO = 0.2


def split_dataset(
    data: Sequence[DataPoint],
    *,
    test_ratio: float = DEFAULT_TEST_RATIO,
    seed: int = DEFAULT_SPLIT_SEED,
) -> Tuple[list[DataPoint], list[DataPoint]]:
    """Create a deterministic train/test split of the dataset."""

    if not data:
        return [], []

    rng = random.Random(seed)
    indices = list(range(len(data)))
    rng.shuffle(indices)

    test_size = max(1, int(len(data) * test_ratio))

    test_split = [data[i] for i in indices[:test_size]]
    train_split = [data[i] for i in indices[test_size:]]

    return train_split, test_split


def features_and_target(data: Iterable[DataPoint]) -> Tuple[list[list[float]], list[float]]:
    """Return features (x) and target (y) arrays for model training."""

    features: list[list[float]] = []
    targets: list[float] = []

    for point in data:
        features.append([point.x])
        targets.append(point.y)

    return features, targets
