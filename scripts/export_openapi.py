"""Export the FastAPI OpenAPI schema for frontend type generation."""

import json
from pathlib import Path

from backend.app.main import app


def main() -> None:
    output_path = Path("artifacts/openapi.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(app.openapi(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
