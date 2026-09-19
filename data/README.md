# Dữ liệu local

Thư mục `data/` chứa dữ liệu chỉ dùng trên máy local. Các thư mục `raw/`, `interim/` và
`processed/` bị loại khỏi Git. Metadata nguồn và giấy phép nằm tại `configs/datasets.yaml`.

## Dữ liệu hiện có

- `raw/yuva_eb/7SegmentImages.zip`: YUVA EB subset do MathWorks phân phối.
- `raw/yuva_eb/extracted/7SegmentImages/`: 119 ảnh JPG đồng hồ điện tử bảy đoạn.

Không đổi nội dung trong `raw/`. Mọi chuyển đổi phải ghi sang `interim/` hoặc `processed/` và
lưu manifest có checksum.

## Dữ liệu cần xin quyền

- UFPR-AMR: gửi yêu cầu bằng email trường theo hướng dẫn của VRI Lab.
- Copel-AMR: cần thỏa thuận do đại diện có thẩm quyền của cơ sở đào tạo ký.

Không được đưa hai bộ dữ liệu hạn chế này lên Git hoặc phân phối lại.
