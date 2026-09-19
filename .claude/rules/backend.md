---
paths:
  - "backend/**/*.py"
---

# Quy tắc backend

- Đọc `docs/03-KIEN-TRUC-HE-THONG.md`, `docs/06-API-VA-UI.md` và `docs/09-QUY-UOC-MA-NGUON.md` trước thay đổi đáng kể.
- FastAPI route chỉ validate/parse transport, gọi application service và map response.
- Không import OpenCV, PyTorch hoặc logic hậu xử lý reading trong route.
- Schema public dùng Pydantic và JSON field `snake_case`.
- Map domain exception sang HTTP error tại API boundary; không trả stack trace.
- Dùng structured logging có `request_id`; không log ảnh, base64 hoặc reading đầy đủ.
- Dependency/model/config được tạo ở composition root hoặc lifespan rồi inject.
- `GET /ready` chỉ trả ready khi model bundle đã load và self-check thành công.
- OpenAPI là contract cho transport types phía React; thay đổi schema phải có contract test và sinh lại frontend types.
- CORS chỉ cho phép origin frontend local được cấu hình; không dùng wildcard khi có credential.
- API test phải kiểm tra cả happy path, ảnh lỗi, model chưa sẵn sàng và status nghiệp vụ.
