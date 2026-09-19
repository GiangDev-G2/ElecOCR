import type { components } from "../../../api/generated/schema";
import type { OcrResultView } from "./types";

type OcrResponse = components["schemas"]["OcrResponse"];

export function presentOcrResponse(response: OcrResponse): OcrResultView {
  return {
    requestId: response.request_id,
    status: response.status,
    reading: response.reading,
    confidence: response.confidence ?? null,
    meterType: response.meter_type,
    decimalStyle: response.decimal_style,
    warnings: response.warnings,
    totalLatencyMs: response.latency_ms.total,
    modelVersion: response.model_version,
  };
}

export function formatConfidence(confidence: number | null): string {
  return confidence === null ? "Chưa có" : `${(confidence * 100).toFixed(1)}%`;
}
