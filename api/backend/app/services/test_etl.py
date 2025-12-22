from __future__ import annotations

import pytest

from backend.app.services import etl


def test_load_xy_csv_validates_and_parses_rows(sample_csv_bytes):
    datapoints = etl.load_xy_csv(sample_csv_bytes)

    assert len(datapoints) == 5
    assert datapoints[0].x == 1.0
    assert datapoints[0].y == 1.0
    assert all(isinstance(point.x, float) and isinstance(point.y, float) for point in datapoints)


@pytest.mark.parametrize(
    "csv_bytes,expected_detail",
    [
        (b"x,y\n1,\n", "Row 2 contains missing values for x or y."),
        (b"x,y\n1,foo\n", "Row 2 contains non-numeric x or y value."),
        (b"a,b\n1,2\n", "CSV header must be exactly: x,y"),
        (b"x\n1\n", "CSV header must be exactly: x,y"),
        (b"x,y,z\n1,2,3\n", "CSV header must be exactly: x,y"),
    ],
)
def test_load_xy_csv_rejects_invalid(csv_bytes: bytes, expected_detail: str):
    with pytest.raises(etl.CsvValidationError) as exc_info:
        etl.load_xy_csv(csv_bytes)

    assert expected_detail in str(exc_info.value)


@pytest.fixture
def sample_csv_bytes() -> bytes:
    return b"x,y\n1,1\n2,4\n3,9\n4,16\n5,25\n"
