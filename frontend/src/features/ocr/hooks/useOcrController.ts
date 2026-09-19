import { useCallback, useEffect, useRef, useState } from "react";

import { ApiClientError, getReadiness, submitOcr } from "../api/ocrClient";
import { presentOcrResponse } from "../model/presenter";
import type { BackendReadiness, OcrRequestState } from "../model/types";

const SUPPORTED_MEDIA_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
]);
const MAX_UPLOAD_BYTES = 12 * 1024 * 1024;

export function useOcrController() {
  const [readiness, setReadiness] = useState<BackendReadiness>({
    kind: "checking",
  });
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [requestState, setRequestState] = useState<OcrRequestState>({
    kind: "idle",
  });
  const activeRequest = useRef<AbortController | null>(null);

  const refreshReadiness = useCallback(async () => {
    try {
      const response = await getReadiness();
      setReadiness({ kind: "ready", modelVersion: response.model_version });
    } catch (error: unknown) {
      const message =
        error instanceof ApiClientError
          ? error.message
          : "Không kiểm tra được backend.";
      setReadiness({ kind: "offline", message });
    }
  }, []);

  useEffect(() => {
    let isActive = true;
    void getReadiness()
      .then((response) => {
        if (isActive) {
          setReadiness({ kind: "ready", modelVersion: response.model_version });
        }
      })
      .catch((error: unknown) => {
        if (isActive) {
          const message =
            error instanceof ApiClientError
              ? error.message
              : "Không kiểm tra được backend.";
          setReadiness({ kind: "offline", message });
        }
      });
    return () => {
      isActive = false;
      activeRequest.current?.abort();
    };
  }, []);

  useEffect(() => {
    return () => {
      if (previewUrl !== null) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const clearImage = useCallback(() => {
    activeRequest.current?.abort();
    setSelectedImage(null);
    setPreviewUrl(null);
    setRequestState({ kind: "idle" });
  }, []);

  const selectImage = useCallback((file: File | null) => {
    activeRequest.current?.abort();
    setRequestState({ kind: "idle" });
    if (file === null) {
      setSelectedImage(null);
      setPreviewUrl(null);
      return;
    }
    if (!SUPPORTED_MEDIA_TYPES.has(file.type)) {
      setRequestState({
        kind: "failure",
        message: "Chỉ hỗ trợ JPG, PNG hoặc WebP.",
      });
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      setRequestState({
        kind: "failure",
        message: "Ảnh vượt quá giới hạn 12 MB.",
      });
      return;
    }
    setSelectedImage(file);
    setPreviewUrl(URL.createObjectURL(file));
  }, []);

  const recognize = useCallback(async () => {
    if (selectedImage === null || readiness.kind !== "ready") {
      return;
    }
    const controller = new AbortController();
    activeRequest.current = controller;
    setRequestState({ kind: "submitting" });
    try {
      const response = await submitOcr(selectedImage, controller.signal);
      setRequestState({
        kind: "success",
        result: presentOcrResponse(response),
      });
    } catch (error: unknown) {
      const message =
        error instanceof ApiClientError ? error.message : "Không thể đọc ảnh.";
      setRequestState({ kind: "failure", message });
    } finally {
      if (activeRequest.current === controller) {
        activeRequest.current = null;
      }
    }
  }, [readiness.kind, selectedImage]);

  return {
    readiness,
    selectedImage,
    previewUrl,
    requestState,
    refreshReadiness,
    selectImage,
    clearImage,
    recognize,
  };
}
