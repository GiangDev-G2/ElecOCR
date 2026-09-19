import { useRef } from "react";

import { OcrResult } from "./components/OcrResult";
import { StatusBadge } from "./components/StatusBadge";
import { useOcrController } from "./hooks/useOcrController";

export function OcrPage() {
  const controller = useOcrController();
  const fileInput = useRef<HTMLInputElement>(null);
  const isSubmitting = controller.requestState.kind === "submitting";
  const canRecognize =
    controller.selectedImage !== null &&
    controller.readiness.kind === "ready" &&
    !isSubmitting;

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="ElecOCR - trang chính">
          <span className="brand__mark" aria-hidden="true">
            E
          </span>
          <span>ElecOCR</span>
        </a>
        {controller.readiness.kind === "ready" ? (
          <StatusBadge tone="success">Model sẵn sàng</StatusBadge>
        ) : controller.readiness.kind === "checking" ? (
          <StatusBadge tone="neutral">Đang kiểm tra backend</StatusBadge>
        ) : (
          <button
            className="readiness-button"
            onClick={() => void controller.refreshReadiness()}
          >
            <StatusBadge tone="error">Backend chưa sẵn sàng</StatusBadge>
          </button>
        )}
      </header>

      <main className="page-content">
        <section className="intro">
          <p className="eyebrow">Xử lý ảnh · OCR local</p>
          <h1>Đọc chỉ số đồng hồ điện</h1>
          <p>
            Tải một ảnh đồng hồ cơ hoặc điện tử. Hệ thống tự tìm vùng số và giữ
            nguyên số 0 ở đầu.
          </p>
        </section>

        <section className="workspace" aria-label="Không gian nhận dạng">
          <div className="panel input-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Ảnh đầu vào</p>
                <h2>Chọn ảnh đồng hồ</h2>
              </div>
              {controller.selectedImage !== null && (
                <button className="text-button" onClick={controller.clearImage}>
                  Xóa ảnh
                </button>
              )}
            </div>

            <input
              ref={fileInput}
              className="visually-hidden"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(event) => {
                controller.selectImage(event.target.files?.[0] ?? null);
              }}
            />

            {controller.previewUrl === null ? (
              <button
                className="upload-zone"
                onClick={() => {
                  fileInput.current?.click();
                }}
              >
                <span className="upload-zone__icon" aria-hidden="true">
                  +
                </span>
                <strong>Kéo-thả hoặc chọn một ảnh</strong>
                <span>JPG, PNG hoặc WebP · tối đa 12 MB</span>
              </button>
            ) : (
              <div className="image-stage">
                <img
                  src={controller.previewUrl}
                  alt="Ảnh đồng hồ điện đã chọn"
                />
              </div>
            )}

            <div className="action-row">
              <button
                className="secondary-button"
                onClick={() => {
                  fileInput.current?.click();
                }}
              >
                {controller.selectedImage === null
                  ? "Chọn ảnh"
                  : "Chọn ảnh khác"}
              </button>
              <button
                className="primary-button"
                disabled={!canRecognize}
                onClick={() => void controller.recognize()}
              >
                {isSubmitting ? "Đang nhận dạng…" : "Đọc chỉ số"}
              </button>
            </div>
          </div>

          <aside className="panel result-panel" aria-label="Kết quả OCR">
            <OcrResult state={controller.requestState} />
          </aside>
        </section>

        {controller.readiness.kind === "offline" && (
          <p className="backend-notice" role="status">
            {controller.readiness.message}
          </p>
        )}
      </main>
    </div>
  );
}
