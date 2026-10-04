from paths import UPLOADS_DIR, BATCHES_DIR

from src.acquisition.intake import read_uploads
from src.acquisition.batch import acquire_batch
from src.acquisition.discovery import existing_fingerprints
from src.acquisition.hashing import sha256_file


if __name__ == "__main__":
    sources = read_uploads(UPLOADS_DIR)

    if not sources:
        raise ValueError(f"No files found under {UPLOADS_DIR}")

    existing = existing_fingerprints(BATCHES_DIR)

    for source in sources:
        platform = source.origin.get(
            "platform",
            source.name,
        )

        current_hashes = tuple(
            sorted(
                sha256_file(path)
                for path in source.files
            )
        )

        fingerprint = (
            platform,
            current_hashes,
        )

        if fingerprint in existing:
            print(
                f"Skipped already acquired source: "
                f"{source.name}"
            )
            continue

        batch_dir = acquire_batch(source)

        print(
            f"Acquired: {source.name} -> "
            f"{batch_dir.name}"
        )