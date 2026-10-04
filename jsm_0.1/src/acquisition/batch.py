from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import secrets
from src.acquisition.hashing import sha256_file
from paths import BATCHES_DIR
from src.acquisition.intake import IntakeSource


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_source_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_-]+", "-", name)

    return name.strip("-") or "unattributed"


def create_batch(source_name: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = secrets.token_hex(4)

    safe_name = _safe_source_name(source_name)

    batch_id = f"{safe_name}-{stamp}-{suffix}"

    batch_dir = BATCHES_DIR / batch_id
    objects_dir = batch_dir / "objects"

    objects_dir.mkdir(parents=True, exist_ok=False)

    return batch_dir


def acquire_file(
    source_file: Path,
    batch_dir: Path,
    sequence: int,
    source: IntakeSource,
) -> dict:
    destination = (
        batch_dir
        / "objects"
        / f"{sequence:08d}-{source_file.name}"
    )

    sha256 = hashlib.sha256()
    size_bytes = 0

    with source_file.open("rb") as src, destination.open("xb") as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)
            sha256.update(chunk)
            size_bytes += len(chunk)

    return {
        "artifact_id": f"artifact_{sequence:08d}",
        "original_filename": source_file.name,
        "sha256": sha256.hexdigest(),
        "size_bytes": size_bytes,
        "source_metadata": {
            "origin_folder": source.name,
        },
        "source_url": source.origin.get("source_url"),
        "stored_relative_path": (
            Path("objects") / destination.name
        ).as_posix(),
    }

def write_source_manifest(
    batch_dir: Path,
    source: IntakeSource,
    files: list[dict],
    collected_at: str,
) -> Path:

    total_bytes = sum(file["size_bytes"] for file in files)

    manifest = {
        "schema_version": "1.0.0",
        "record_type": "incoming_source_batch",

        "batch_id": batch_dir.name,

        "collected_at": collected_at,
        "created_at": utc_now(),

        "connector": {
            "contract_version": "0.1.0",
            "name": "local-uploads",
            "version": "1.0.0",
        },

        "source": {
            "platform": source.origin.get(
                "platform",
                source.name,
            ),
            "source_type": source.origin.get(
                "source_type",
                "undeclared_local_files",
            ),
            "source_url": source.origin.get("source_url"),
        },

        "license": {
            "identifier": source.origin.get(
                "license_identifier",
                "unknown",
            ),
            "attribution": source.origin.get("attribution"),
            "status": "review_required",
            "training_use": "review_required",
        },

        "immutability": {
            "append_only": True,
            "never_modify_in_place": True,
        },

        "artifacts": files,

        "summary": {
            "artifacts": len(files),
            "bytes": total_bytes,
        },

        "next_stage": "inspection",
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

    with open(checksum_path, "x", encoding="utf-8") as file:
        file.write(sha256.hexdigest())

    return checksum_path


def acquire_batch(source: IntakeSource) -> Path:
    collected_at = utc_now()

    batch_dir = create_batch(source.name)

    files_metadata = []

    for sequence, source_file in enumerate(
        source.files,
        start=1,
    ):
        metadata = acquire_file(
            source_file=source_file,
            batch_dir=batch_dir,
            sequence=sequence,
            source=source,
        )

        files_metadata.append(metadata)

    manifest_path = write_source_manifest(
        batch_dir=batch_dir,
        source=source,
        files=files_metadata,
        collected_at=collected_at,
    )

    write_manifest_checksum(manifest_path)

    return batch_dir