export type BackendReadiness =
  | { kind: "checking" }
  | { kind: "ready"; modelVersion: string }
  | { kind: "offline"; message: string };

export interface OcrResultView {
  requestId: string;
  status: "ok" | "review_required" | "unreadable" | "error";
  reading: string | null;
  confidence: number | null;
  meterType: "mechanical" | "electronic" | "unknown";
  decimalStyle: "dot" | "comma" | "red_digits" | "none" | "unknown";
  warnings: string[];
  totalLatencyMs: number;
  modelVersion: string;
}

export type OcrRequestState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success"; result: OcrResultView }
  | { kind: "failure"; message: string };
