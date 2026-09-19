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
            decimalStyle: "red_digits",
            warnings: [],
            totalLatencyMs: 120,
            modelVersion: "test-model",
          },
        }}
      />,
    );

    expect(screen.getByText("00012.3")).toBeInTheDocument();
  });
});
