---
name: elecocr-quality
description: Review ElecOCR changes for requirement compliance, clean code, architecture boundaries, tests, privacy, API compatibility, and ML evaluation integrity. Use after implementation or when the user asks for an audit, review, readiness check, or quality gate.
---

# ElecOCR Quality Review

Read the changed files first, then the smallest relevant set of project docs. Use [references/review-checklist.md](references/review-checklist.md) for the final pass.

## Review order

1. Correctness and violations of product invariants.
2. Data leakage, metric validity and confidence/rejection behavior.
3. API compatibility, security and privacy.
4. Architecture boundaries, naming and type safety.
5. Tests, documentation and reproducibility.
6. Performance only after correctness.

Report findings by severity with file and line references. Separate verified defects from suggestions. Do not change code unless the user asks for fixes.

