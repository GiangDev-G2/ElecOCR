# ElecOCR

ElecOCR là đồ án cá nhân xây dựng hệ thống OCR chỉ số đồng hồ điện từ ảnh. Hệ thống hỗ trợ đồng hồ cơ và đồng hồ điện tử, tự tìm vùng hiển thị, giữ số `0` ở đầu và đọc phần thập phân được biểu diễn bằng dấu chấm, dấu phẩy hoặc chữ số màu đỏ. Frontend dùng React + TypeScript; backend, core AI và training dùng Python.

Trạng thái hiện tại: **đã có skeleton chạy được cho backend, React UI và công cụ dữ liệu; detector/recognizer chưa được huấn luyện**. Bộ tài liệu trong `docs/` là nguồn sự thật cho quá trình triển khai.

Toàn bộ AI, bao gồm suy luận, huấn luyện và đánh giá, nằm trong `backend/ai/`. Frontend là web UI phục vụ tải ảnh và kiểm thử model qua API local.

Pipeline MVP được chốt theo luồng tối giản: canonicalize ảnh → phát hiện vùng hiển thị → crop có padding → chuẩn hóa input → nhận dạng một lần → chuẩn hóa/kiểm tra kết quả → quyết định trạng thái. Hiệu chỉnh phối cảnh hoặc tăng tương phản chỉ là fallback có điều kiện, với tối đa một lần nhận dạng lại.

## Chạy local

Yêu cầu: Python 3.12, Node.js/npm và Windows PowerShell.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
npm.cmd --prefix frontend ci
```

Mở hai terminal từ thư mục dự án:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
npm.cmd --prefix frontend run dev
```

Truy cập `http://127.0.0.1:5173`. Backend hiện kiểm tra ảnh đầu vào nhưng chủ động trả
`MODEL_NOT_READY` cho đến khi có model bundle thật; không sinh kết quả OCR giả.

## Dữ liệu và kiểm tra

```powershell
.\.venv\Scripts\python.exe -m backend.ai.training.data.download_yuva_eb
.\.venv\Scripts\python.exe -m backend.ai.training.data.inspect_dataset data\raw\yuva_eb\extracted\7SegmentImages
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy backend
.\.venv\Scripts\python.exe -m pytest
npm.cmd --prefix frontend run lint
npm.cmd --prefix frontend run typecheck
npm.cmd --prefix frontend run test
npm.cmd --prefix frontend run build
```

## Tài liệu chính

1. [Mục lục và cách sử dụng](docs/00-MUC-LUC.md)
2. [Tổng quan và phạm vi](docs/01-TONG-QUAN-VA-PHAM-VI.md)
3. [Yêu cầu và tiêu chí nghiệm thu](docs/02-YEU-CAU-VA-NGHIEM-THU.md)
4. [Kiến trúc hệ thống](docs/03-KIEN-TRUC-HE-THONG.md)
5. [Chiến lược dữ liệu](docs/04-DU-LIEU.md)
6. [Huấn luyện và đánh giá](docs/05-HUAN-LUYEN-VA-DANH-GIA.md)
7. [Hợp đồng API và giao diện](docs/06-API-VA-UI.md)
8. [Kế hoạch thực hiện 14 ngày](docs/07-KE-HOACH-14-NGAY.md)
9. [Rủi ro, quyết định và câu hỏi mở](docs/08-RUI-RO-VA-QUYET-DINH.md)
10. [Đặc tả UI/UX web](docs/ui-ux.md)
11. [Quy ước mã nguồn và Clean Code](docs/09-QUY-UOC-MA-NGUON.md)

Các agent làm việc trên kho mã phải đọc [AGENTS.md](AGENTS.md) trước khi thay đổi dự án.

Claude Code dùng [CLAUDE.md](CLAUDE.md) làm entrypoint và cấu trúc dự án trong [.claude/INDEX.md](.claude/INDEX.md).
