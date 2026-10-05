import json
from pathlib import Path

from paths import RAW_STORAGE_DIR, EXTRACTED_DIR
from src.corpus_factory.extraction.extractor import extract_text


if __name__ == "__main__":
    batch_dirs = sorted(
        path
        for path in RAW_STORAGE_DIR.iterdir()
        if path.is_dir()
    )

    for batch_dir in batch_dirs:
        manifest_path = batch_dir / "manifest.json"

        if not manifest_path.is_file():
            continue

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        output_batch_dir = EXTRACTED_DIR / batch_dir.name
        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for document in manifest.get("documents", []):
            document_id = document["document_id"]

            source_file = (
                batch_dir
                / document["stored_relative_path"]
            )

            try:
                text = extract_text(source_file)

            except ValueError as error:
                print(
                    f"SKIP: {source_file.name} — {error}"
                )
                continue

            output_path = (
                output_batch_dir
                / f"{document_id}.txt"
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"EXTRACTED: {source_file.name}"
                f" -> {output_path.name}"
            )