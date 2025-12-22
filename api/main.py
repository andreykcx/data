import os
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.schemas import DataPoint, DatasetUploadResponse, ModelRequest, ModelResponse
from backend.app.services import etl, ml
from backend.app.db import check_database_connection, run_migrations_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str


DEFAULT_CORS_ORIGINS = {"http://localhost:5173", "http://frontend:5173"}


def _cors_origins() -> list[str]:
    user_origins = {
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    }
    return sorted(DEFAULT_CORS_ORIGINS.union(user_origins))


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations_with_retry()
    yield


app = FastAPI(title="Example API", lifespan=lifespan)

cors_origins = _cors_origins()

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


@app.get("/health", response_model=HealthResponse, summary="Health check with database connectivity")
def health_check() -> HealthResponse:
    if not check_database_connection():
        raise HTTPException(status_code=503, detail="Database is unavailable.")
    return HealthResponse(status="ok")


async def verify_api_key(request: Request) -> None:
    expected_api_key: Optional[str] = os.getenv("API_KEY")
    if expected_api_key and request.headers.get("x-api-key") != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


@app.post(
    "/datasets/upload",
    response_model=DatasetUploadResponse,
    summary="Upload CSV dataset with x and y columns",
)
async def upload_dataset(
    file: UploadFile = File(..., description="CSV with x and y headers"),
    _: None = Depends(verify_api_key),
) -> DatasetUploadResponse:
    """Validate an uploaded CSV and return deterministic train/test splits."""

    try:
        contents = await file.read()
        datapoints = etl.load_xy_csv(contents)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Uploaded file must be UTF-8 encoded and include x,y headers.")
    except etl.CsvValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    dataset_id = uuid.uuid4()
    train_split, test_split = ml.split_dataset(datapoints)

    logger.info(
        "Dataset %s uploaded: total_rows=%s, train_rows=%s, test_rows=%s",
        dataset_id,
        len(datapoints),
        len(train_split),
        len(test_split),
    )

    return DatasetUploadResponse(
        dataset_id=dataset_id,
        rows=len(datapoints),
        train_rows=len(train_split),
        test_rows=len(test_split),
        train=[DataPoint.model_validate(point) for point in train_split],
        test=[DataPoint.model_validate(point) for point in test_split],
    )


@app.post(
    "/model",
    response_model=ModelResponse,
    summary="Train simple linear regression and return line parameters",
)
def train_model(request: ModelRequest) -> ModelResponse:
    """Train a simple regression model using uploaded x,y points."""

    try:
        result = ml.train_simple_linear_regression(request.data)
    except ml.ModelTrainingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    dataset_id = request.dataset_id or uuid.uuid4()
    logger.info(
        "Model trained for dataset %s: rows=%s",
        dataset_id,
        len(request.data),
    )

    return ModelResponse(
        slope=result.slope,
        intercept=result.intercept,
        r_squared=result.r_squared,
        line=[DataPoint.model_validate(point) for point in result.line],
    )
