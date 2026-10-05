from pathlib import Path


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix in {".txt", ".md"}:
        return file_path.read_text(
            encoding="utf-8"
        )

    raise ValueError(
        f"Unsupported extraction type: {suffix}"
    )