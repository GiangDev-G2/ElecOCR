import type { components } from "../../../api/generated/schema";

type ApiErrorResponse = components["schemas"]["ApiErrorResponse"];
type OcrResponse = components["schemas"]["OcrResponse"];
type ReadinessResponse = components["schemas"]["ReadinessResponse"];

const API_URL = import.meta.env.VITE_ELECOCR_API_URL ?? "http://127.0.0.1:8000";
const REQUEST_TIMEOUT_MS = 30_000;

export class ApiClientError extends Error {
  public readonly code: string;

  public constructor(code: string, message: string) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
  }
}

async function request(input: string, init?: RequestInit): Promise<Response> {
  const timeoutController = new AbortController();
  const timeoutId = window.setTimeout(() => {
    timeoutController.abort();
  }, REQUEST_TIMEOUT_MS);
  const externalSignal = init?.signal;
  const abortFromExternal = () => {
    timeoutController.abort();
  };
  externalSignal?.addEventListener("abort", abortFromExternal, { once: true });

  try {
    return await fetch(`${API_URL}${input}`, {
      ...init,
      signal: timeoutController.signal,
    });
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiClientError(
        "REQUEST_ABORTED",
        "Yêu cầu đã bị hủy hoặc hết thời gian.",
      );
    }
    throw new ApiClientError(
      "NETWORK_ERROR",
      "Không kết nối được với bộ xử lý.",
    );
  } finally {
    window.clearTimeout(timeoutId);
    externalSignal?.removeEventListener("abort", abortFromExternal);
  }
}

async function parseError(response: Response): Promise<never> {
  const fallbackMessage = `Backend trả về HTTP ${String(response.status)}.`;
  try {
    const body = (await response.json()) as ApiErrorResponse;
    throw new ApiClientError(body.error.code, body.error.message);
  } catch (error: unknown) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    throw new ApiClientError("HTTP_ERROR", fallbackMessage);
  }
}

export async function getReadiness(): Promise<ReadinessResponse> {
  const response = await request("/ready");
  if (!response.ok) {
    return parseError(response);
  }
  return (await response.json()) as ReadinessResponse;
}

export async function submitOcr(
  image: File,
  signal: AbortSignal,
): Promise<OcrResponse> {
  const body = new FormData();
  body.append("image", image, image.name);
  body.append("debug", "true");

  const response = await request("/v1/ocr", { method: "POST", body, signal });
  if (!response.ok) {
    return parseError(response);
  }
  return (await response.json()) as OcrResponse;
}
