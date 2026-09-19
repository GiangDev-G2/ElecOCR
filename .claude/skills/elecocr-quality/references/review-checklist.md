# Quality review checklist

## Product

- Reading remains a string and preserves leading zeros.
- Decimal normalization and ambiguity policy match requirements.
- All four OCR statuses have coherent behavior.

## Architecture and code

- Frontend calls HTTP only; routes contain no OCR logic.
- React presentation components do not call HTTP directly; TypeScript is strict and API transport types match OpenAPI.
- Reading remains a string through API mapping, React state and rendering.
- Default inference uses one detector crop and one recognition call; it has no always-on parallel image variants.
- Any perspective/contrast fallback is quality-gated, chooses at most one transformation, retries recognition at most once, and converts disagreement to `review_required`.
- Names follow the shared domain vocabulary.
- Image/tensor conventions and units are explicit.
- No broad `Any`, magic thresholds, scattered device logic or catch-all utility modules.
- Exceptions are specific and translated only at boundaries.

## Data and ML

- Test data was not used for tuning.
- Split leakage was checked.
- Exact-match and subgroup metrics are reported honestly.
- Model/export parity and confidence calibration are tested when relevant.
- Recognizer evaluation includes predicted crops and crop jitter, not only perfect ground-truth crops.

## Safety and delivery

- No datasets, images, checkpoints, secrets or sensitive logs are committed.
- Ruff, mypy, pytest and the applicable frontend format/lint/typecheck/test/build gates were run or explicitly reported unavailable.
- Behavior, API and architectural changes update the corresponding docs/ADR.
