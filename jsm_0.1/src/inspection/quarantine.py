import json
from datetime import datetime, timezone
from pathlib import Path

from paths import QUARANTINE_DIR
from src.inspection.result import InspectionResult


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def quarantine_batch(
    batch_dir: Path,
    result: InspectionResult,
) -> Path:
    quarantine_dir = QUARANTINE_DIR / batch_dir.name
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    record_path = quarantine_dir / "quarantine.json"

    if record_path.exists():
        return record_path

    record = {
        "schema_version": "1.0.0",
        "record_type": "quarantine_record",
        "batch_id": batch_dir.name,
        "quarantined_at": utc_now(),
        "source_batch": batch_dir.as_posix(),
        "errors": result.errors,
    }

    with record_path.open("x", encoding="utf-8") as file:
        json.dump(
            record,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return record_path
