from datetime import datetime, timezone
from pathlib import Path
import hashlib
from paths import BATCHES_DIR
import json

def create_batch() -> Path:
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    batch_dir = BATCHES_DIR / batch_id
    objects_dir = batch_dir / "objects"

    objects_dir.mkdir(parents=True, exist_ok=False)

    return batch_dir



def acquire_file(
    source_file: Path,
    batch_dir: Path,
    sequence: int,
) -> dict:

    destination = (
        batch_dir
        / "objects"
        / f"{sequence:06d}-{source_file.name}"
    )

    sha256 = hashlib.sha256()
    size = 0

    with open(source_file, "rb") as src, open(destination, "xb") as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)
            sha256.update(chunk)
            size += len(chunk)

    return {
        "sequence": sequence,
        "original_name": source_file.name,
        "stored_name": destination.name,
        "size_bytes": size,
        "sha256": sha256.hexdigest(),
    }






def write_source_manifest(
    batch_dir: Path,
    source_info: dict,
    files: list[dict],
) -> Path:

    manifest = {
        "source": source_info,
        "files": files,
    }

    manifest_path = batch_dir / "source.json"

    with open(manifest_path, "x", encoding="utf-8") as file:
        json.dump(
            manifest,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return manifest_path



def write_manifest_checksum(manifest_path: Path) -> Path:
    sha256 = hashlib.sha256()

    with open(manifest_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    checksum_path = manifest_path.with_suffix(
        manifest_path.suffix + ".sha256"
    )

    checksum_path.write_text(
        sha256.hexdigest(),
        encoding="utf-8",
    )

    return checksum_path


def acquire_batch(
    source_files: list[Path],
    source_info: dict,
) -> Path:

    batch_dir = create_batch()

    files_metadata = []

    for sequence, source_file in enumerate(source_files, start=1):
        metadata = acquire_file(
            source_file=source_file,
            batch_dir=batch_dir,
            sequence=sequence,
        )
        files_metadata.append(metadata)

    manifest_path = write_source_manifest(
        batch_dir=batch_dir,
        source_info=source_info,
        files=files_metadata,
    )

    write_manifest_checksum(manifest_path)

    return batch_dir