from pathlib import Path

from paths import EXTRACTED_DIR, PROCESSED_DIR
from src.preprocessing.cleaning import clean_text


CLEANED_DIR = PROCESSED_DIR / "cleaned"


if __name__ == "__main__":
    for batch_dir in sorted(
        path
        for path in EXTRACTED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = CLEANED_DIR / batch_dir.name

        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        for source_file in sorted(
            batch_dir.glob("*.txt")
        ):
            text = source_file.read_text(
                encoding="utf-8"
            )

            cleaned = clean_text(text)

            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                cleaned,
                encoding="utf-8",
            )

            print(
                f"CLEANED: {source_file.name}"
                f" -> {output_path}"
            )