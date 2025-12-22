from __future__ import annotations

from pydantic import BaseModel, Field


class DataPoint(BaseModel):
    """Single observation with x feature and y target."""

    x: float = Field(..., description="Feature value")
    y: float = Field(..., description="Target value")

    model_config = {
        "extra": "forbid",
    }


class DatasetUploadResponse(BaseModel):
    """Response returned after dataset upload and split."""

    rows: int
    train_rows: int
    test_rows: int
    train: list[DataPoint]
    test: list[DataPoint]

    model_config = {
        "extra": "forbid",
    }
