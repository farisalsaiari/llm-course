from paths import PROCESSED_DIR
from src.corpus_factory.preprocessing.deduplication import text_sha256


FILTERED_DIR = PROCESSED_DIR / "filtered"
DEDUPED_DIR = PROCESSED_DIR / "deduplicated"


if __name__ == "__main__":
    seen_hashes = set()

    for batch_dir in sorted(
        path
        for path in FILTERED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = DEDUPED_DIR / batch_dir.name

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

            digest = text_sha256(text)

            if digest in seen_hashes:
                print(
                    f"DUPLICATE: {source_file.name}"
                )
                continue

            seen_hashes.add(digest)

            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"UNIQUE: {source_file.name}"
                f" -> {output_path}"
            )