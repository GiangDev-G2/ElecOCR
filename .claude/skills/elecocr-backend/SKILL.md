---
name: elecocr-backend
description: Implement or review ElecOCR FastAPI endpoints, application services, schemas, errors, logging, model lifecycle, and backend tests. Use for work under backend/ or changes to the HTTP contract; do not use for model training or visual design alone.
---

# ElecOCR Backend

Read these sources before editing:

- `docs/02-YEU-CAU-VA-NGHIEM-THU.md`
- `docs/03-KIEN-TRUC-HE-THONG.md`
- `docs/06-API-VA-UI.md`
- `docs/09-QUY-UOC-MA-NGUON.md`

For API-specific verification, also read [references/api-checklist.md](references/api-checklist.md).

## Workflow

1. Identify the affected API/application/domain boundary.
2. Define or update typed schema/domain objects before route glue.
3. Keep transport, orchestration, and model adapters separate.
4. Implement stable exception mapping and structured logs.
5. Add unit plus contract/integration tests for the changed behavior.
6. Run Ruff, mypy, and the relevant pytest scope.

Preserve these invariants: reading is a string; business statuses are not HTTP 500 errors; routes do not contain OCR logic; uploaded images are not persisted by default. The normal orchestration calls one detector and one recognizer; an eligible quality-gated fallback may add at most one recognition retry.
