import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_requires_database(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    response = client.get("/health")
    assert response.status_code == 503


def test_upload_dataset_success(sample_csv_bytes):
    response = client.post(
        "/datasets/upload",
        files={"file": ("data.csv", sample_csv_bytes, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["rows"] == 5
    assert body["train_rows"] + body["test_rows"] == 5
    assert body["dataset_id"]

    # Deterministic split ensures consistent ordering
    assert body["train"][0] == {"x": 2.0, "y": 4.0}


@pytest.mark.parametrize(
    "csv_bytes,expected_detail",
    [
        (b"a,b\n1,2\n", "CSV header must be exactly: x,y"),
        (b"x\n1\n", "CSV header must be exactly: x,y"),
        (b"x,y,z\n1,2,3\n", "CSV header must be exactly: x,y"),
        (b"x,y\n1,\n", "Row 2 contains missing values for x or y."),
        (b"x,y\n1,foo\n", "Row 2 contains non-numeric x or y value."),
    ],
)
def test_upload_dataset_validation_errors(csv_bytes, expected_detail):
    response = client.post(
        "/datasets/upload",
        files={"file": ("data.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 400
    assert expected_detail in response.json()["detail"]


def test_upload_requires_api_key(monkeypatch, sample_csv_bytes):
    monkeypatch.setenv("API_KEY", "supersecret")
    response = client.post(
        "/datasets/upload",
        files={"file": ("data.csv", sample_csv_bytes, "text/csv")},
    )
    assert response.status_code == 401
    assert "Invalid or missing API key." in response.json()["detail"]


@pytest.fixture
def sample_csv_bytes() -> bytes:
    return b"x,y\n1,1\n2,4\n3,9\n4,16\n5,25\n"


def test_train_model_success():
    payload = {"data": [{"x": 1.0, "y": 1.0}, {"x": 2.0, "y": 4.0}, {"x": 3.0, "y": 9.0}]}

    response = client.post("/model", json=payload)
    assert response.status_code == 200
    body = response.json()

    assert "slope" in body and "intercept" in body and "r_squared" in body
    assert len(body["line"]) == 2
    assert body["line"][0]["x"] <= body["line"][1]["x"]


def test_train_model_validation_errors():
    payload = {"data": [{"x": 1.0, "y": 2.0}]}  # only one row
    response = client.post("/model", json=payload)
    assert response.status_code == 400
    assert "At least two" in response.json()["detail"]
