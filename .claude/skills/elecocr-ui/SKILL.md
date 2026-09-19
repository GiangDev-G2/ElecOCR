---
name: elecocr-ui
description: Design, implement, or review the ElecOCR React and TypeScript web interface using the Calm Glass Precision system. Use for frontend/, Vite, UI states, responsive behavior, accessibility, CSS tokens, and backend-to-UI presentation mapping.
---

# ElecOCR UI

Read:

- `docs/ui-ux.md`
- `docs/06-API-VA-UI.md`
- `.claude/design/INDEX.md`

Read [references/visual-checklist.md](references/visual-checklist.md) before final visual review.

## Workflow

1. Identify the user state and API fields being represented.
2. Confirm OpenAPI-derived transport types and isolate HTTP in the OCR feature API client.
3. Model request state explicitly and keep presentation components free of OCR/business logic.
4. Use shared design tokens; do not add local colors, radii, or shadows.
5. Keep image input larger than the result column on wide screens.
6. Make reading, status, confidence, ROI, warning and retry behavior explicit.
7. Preserve reading as a string from API to DOM.
8. Verify keyboard use, contrast, reduced motion and target sizes.
9. Check 1440, 1024, 768 and 390 px widths.
10. Run Prettier check, ESLint, TypeScript, Vitest and Vite build.

Frontend must call FastAPI through the typed HTTP client. Hide missing debug artifacts rather than fabricating them. Do not use `any`, convert readings to numbers, or persist uploaded images by default.
