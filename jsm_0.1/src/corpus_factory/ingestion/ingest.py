import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from paths import RAW_STORAGE_DIR


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ingest_artifact(
    source_path: Path,
    batch_id: str,
    artifact_id: str,
    sha256: str,
) -> dict:
    document_id = f"doc_{uuid.uuid4().hex}"

    batch_dir = RAW_STORAGE_DIR / batch_id
    objects_dir = batch_dir / "objects"

    objects_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        objects_dir
        / f"{document_id}-{source_path.name}"
    )

    shutil.copy2(
        source_path,
        destination,
    )

    return {
        "document_id": document_id,
        "batch_id": batch_id,
        "artifact_id": artifact_id,
        "sha256": sha256,
        "source_path": source_path.as_posix(),
        "stored_relative_path": (
            Path("objects") / destination.name
        ).as_posix(),
    }


def write_ingestion_manifest(
    batch_id: str,
    documents: list[dict],
) -> Path:
    batch_dir = RAW_STORAGE_DIR / batch_id

    manifest = {
        "schema_version": "1.0.0",
        "record_type": "ingestion_manifest",
        "batch_id": batch_id,
        "created_at": utc_now(),
        "documents": documents,
        "summary": {
            "documents": len(documents),
        },
        "next_stage": "extraction",
    }

    manifest_path = batch_dir / "manifest.json"

    encoded = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    manifest_path.write_bytes(encoded)

    digest = hashlib.sha256(encoded).hexdigest()

    checksum_path = batch_dir / "manifest.json.sha256"

    checksum_path.write_text(
        f"{digest}  manifest.json\n",
        encoding="utf-8",
    )

    return manifest_path