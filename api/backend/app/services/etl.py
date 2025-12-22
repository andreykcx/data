from __future__ import annotations

import csv
import io
from typing import Iterable

from backend.app.schemas import DataPoint

EXPECTED_HEADERS = ["x", "y"]


class CsvValidationError(ValueError):
    """Raised when an uploaded CSV fails validation."""


def _normalize_headers(headers: Iterable[str]) -> list[str]:
    normalized = []
    for header in headers:
        if header is None:
            continue
        normalized.append(header.strip().lstrip("\ufeff").lower())
    return normalized


def load_xy_csv(file_bytes: bytes) -> list[DataPoint]:
    """Validate and load CSV content into a list of DataPoint objects.

    The CSV must contain a header row with exactly two columns: ``x`` and ``y``.
    Values must be numeric and non-null. Extra or missing columns are rejected.
    """

    try:
        decoded = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise exc

    reader = csv.DictReader(io.StringIO(decoded))

    if reader.fieldnames is None:
        raise CsvValidationError("CSV header must be exactly: x,y")

    normalized_headers = _normalize_headers(reader.fieldnames)
    if normalized_headers != EXPECTED_HEADERS:
        found_headers = ",".join(normalized_headers)
        raise CsvValidationError(f"CSV header must be exactly: x,y (found: {found_headers})")

    datapoints: list[DataPoint] = []
    for idx, row in enumerate(reader, start=2):
        raw_x = row.get("x")
        raw_y = row.get("y")

        if raw_x is None or raw_y is None:
            raise CsvValidationError(f"Row {idx} contains missing values for x or y.")

        if raw_x == "" or raw_y == "":
            raise CsvValidationError(f"Row {idx} contains missing values for x or y.")

        try:
            x_value = float(raw_x)
            y_value = float(raw_y)
        except ValueError:
            raise CsvValidationError(f"Row {idx} contains non-numeric x or y value.")

        datapoints.append(DataPoint(x=x_value, y=y_value))

    if not datapoints:
        raise CsvValidationError("CSV must contain at least one x,y row.")

    return datapoints
