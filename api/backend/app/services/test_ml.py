from __future__ import annotations

import pytest

from backend.app.schemas import DataPoint
from backend.app.services import ml


def test_split_dataset_is_deterministic(sample_points):
    train1, test1 = ml.split_dataset(sample_points, seed=123)
    train2, test2 = ml.split_dataset(sample_points, seed=123)

    assert train1 == train2
    assert test1 == test2
    assert len(train1) + len(test1) == len(sample_points)


def test_split_dataset_respects_ratio(sample_points):
    train, test = ml.split_dataset(sample_points, test_ratio=0.5, seed=1)
    assert len(test) == max(1, int(len(sample_points) * 0.5))
    assert len(train) + len(test) == len(sample_points)


def test_split_dataset_handles_empty_input():
    train, test = ml.split_dataset([])
    assert train == []
    assert test == []


def test_features_and_target_maps_x_and_y(sample_points):
    features, targets = ml.features_and_target(sample_points)
    assert features == [[1.0], [2.0], [3.0]]
    assert targets == [10.0, 20.0, 30.0]


def test_features_and_target_returns_float_types(sample_points):
    features, targets = ml.features_and_target(sample_points)
    assert all(isinstance(row[0], float) for row in features)
    assert all(isinstance(target, float) for target in targets)


def test_split_dataset_returns_datapoints(sample_points):
    train, test = ml.split_dataset(sample_points)
    assert all(isinstance(point, DataPoint) for point in train + test)


def test_split_dataset_minimum_one_test_row(sample_points):
    train, test = ml.split_dataset(sample_points, test_ratio=0.0)
    assert len(test) == 1
    assert len(train) + len(test) == len(sample_points)


def test_split_dataset_preserves_values(sample_points):
    train, test = ml.split_dataset(sample_points, seed=5)
    combined = train + test
    assert sorted((p.x, p.y) for p in combined) == sorted((p.x, p.y) for p in sample_points)


def test_features_and_target_handles_single_point():
    features, targets = ml.features_and_target([DataPoint(x=5.5, y=11.0)])
    assert features == [[5.5]]
    assert targets == [11.0]


def test_split_dataset_handles_single_point():
    data = [DataPoint(x=1.0, y=2.0)]
    train, test = ml.split_dataset(data)
    assert train == []
    assert test == data


def test_split_dataset_does_not_modify_input(sample_points):
    original = list(sample_points)
    ml.split_dataset(sample_points, seed=42)
    assert sample_points == original


def test_features_and_target_does_not_modify_input(sample_points):
    original = list(sample_points)
    ml.features_and_target(sample_points)
    assert sample_points == original


def test_split_dataset_with_larger_data():
    data = [DataPoint(x=float(i), y=float(i * 2)) for i in range(10)]
    train, test = ml.split_dataset(data, test_ratio=0.3, seed=123)
    assert len(test) == max(1, int(len(data) * 0.3))
    assert len(train) + len(test) == len(data)


def test_features_and_target_accepts_ints():
    data = [DataPoint(x=1, y=2), DataPoint(x=3, y=4)]
    features, targets = ml.features_and_target(data)
    assert features == [[1.0], [3.0]]
    assert targets == [2.0, 4.0]


def test_split_dataset_seed_changes_split(sample_points):
    data = [DataPoint(x=float(i), y=float(i * 2)) for i in range(5)]
    _, test1 = ml.split_dataset(data, seed=1, test_ratio=0.4)
    _, test2 = ml.split_dataset(data, seed=2, test_ratio=0.4)
    assert test1 != test2


def test_split_dataset_returns_lists(sample_points):
    train, test = ml.split_dataset(sample_points)
    assert isinstance(train, list)
    assert isinstance(test, list)


def test_features_and_target_length_matches(sample_points):
    features, targets = ml.features_and_target(sample_points)
    assert len(features) == len(sample_points)
    assert len(targets) == len(sample_points)


@pytest.fixture
def sample_points():
    return [
        DataPoint(x=1.0, y=10.0),
        DataPoint(x=2.0, y=20.0),
        DataPoint(x=3.0, y=30.0),
    ]
