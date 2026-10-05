import json
from pathlib import Path

from paths import PROCESSED_DIR, TRAINING_DATA_DIR
from src.dataset.builder import choose_split


DEDUPED_DIR = PROCESSED_DIR / "deduplicated"
DATASET_DIR = TRAINING_DATA_DIR / "dataset"


if __name__ == "__main__":
    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_files = {
        "train": DATASET_DIR / "train.jsonl",
        "validation": DATASET_DIR / "validation.jsonl",
        "test": DATASET_DIR / "test.jsonl",
    }

    handles = {
        split: path.open(
            "w",
            encoding="utf-8",
        )
        for split, path in output_files.items()
    }

    try:
        for batch_dir in sorted(
            path
            for path in DEDUPED_DIR.iterdir()
            if path.is_dir()
        ):
            for source_file in sorted(
                batch_dir.glob("*.txt")
            ):
                document_id = source_file.stem

                text = source_file.read_text(
                    encoding="utf-8"
                )

                split = choose_split(
                    document_id
                )

                record = {
                    "document_id": document_id,
                    "batch_id": batch_dir.name,
                    "text": text,
                }

                handles[split].write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                print(
                    f"{split.upper()}: "
                    f"{document_id}"
                )

    finally:
        for handle in handles.values():
            handle.close()