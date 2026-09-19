from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.settings import Settings


def _client() -> TestClient:
    settings = Settings(model_version="unavailable")
    return TestClient(create_app(settings=settings))


def test_health_returns_ok() -> None:
    response = _client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_without_model_returns_stable_error() -> None:
    response = _client().get("/ready", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 503
    assert response.json() == {
        "request_id": "test-request",
        "status": "error",
        "error": {"code": "MODEL_NOT_READY", "message": "Model OCR chưa sẵn sàng."},
    }


def test_ocr_with_invalid_file_returns_invalid_image() -> None:
    response = _client().post(
        "/v1/ocr",
        files={"image": ("meter.png", b"invalid", "image/png")},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_IMAGE"
