from paths import PROCESSED_DIR
from src.corpus_factory.preprocessing.filtering import filter_text


NORMALIZED_DIR = PROCESSED_DIR / "normalized"
FILTERED_DIR = PROCESSED_DIR / "filtered"


if __name__ == "__main__":
    for batch_dir in sorted(
        path
        for path in NORMALIZED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = FILTERED_DIR / batch_dir.name

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

            result = filter_text(text)

            if not result.accepted:
                print(
                    f"FILTERED OUT: {source_file.name}"
                    f" — {result.reason}"
                )
                continue

            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"ACCEPTED: {source_file.name}"
                f" -> {output_path}"
            )