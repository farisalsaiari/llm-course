from paths import PROCESSED_DIR
from src.corpus_factory.preprocessing.normalization import normalize_text


CLEANED_DIR = PROCESSED_DIR / "cleaned"
NORMALIZED_DIR = PROCESSED_DIR / "normalized"


if __name__ == "__main__":
    for batch_dir in sorted(
        path
        for path in CLEANED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = NORMALIZED_DIR / batch_dir.name

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

            normalized = normalize_text(text)

            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                normalized,
                encoding="utf-8",
            )

            print(
                f"NORMALIZED: {source_file.name}"
                f" -> {output_path}"
            )