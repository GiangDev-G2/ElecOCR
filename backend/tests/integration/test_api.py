from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from backend.ai.contracts import ImageArray
from backend.ai.domain import OcrPrediction, OcrStatus
from backend.app.main import create_app
from backend.app.service import OcrService
from backend.app.settings import Settings


def _client() -> TestClient:
    settings = Settings(model_version="unavailable")
    return TestClient(create_app(settings=settings))


class ReadyPipeline:
    """Small deterministic pipeline double for API contract tests."""

    @property
    def is_ready(self) -> bool:
        return True

    @property
    def model_version(self) -> str:
        return "test-model"

    def predict(self, source_image: ImageArray, *, debug: bool) -> OcrPrediction:
        del source_image, debug
        return OcrPrediction(
            status=OcrStatus.OK,
            reading="00012.3",
            raw_reading="00012.3",
            confidence=0.98,
        )


def _ready_client() -> TestClient:
    settings = Settings(model_version="test-model")
    service = OcrService(pipeline=ReadyPipeline(), settings=settings)
    return TestClient(create_app(settings=settings, ocr_service=service))


def _png_bytes() -> bytes:
    image = Image.new("RGB", (8, 6), color=(20, 30, 40))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


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


def test_ocr_with_request_id_returns_same_request_id() -> None:
    response = _ready_client().post(
        "/v1/ocr",
        headers={"X-Request-ID": "request-from-client"},
        files={"image": ("meter.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["request_id"] == "request-from-client"
    assert response.json()["reading"] == "00012.3"
