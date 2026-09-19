---
paths:
  - "**/tests/**/*.py"
  - "tests/**/*.py"
  - "frontend/**/*.test.ts"
  - "frontend/**/*.test.tsx"
  - "frontend/tests/**/*.{ts,tsx}"
---

# Quy tắc kiểm thử

- Tên test theo `test_<unit>_<scenario>_<expected>`.
- Reading được assert bằng exact string; không ép kiểu số.
- Test độc lập với thứ tự chạy, network thật và clock thật trừ khi được đánh dấu integration rõ ràng.
- Mock ở boundary, không mock chi tiết nội bộ của đơn vị đang test.
- Bug fix phải bổ sung regression test thể hiện hành vi lỗi cũ.
- Test pipeline phải phủ leading zero, ba kiểu thập phân và các trạng thái không chắc chắn.
- Test luồng mặc định phải xác nhận chỉ có một lần recognizer. Test fallback phải xác nhận quality gate, tối đa một retry và bất đồng kết quả chuyển thành `review_required`.
- Test performance phải warm up, batch size 1 và đồng bộ CUDA khi đo.
- Frontend dùng Vitest + React Testing Library; test qua accessible role/text và hành vi người dùng, không bám DOM structure nội bộ.
- API client được mock ở network boundary; contract test phải phát hiện OpenAPI/TypeScript drift.
