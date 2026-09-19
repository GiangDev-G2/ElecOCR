# ElecOCR design handoff

Nguồn sự thật đầy đủ là `docs/ui-ux.md`. Thư mục này cung cấp bản giao tiếp ngắn và token máy đọc được để agent triển khai giao diện React + TypeScript nhất quán.

## Phong cách

`Calm · Glass · Precision`

- Nền xanh-xám/navy đặc, không ảnh nền hoặc gradient trang trí.
- Glass dùng cho phân lớp, không làm giảm độ đọc.
- Border sáng mảnh quan trọng hơn shadow.
- Reading và trạng thái là điểm nhìn chính sau khi OCR.
- Một primary action tại mỗi thời điểm.
- Không mô phỏng cửa sổ desktop bên trong trình duyệt.

## Tệp

- `tokens.json`: màu, spacing, radius, shadow và breakpoint dùng chung.
- `component-contracts.md`: hợp đồng thị giác/hành vi của các component chính.
- `docs/ui-ux.md`: layout, state, accessibility và tiêu chí nghiệm thu đầy đủ.

Khi có mâu thuẫn, `docs/ui-ux.md` ưu tiên hơn tệp trong thư mục này. Thay đổi token phải cập nhật cả hai nơi trong cùng một thay đổi.
