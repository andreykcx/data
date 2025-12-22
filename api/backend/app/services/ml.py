from __future__ import annotations

import random
from dataclasses import dataclass
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


class ModelTrainingError(ValueError):
    """Raised when model training cannot proceed."""


@dataclass(frozen=True)
class ModelResult:
    slope: float
    intercept: float
    r_squared: float
    line: list[DataPoint]


def train_simple_linear_regression(data: Sequence[DataPoint]) -> ModelResult:
    """Fit a simple linear regression ``y = slope * x + intercept``.

    Requires at least two rows with varying ``x`` values. Returns the
    slope/intercept along with two points describing the fitted line spanning the
    observed ``x`` range.
    """

    if len(data) < 2:
        raise ModelTrainingError("At least two x,y rows are required to fit a model.")

    x_values = [float(point.x) for point in data]
    y_values = [float(point.y) for point in data]

    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)

    denominator = sum((x - x_mean) ** 2 for x in x_values)
    if denominator == 0:
        raise ModelTrainingError("x values must vary to compute a regression line.")

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    # Coefficient of determination (R^2)
    residuals = [y - (slope * x + intercept) for x, y in zip(x_values, y_values)]
    ss_res = sum(value**2 for value in residuals)
    ss_tot = sum((y - y_mean) ** 2 for y in y_values)
    r_squared = 1.0 if ss_tot == 0 else 1 - ss_res / ss_tot

    min_x = min(x_values)
    max_x = max(x_values)

    line_points = [
        DataPoint(x=min_x, y=slope * min_x + intercept),
        DataPoint(x=max_x, y=slope * max_x + intercept),
    ]

    return ModelResult(slope=slope, intercept=intercept, r_squared=r_squared, line=line_points)
