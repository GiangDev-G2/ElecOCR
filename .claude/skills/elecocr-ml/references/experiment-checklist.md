# Experiment checklist

## Before

- Question and success metric are explicit.
- Source/license and data manifest are recorded.
- Split is grouped and checked for exact/perceptual duplicates.
- Test split remains sealed.
- Seed, config and environment are fixed.

## During

- Train/inference transforms use the same contract.
- Model input/output shapes, dtype, range and device are asserted.
- Best checkpoint is selected by a predefined validation metric.
- Default inference uses one RGB crop; any fallback is gated and limited to one retry.
- Failures and OOM/restarts are recorded, not overwritten.

## After

- Report exact-match, CER, decimal accuracy, risk-coverage and P50/P95 latency.
- Report subgroups by meter type, decimal style and dataset source.
- Report fallback eligibility, retry rate and whether fallback improved or degraded the result.
- Save `config.yaml`, `environment.txt`, `data_manifest.json`, `metrics.json` and `predictions.jsonl`.
- Inspect representative failure modes without tuning on test.
- Exported model passes parity checks against the source checkpoint.
