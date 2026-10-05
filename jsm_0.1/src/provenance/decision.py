import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from paths import PROVENANCE_CATALOG_DIR


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_rights_decision(
    batch_id: str,
    training_use: str,
    basis: str,
) -> Path:

    if training_use not in {
        "allowed",
        "denied",
        "review_required",
    }:
        raise ValueError(
            f"Invalid training_use: {training_use}"
        )

    now = datetime.now(timezone.utc)

    decision_id = (
        f"provenance_{now:%Y%m%dT%H%M%SZ}_"
        f"{uuid.uuid4().hex[:8]}"
    )

    decision_dir = (
        PROVENANCE_CATALOG_DIR / decision_id
    )

    decision_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    manifest = {
        "schema_version": "1.0.0",
        "record_type": "provenance_decision",
        "decision_id": decision_id,
        "batch_id": batch_id,
        "created_at": utc_now(),
        "training_use": training_use,
        "basis": basis,
        "review_method": "manual",
        "next_stage": (
            "ingestion"
            if training_use == "allowed"
            else None
        ),
    }

    manifest_path = decision_dir / "manifest.json"

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

    checksum_path = (
        decision_dir / "manifest.json.sha256"
    )

    checksum_path.write_text(
        f"{digest}  manifest.json\n",
        encoding="utf-8",
    )

    return manifest_path