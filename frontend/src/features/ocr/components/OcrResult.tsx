import { formatConfidence } from "../model/presenter";
import type { OcrRequestState } from "../model/types";
import { StatusBadge } from "./StatusBadge";

interface OcrResultProps {
  state: OcrRequestState;
}

const STATUS_PRESENTATION = {
  ok: { tone: "success", label: "Đọc thành công" },
  review_required: { tone: "warning", label: "Cần kiểm tra" },
  unreadable: { tone: "error", label: "Không đọc được" },
  error: { tone: "error", label: "Có lỗi xử lý" },
} as const;

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
  const presentation = STATUS_PRESENTATION[result.status];
  return (
    <div className="result-content" aria-live="polite">
      <StatusBadge tone={presentation.tone}>{presentation.label}</StatusBadge>
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
      {result.warnings.length > 0 && (
        <ul className="result-warnings" aria-label="Cảnh báo kết quả">
          {result.warnings.map((warning) => (
            <li key={warning}>{warning}</li>
          ))}
        </ul>
      )}
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
