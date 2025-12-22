from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from backend.app.schemas import DataPoint, DatasetUploadResponse
from backend.app.services import etl, ml


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Example API")

cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", response_model=HealthResponse)
def read_root() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/datasets/upload",
    response_model=DatasetUploadResponse,
    summary="Upload CSV dataset with x and y columns",
)
async def upload_dataset(file: UploadFile = File(..., description="CSV with x and y headers")) -> DatasetUploadResponse:
    """Validate an uploaded CSV and return deterministic train/test splits."""

    try:
        contents = await file.read()
        datapoints = etl.load_xy_csv(contents)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 encoded and include x,y headers.")
    except etl.CsvValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    train_split, test_split = ml.split_dataset(datapoints)

    return DatasetUploadResponse(
        rows=len(datapoints),
        train_rows=len(train_split),
        test_rows=len(test_split),
        train=[DataPoint.model_validate(point) for point in train_split],
        test=[DataPoint.model_validate(point) for point in test_split],
    )
