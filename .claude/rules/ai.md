---
paths:
  - "backend/**/detection/**/*.py"
  - "backend/**/preprocessing/**/*.py"
  - "backend/**/recognition/**/*.py"
  - "backend/**/postprocessing/**/*.py"
  - "backend/**/quality/**/*.py"
  - "backend/ai/**/*.py"
  - "configs/**/*.yaml"
  - "configs/**/*.yml"
  - "configs/**/*.json"
  - "configs/**/*.toml"
---

# Quy tắc AI và xử lý ảnh

- Đọc `docs/04-DU-LIEU.md`, `docs/05-HUAN-LUYEN-VA-DANH-GIA.md` và phần AI trong chuẩn mã nguồn.
- Ảnh nội bộ mặc định là RGB HWC `uint8` trong `[0, 255]`; mọi ngoại lệ phải được ghi rõ tại boundary.
- Luồng mặc định phải tối giản: canonicalize ảnh → detector → crop có padding → chuẩn hóa input recognizer → một lần recognizer → quyết định trạng thái.
- Không chạy song song các biến thể RGB/CLAHE/nhị phân trong luồng mặc định. Perspective rectification hoặc tăng tương phản chỉ là fallback có quality gate; mỗi ảnh được retry recognizer tối đa một lần.
- Tensor model dùng BCHW; shape, dtype, range và device phải rõ trong contract/docstring.
- Không hard-code charset, input size, threshold hoặc normalization trong inference function.
- Dùng `model.eval()` và `torch.inference_mode()` khi suy luận.
- Không gọi `.cuda()`/`.half()` rải rác; device và dtype được cấu hình tập trung.
- Train/inference preprocessing phải có parity test.
- Recognizer phải được huấn luyện và đánh giá với predicted crop cùng crop jitter, không chỉ với ground-truth crop hoàn hảo.
- Mọi run ghi seed, config, code version, data manifest, metric và checkpoint.
- Không dùng test split để chọn model hoặc threshold.
- Metric chính là exact-match toàn chuỗi; luôn báo cáo theo loại đồng hồ và kiểu thập phân.
