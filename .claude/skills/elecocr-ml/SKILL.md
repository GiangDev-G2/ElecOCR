---
name: elecocr-ml
description: Develop or evaluate the minimal ElecOCR pipeline, image canonicalization, display localization, recognition, conditional fallback, confidence calibration, training, export, and ML tests. Use for backend/ai/ modules, configs/, datasets, metrics, or model artifacts.
---

# ElecOCR ML

Read:

- `docs/04-DU-LIEU.md`
- `docs/05-HUAN-LUYEN-VA-DANH-GIA.md`
- AI/image conventions in `docs/09-QUY-UOC-MA-NGUON.md`

Use [references/experiment-checklist.md](references/experiment-checklist.md) when training, comparing, exporting, or reporting a model.

## Workflow

1. State the experiment question and acceptance metric.
2. Verify dataset provenance, manifest, split and leakage checks.
3. Keep image/tensor conventions explicit at every adapter boundary.
4. Keep the default path to one detector and one recognizer call; add at most one gated retry.
5. Change one controlled factor when running an ablation.
6. Tune only on train/validation; keep test locked.
7. Save config, seed, environment, metrics, predictions and model manifest.
8. Run shape/dtype smoke tests and end-to-end evaluation.

Exact-match is the primary OCR metric. Report mechanical/electronic and decimal-style slices. Do not present synthetic-only results as evidence of real-world performance.
