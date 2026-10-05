from pathlib import Path

from src.corpus_factory.ingestion.document import Document


def process_file(file_path: Path) -> Document:
    source_type = file_path.suffix.lower().lstrip(".")

    return Document(
        source_path=str(file_path),
        source_type=source_type,
        raw_text=None,
    )