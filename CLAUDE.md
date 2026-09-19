# ElecOCR — Project Instructions

## Mission

Build ElecOCR as a local application with a React + TypeScript frontend and a Python FastAPI/AI backend that detects and reads electricity-meter displays from one image. Support mechanical and electronic meters, preserve leading zeros, and handle decimal points, commas, and red fractional digits.

## Source of truth

Read only the documents relevant to the current task:

- Requirements: `docs/02-YEU-CAU-VA-NGHIEM-THU.md`
- Architecture: `docs/03-KIEN-TRUC-HE-THONG.md`
- Data: `docs/04-DU-LIEU.md`
- ML and evaluation: `docs/05-HUAN-LUYEN-VA-DANH-GIA.md`
- API: `docs/06-API-VA-UI.md`
- UI/UX: `docs/ui-ux.md`
- Decisions and risks: `docs/08-RUI-RO-VA-QUYET-DINH.md`
- Coding standard: `docs/09-QUY-UOC-MA-NGUON.md`

When documents conflict, follow the latest confirmed user request, then requirements, ADRs, coding standards, architecture, and existing code in that order.

## Non-negotiable invariants

- Treat every reading as a string. Never convert it to `int` or `float`.
- Normalize comma decimals to a dot while preserving raw evidence.
- Never guess an ambiguous decimal position. Return `review_required`.
- Use only `ok`, `review_required`, `unreadable`, or `error` as OCR statuses.
- Do not use the test split to tune models, thresholds, preprocessing, or postprocessing.
- Do not commit datasets, user images, model weights, secrets, or image-bearing logs.
- Frontend communicates with backend through HTTP; it never imports the OCR pipeline.
- Frontend uses React function components, strict TypeScript and Vite. It treats the FastAPI OpenAPI contract as the source for transport types and never converts a reading to a number.
- Routes contain transport logic only. OCR and image-processing logic belongs in the application/pipeline layers.
- Keep the default inference path minimal: canonicalize image -> detect display -> padded crop -> normalize recognizer input -> one recognition call -> normalize/validate -> confidence and status decision.
- Perspective rectification and contrast enhancement are optional, quality-gated fallbacks. Run at most one fallback and one recognition retry; do not run parallel RGB/CLAHE/binary variants by default.
- Follow the project vocabulary and naming rules in `docs/09-QUY-UOC-MA-NGUON.md`.

## Workflow

1. Inspect the relevant docs and existing code before editing.
2. Make the smallest coherent change that satisfies the request.
3. Add or update tests for changed behavior.
4. Run the applicable quality gates.
5. Update docs or ADRs when a contract or architectural decision changes.
6. Report changed files, commands run, results, and unresolved limits.

## Quality gates

```powershell
ruff format --check .
ruff check .
mypy backend
pytest
npm --prefix frontend run format:check
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend run test
npm --prefix frontend run build
```

If a tool or directory does not exist yet, say so explicitly; do not claim the check passed.

## Claude extensions

- Rules: `.claude/rules/`
- Reusable skills: `.claude/skills/`
- Specialized subagents: `.claude/agents/`
- Design handoff: `.claude/design/`
- Reusable work templates: `.claude/templates/`

Use a specialized skill when its description matches the task. Use subagents for bounded investigation or independent review, not for trivial single-file edits.
