import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useOcrController } from "./useOcrController";

vi.mock("../api/ocrClient", () => ({
  ApiClientError: class ApiClientError extends Error {},
  getReadiness: vi.fn().mockResolvedValue({
    status: "ready",
    model_version: "test-model",
  }),
  submitOcr: vi.fn(),
}));

describe("useOcrController", () => {
  beforeEach(() => {
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn().mockReturnValue("blob:meter-preview"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("clears the previous image when the replacement file is unsupported", async () => {
    const { result } = renderHook(() => useOcrController());
    await waitFor(() => {
      expect(result.current.readiness.kind).toBe("ready");
    });

    act(() => {
      result.current.selectImage(
        new File(["valid"], "meter.png", { type: "image/png" }),
      );
    });
    expect(result.current.selectedImage?.name).toBe("meter.png");

    act(() => {
      result.current.selectImage(
        new File(["invalid"], "notes.txt", { type: "text/plain" }),
      );
    });

    expect(result.current.selectedImage).toBeNull();
    expect(result.current.previewUrl).toBeNull();
    expect(result.current.requestState).toEqual({
      kind: "failure",
      message: "Chỉ hỗ trợ JPG, PNG hoặc WebP.",
    });
  });
});
