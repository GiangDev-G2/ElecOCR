# Hướng dẫn dành cho agent

## 1. Mục tiêu

Xây dựng ElecOCR theo đặc tả trong `docs/`: một ứng dụng OCR đồng hồ điện chạy local, có frontend React + TypeScript và backend FastAPI/core AI bằng Python tách riêng. Mục tiêu chính là độ chính xác end-to-end lớn hơn 95% trên tập kiểm thử đại diện.

## 2. Thứ tự nguồn sự thật

Khi có mâu thuẫn, áp dụng thứ tự ưu tiên sau:

1. Yêu cầu mới nhất được người dùng xác nhận.
2. `docs/02-YEU-CAU-VA-NGHIEM-THU.md`.
3. Các bản ghi quyết định trong `docs/08-RUI-RO-VA-QUYET-DINH.md`.
4. Quy ước mã nguồn trong `docs/09-QUY-UOC-MA-NGUON.md`.
5. Kiến trúc và kế hoạch còn lại trong `docs/`.
6. Mã nguồn hiện có.

Không tự ý thay đổi một quyết định đã chốt. Nếu thay đổi là cần thiết, cập nhật bản ghi quyết định, nêu lý do, ảnh hưởng và phương án chuyển đổi.

## 3. Quy tắc bất biến

- Giá trị đọc được phải là `string`; không chuyển thành `float` vì sẽ mất số `0` ở đầu và có thể gây sai số.
- Chuẩn hóa dấu thập phân đầu ra thành dấu chấm, nhưng lưu bằng chứng thô để gỡ lỗi.
- Không đoán phần thập phân khi bằng chứng mâu thuẫn; trả `review_required`.
- Một ảnh chỉ có một đồng hồ, nhưng vùng hiển thị phải được tự động phát hiện.
- Không âm thầm trả kết quả khi model không chắc chắn. Luôn áp dụng cơ chế `ok`, `review_required`, `unreadable` hoặc `error`.
- Không đưa dataset, ảnh người dùng, checkpoint, log chứa ảnh hay khóa bí mật vào Git.
- Không dùng tập test để chọn siêu tham số, ngưỡng confidence hoặc quy tắc hậu xử lý.
- Mọi phép đo độ chính xác phải báo cáo exact-match toàn chuỗi, không chỉ accuracy từng ký tự.
- Báo cáo riêng theo đồng hồ cơ, đồng hồ điện tử và ba kiểu thập phân; không để điểm tổng che giấu nhóm yếu.
- Luồng suy luận mặc định phải tối giản: canonicalize ảnh → phát hiện vùng hiển thị → crop có padding → chuẩn hóa input recognizer → một lần nhận dạng → chuẩn hóa/kiểm tra → quyết định confidence và trạng thái.
- Hiệu chỉnh phối cảnh hoặc tăng tương phản chỉ là fallback có quality gate. Mỗi ảnh chỉ được chọn tối đa một fallback và retry recognizer một lần; không chạy song song các biến thể RGB/CLAHE/nhị phân theo mặc định.

## 4. Cấu trúc đích

```text
backend/                 FastAPI và toàn bộ AI
backend/ai/              pipeline suy luận, training, đánh giá, công cụ dữ liệu
frontend/                React + TypeScript/Vite, chỉ gọi API công khai của backend
configs/                 cấu hình có phiên bản; không chứa secret
data/                    dữ liệu local, bị loại khỏi Git
models/                  checkpoint local, bị loại khỏi Git
backend/tests/           unit, integration, contract và smoke test backend/AI
docs/                    đặc tả và quyết định
artifacts/               báo cáo đánh giá sinh tự động, bị loại khỏi Git khi lớn
```

Backend không được import frontend. Frontend không được import trực tiếp pipeline model; frontend chỉ giao tiếp qua HTTP để bảo đảm ranh giới triển khai.

## 5. Quy ước triển khai

- Trước khi viết hoặc review mã Python/TypeScript/React, bắt buộc đọc và tuân thủ `docs/09-QUY-UOC-MA-NGUON.md`.
- Python 3.12 là phiên bản bắt buộc; xác nhận tương thích CUDA/PyTorch trước khi khóa dependency.
- Frontend dùng React + TypeScript strict, Vite và npm; khóa Node.js LTS khi tạo skeleton và commit `package-lock.json`.
- Dùng type hint cho API công khai, `pathlib` cho đường dẫn và cấu hình thay vì hằng số rải rác.
- Định danh, tên hàm và mã nguồn dùng tiếng Anh; tài liệu, chú thích nghiệp vụ và nội dung UI dùng tiếng Việt.
- Cố định seed và ghi lại phiên bản dependency, dataset, cấu hình, commit và checkpoint cho mỗi thí nghiệm.
- Mỗi thay đổi hành vi phải có test tương ứng. Ưu tiên unit test cho chuẩn hóa chuỗi, dấu thập phân và trạng thái confidence.
- API phải kiểm tra MIME, kích thước, khả năng giải mã ảnh và giới hạn tài nguyên trước khi suy luận.
- Mặc định không lưu ảnh tải lên. Chế độ debug chỉ được bật rõ ràng và phải che/giới hạn dữ liệu lưu.
- Dependency mới phải được kiểm tra giấy phép. Ultralytics dùng AGPL-3.0 trong nhánh học thuật; không tuyên bố sẵn sàng thương mại nếu chưa xử lý giấy phép.
- Không tạo quy ước tên riêng cho từng module. Từ điển miền, tên schema, ảnh/tensor và confidence phải dùng đúng chuẩn chung.
- Trước khi bàn giao thay đổi mã Python, chạy `ruff format --check .`, `ruff check .`, `mypy backend` và `pytest`. Khi thay đổi frontend, chạy các script `format:check`, `lint`, `typecheck`, `test` và `build` trong `frontend/package.json`; ghi rõ công cụ nào chưa thể chạy cùng lý do.

## 6. Quy trình cho mỗi nhiệm vụ

1. Đọc tài liệu liên quan và xác định tiêu chí hoàn thành.
2. Thực hiện thay đổi nhỏ nhất đáp ứng tiêu chí.
3. Chạy test liên quan; với thay đổi pipeline phải chạy ít nhất một smoke test end-to-end.
4. Cập nhật tài liệu, cấu hình mẫu và changelog quyết định nếu hợp đồng bị thay đổi.
5. Báo cáo lệnh đã chạy, kết quả, giới hạn còn lại và tệp đã thay đổi.

Một nhiệm vụ chưa hoàn thành nếu chỉ có mã nhưng không có kiểm thử hoặc làm thay đổi hợp đồng mà chưa cập nhật tài liệu.
