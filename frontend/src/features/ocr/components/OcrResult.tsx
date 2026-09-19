import { formatConfidence } from "../model/presenter";
import type { OcrRequestState } from "../model/types";
import { StatusBadge } from "./StatusBadge";

interface OcrResultProps {
  state: OcrRequestState;
}

export function OcrResult({ state }: OcrResultProps) {
  if (state.kind === "failure") {
    return (
      <div className="result-empty" role="alert">
        <StatusBadge tone="error">Không thể xử lý</StatusBadge>
        <p>{state.message}</p>
      </div>
    );
  }
  if (state.kind === "submitting") {
    return (
      <div className="result-empty" aria-live="polite">
        <span className="spinner" aria-hidden="true" />
        <p>Đang nhận dạng…</p>
      </div>
    );
  }
  if (state.kind === "idle") {
    return (
      <div className="result-empty">
        <p className="eyebrow">Kết quả</p>
        <h2>Chưa có chỉ số</h2>
        <p>Kết quả đọc và độ tin cậy sẽ xuất hiện tại đây.</p>
      </div>
    );
  }

  const { result } = state;
  const tone = result.status === "ok" ? "success" : "warning";
  const label = result.status === "ok" ? "Đọc thành công" : "Cần kiểm tra";
  return (
    <div className="result-content" aria-live="polite">
      <StatusBadge tone={tone}>{label}</StatusBadge>
      <p
        className="reading"
        aria-label={`Chỉ số nhận dạng: ${result.reading ?? "không có"}`}
      >
        {result.reading ?? "—"}
      </p>
      <div className="result-metadata">
        <span>Độ tin cậy</span>
        <strong>{formatConfidence(result.confidence)}</strong>
      </div>
      <details>
        <summary>Chi tiết kỹ thuật</summary>
        <dl className="technical-list">
          <div>
            <dt>Model</dt>
            <dd>{result.modelVersion}</dd>
          </div>
          <div>
            <dt>Độ trễ</dt>
            <dd>{result.totalLatencyMs.toFixed(1)} ms</dd>
          </div>
          <div>
            <dt>Request ID</dt>
            <dd>{result.requestId}</dd>
          </div>
        </dl>
      </details>
    </div>
  );
}
