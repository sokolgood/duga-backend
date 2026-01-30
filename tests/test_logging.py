import logging
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture(scope="module")
def test_client():
    client = TestClient(app)
    yield client

@pytest.fixture(autouse=True)
def caplog(caplog):
    # Optional: add specific log level filtering
    caplog.set_level(logging.INFO)
    yield caplog


def test_startup_logging(caplog, test_client):
    with caplog.at_level(logging.INFO):
        response = test_client.get("")
    # Verifying startup log
    assert "Starting FastAPI app..." in caplog.text
    assert response.status_code == 200


def test_shutdown_logging(caplog, test_client):
    with caplog.at_level(logging.INFO):
        response = test_client.get("/health")
    # Verifying shutdown log after startup
    assert "Shutting down FastAPI app..." in caplog.text
    assert response.status_code == 200
