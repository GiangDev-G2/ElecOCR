# Quy tắc chung ElecOCR

- Đọc tài liệu phù hợp trước khi sửa mã; không suy đoán lại yêu cầu đã được chốt.
- Mã nguồn và identifier dùng tiếng Anh; tài liệu và nội dung UI dùng tiếng Việt.
- `reading` luôn là chuỗi và phải giữ leading zero.
- Không đoán kết quả khi confidence hoặc bằng chứng thập phân mâu thuẫn.
- Giữ luồng mặc định tối giản với một detector và một lần recognizer; fallback phải qua quality gate và chỉ được retry một lần.
- Không đưa dataset, ảnh người dùng, checkpoint, secret hoặc log chứa ảnh vào Git.
- Không thay đổi contract API, schema dữ liệu hoặc kiến trúc mà không cập nhật tài liệu liên quan.
- Không tuyên bố đạt accuracy/latency nếu chưa có artifact đo trên split và môi trường xác định.
- Thay đổi hành vi phải có test; bug fix phải có regression test khi có thể.
- Không sửa ngoài phạm vi yêu cầu và phải giữ nguyên thay đổi không liên quan của người dùng.
