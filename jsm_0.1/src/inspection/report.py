import json
from datetime import datetime, timezone
from pathlib import Path

from src.inspection.result import InspectionResult


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_inspection_report(
    batch_dir: Path,
    result: InspectionResult,
) -> Path:

    status = "PASS" if result.passed else "QUARANTINE"

    report = {
        "schema_version": "1.0.0",
        "record_type": "inspection_report",

        "batch_id": batch_dir.name,

        "status": status,
        "checked_at": utc_now(),
        "inspector_version": "1.0.0",

        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "errors": check.errors,
            }
            for check in result.checks
        ],

        "errors": result.errors,

        "next_stage": (
            "ingestion"
            if status == "PASS"
            else "quarantine"
        ),
    }

    report_path = batch_dir / "inspection.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return report_path