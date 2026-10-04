from pathlib import Path

from src.ingestion.document import Document
from src.ingestion.readers.txt_reader import read_txt


def process_file(file_path: Path) -> Document:
    if file_path.suffix.lower() == ".txt":
        text = read_txt(file_path)

        return Document(
            source_path=str(file_path),
            source_type="txt",
            raw_text=text,
        )

    raise ValueError(f"Unsupported file type: {file_path.suffix}")