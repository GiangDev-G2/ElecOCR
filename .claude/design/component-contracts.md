# Hợp đồng component ElecOCR

## Header

- Hiển thị ElecOCR, readiness, model version, trợ giúp và theme.
- Readiness có icon/dot và text, không chỉ màu.
- Không có navigation giả hoặc model selector trong MVP.

## Upload zone

- Nhận đúng một JPG/PNG/WebP, tối đa theo cấu hình API.
- Có empty, drag-over, invalid, ready và disabled state.
- Lỗi file hiển thị nội tuyến.

## Image stage

- Dùng `object-fit: contain`; không crop preview.
- Chỉ vẽ polygon thật do backend trả về.
- Toolbar không che ảnh và có accessible labels.

## Result hero

- Reading là chuỗi tabular numerals, giữ leading zero.
- Hiển thị status + confidence bằng text, icon và màu.
- `unreadable`/`error` không hiển thị reading phỏng đoán như kết quả chính.

## Recognition crop preview

- Hiển thị crop đủ lớn để kiểm tra từng chữ số.
- Mặc định chỉ hiện crop RGB của lần nhận dạng chính.
- Chỉ hiện ảnh rectified/enhanced khi fallback thực sự đã chạy.
- Nêu cách chuẩn hóa dấu phẩy/chữ số đỏ khi có bằng chứng.

## Technical details

- Đóng mặc định.
- Có meter type, decimal style, latency, model version, request ID và warning.
- Không lộ stack trace, local path hoặc secret.

## Responsive order

```text
ảnh → hành động → kết quả → crop nhận dạng/fallback nếu có → chi tiết
```

Thứ tự này không thay đổi ở viewport nhỏ.
