---
paths:
  - "frontend/**/*.{ts,tsx,css,html,json}"
  - "frontend/package-lock.json"
---

# Quy tắc frontend

- Đọc `docs/ui-ux.md`, `docs/06-API-VA-UI.md` và `.claude/design/INDEX.md`.
- Dùng React function component, TypeScript strict và Vite; chỉ gọi backend qua HTTP, không sao chép pipeline hoặc checkpoint.
- Public API types phải bám OpenAPI của FastAPI; không duy trì schema TypeScript thủ công bị sai lệch.
- Giữ style `Calm · Glass · Precision` và dùng token tập trung.
- Không chuyển reading thành số hoặc format lại leading zero.
- Component trình bày không gọi API trực tiếp; HTTP, mapping response và request state nằm trong feature boundary.
- Không dùng `any`; state request phải có type không cho phép tồn tại các trạng thái mâu thuẫn.
- Thiết kế đủ `ok`, `review_required`, `unreadable`, `error`, loading và backend-offline.
- Không dùng màu làm tín hiệu trạng thái duy nhất.
- UI phải dùng được bằng bàn phím, có focus rõ và tôn trọng reduced motion.
- Không lưu ảnh/reading theo mặc định; xóa state và tệp tạm khi người dùng xóa ảnh.
- Revoke object URL khi thay/xóa ảnh hoặc unmount; dùng `AbortController` cho request có thể hủy.
- Trước bàn giao, chạy format check, ESLint, TypeScript check, Vitest và Vite production build.
