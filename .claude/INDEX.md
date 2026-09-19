# Cấu trúc Claude Code của ElecOCR

```text
.claude/
├── rules/                       Chỉ dẫn tự nạp, có thể giới hạn theo đường dẫn
├── agents/                      Subagent chuyên biệt cho backend, AI, UI và review
├── skills/                      Workflow/kiến thức nạp theo nhu cầu
├── design/                      Design handoff và token máy đọc được
├── templates/                   Mẫu kế hoạch, báo cáo thí nghiệm và review
└── settings.json                Cấu hình dự án tối thiểu, không chứa secret
```

`CLAUDE.md` ở gốc là entrypoint luôn được nạp. Nội dung chi tiết không được sao chép vào entrypoint; agent đọc rule/skill/tài liệu liên quan theo nhiệm vụ để tiết kiệm context.

## Phân loại nội dung

- Quy tắc luôn đúng hoặc theo đường dẫn: đặt trong `rules/`.
- Quy trình lặp lại có thể gọi bằng `/skill-name`: đặt trong `skills/`.
- Vai trò cần context tách biệt: đặt trong `agents/`.
- Quyết định thiết kế và token: đặt trong `design/`.
- Định dạng đầu ra lặp lại: đặt trong `templates/`.
- Đặc tả sản phẩm đầy đủ vẫn nằm trong `docs/` và là nguồn sự thật.

Không đưa credential, đường dẫn máy cá nhân hoặc quyền tự động nguy hiểm vào `.claude/settings.json`.

