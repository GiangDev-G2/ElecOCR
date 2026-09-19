"""FastAPI composition root for ElecOCR."""

from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.ai.errors import (
    ElecOcrError,
    ImageTooLargeError,
    InvalidImageError,
    ModelNotReadyError,
    UnsupportedImageError,
)
from backend.ai.pipeline import UnavailableOcrPipeline
from backend.app.schemas import (
    ApiError,
    ApiErrorResponse,
    HealthResponse,
    OcrLatency,
    OcrResponse,
    ReadinessResponse,
    VersionResponse,
)
from backend.app.service import OcrService
from backend.app.settings import Settings

API_VERSION = "v1"


def _error_status(error: ElecOcrError) -> tuple[int, str, str]:
    if isinstance(error, UnsupportedImageError):
        return 415, "UNSUPPORTED_MEDIA_TYPE", "Tệp tải lên không thuộc định dạng được hỗ trợ."
    if isinstance(error, ImageTooLargeError):
        return 413, "FILE_TOO_LARGE", "Ảnh vượt quá giới hạn kích thước cho phép."
    if isinstance(error, InvalidImageError):
        return 422, "INVALID_IMAGE", "Tệp tải lên không phải ảnh hợp lệ."
    if isinstance(error, ModelNotReadyError):
        return 503, "MODEL_NOT_READY", "Model OCR chưa sẵn sàng."
    return 500, "INTERNAL_ERROR", "Hệ thống không thể xử lý yêu cầu."


def create_app(
    *,
    settings: Settings | None = None,
    ocr_service: OcrService | None = None,
) -> FastAPI:
    """Create an application with explicit, replaceable dependencies."""
    resolved_settings = settings or Settings()
    resolved_service = ocr_service or OcrService(
        pipeline=UnavailableOcrPipeline(resolved_settings.model_version),
        settings=resolved_settings,
    )

    app = FastAPI(title="ElecOCR API", version=resolved_settings.app_version)
    app.state.settings = resolved_settings
    app.state.ocr_service = resolved_service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved_settings.frontend_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.exception_handler(ElecOcrError)
    async def handle_elecocr_error(request: Request, error: ElecOcrError) -> JSONResponse:
        request_id = request.headers.get("x-request-id", str(uuid4()))
        status_code, code, message = _error_status(error)
        body = ApiErrorResponse(
            request_id=request_id,
            error=ApiError(code=code, message=message),
        )
        return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get(
        "/ready",
        response_model=ReadinessResponse,
        responses={503: {"model": ApiErrorResponse}},
    )
    async def ready() -> ReadinessResponse:
        if not resolved_service.is_ready:
            raise ModelNotReadyError("No OCR model bundle is currently loaded.")
        return ReadinessResponse(status="ready", model_version=resolved_service.model_version)

    @app.get("/version", response_model=VersionResponse)
    async def version() -> VersionResponse:
        return VersionResponse(
            api_version=API_VERSION,
            app_version=resolved_settings.app_version,
            model_version=resolved_service.model_version,
        )

    @app.post(
        "/v1/ocr",
        response_model=OcrResponse,
        responses={
            413: {"model": ApiErrorResponse},
            415: {"model": ApiErrorResponse},
            422: {"model": ApiErrorResponse},
            503: {"model": ApiErrorResponse},
        },
    )
    async def recognize(
        image: Annotated[UploadFile, File()],
        debug: Annotated[bool, Form()] = False,
    ) -> OcrResponse:
        started_at = perf_counter()
        image_bytes = await image.read(resolved_settings.max_image_bytes + 1)
        prediction = resolved_service.recognize(
            image_bytes,
            media_type=image.content_type,
            debug=debug,
        )
        total_ms = (perf_counter() - started_at) * 1000
        return OcrResponse(
            request_id=str(uuid4()),
            status=prediction.status,
            reading=prediction.reading,
            raw_reading=prediction.raw_reading,
            confidence=prediction.confidence,
            meter_type=prediction.meter_type,
            decimal_style=prediction.decimal_style,
            display_polygon=[],
            alternatives=[],
            warnings=list(prediction.warnings),
            latency_ms=OcrLatency(
                total=total_ms,
                canonicalization=0,
                localization=0,
                recognition=0,
                fallback=0,
                decision=0,
            ),
            model_version=resolved_service.model_version,
        )

    return app


app = create_app()
