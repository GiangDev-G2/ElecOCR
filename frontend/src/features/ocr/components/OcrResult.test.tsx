import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { OcrResult } from "./OcrResult";

describe("OcrResult", () => {
  it("preserves leading zeros in the rendered reading", () => {
    render(
      <OcrResult
        state={{
          kind: "success",
          result: {
            requestId: "request-1",
            status: "ok",
            reading: "00012.3",
            confidence: 0.98,
            meterType: "mechanical",
            decimalStyle: "red_digit",
            warnings: [],
            totalLatencyMs: 120,
            modelVersion: "test-model",
          },
        }}
      />,
    );

    expect(screen.getByText("00012.3")).toBeInTheDocument();
  });

  it.each([
    ["review_required", "Cần kiểm tra"],
    ["unreadable", "Không đọc được"],
    ["error", "Có lỗi xử lý"],
  ] as const)("renders the %s status distinctly", (status, label) => {
    render(
      <OcrResult
        state={{
          kind: "success",
          result: {
            requestId: "request-2",
            status,
            reading: status === "review_required" ? "00012.3" : null,
            confidence: status === "review_required" ? 0.62 : null,
            meterType: "unknown",
            decimalStyle: "unknown",
            warnings: [],
            totalLatencyMs: 80,
            modelVersion: "test-model",
          },
        }}
      />,
    );

    expect(screen.getByText(label)).toBeInTheDocument();
  });
});
