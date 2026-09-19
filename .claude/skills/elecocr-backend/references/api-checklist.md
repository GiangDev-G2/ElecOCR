# Backend/API checklist

- Request validates MIME, byte size, decoded dimensions and corrupt input.
- Response uses documented `snake_case` fields and `reading: str | None`.
- OpenAPI changes are intentional, covered by contract tests, and regenerated into frontend transport types.
- `review_required` and `unreadable` return a valid business response.
- Error response has stable code/message and no stack trace/path.
- `/ready` reflects the real model lifecycle.
- Request log includes `request_id`, `model_version`, status and latency.
- No image, base64, original filename or full reading is logged by default.
- Route delegates to an application service.
- Model/framework dependency remains behind an adapter.
- CORS permits only the configured local React origin; browser-exposed configuration contains no secrets.
- The normal request path calls the recognizer once; an eligible fallback adds at most one retry and exposes its reason in debug metadata.
- Unit, contract and failure-path tests cover the change.
