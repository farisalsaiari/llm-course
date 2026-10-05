import json

from paths import (
    BATCHES_DIR,
    INSPECTIONS_CATALOG_DIR,
)
from src.provenance.gate import evaluate_training_rights


def load_inspection_manifests() -> list[dict]:
    manifests = []

    if not INSPECTIONS_CATALOG_DIR.exists():
        return manifests

    for manifest_path in sorted(
        INSPECTIONS_CATALOG_DIR.glob("*/manifest.json")
    ):
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        manifests.append(manifest)

    return manifests


def get_batch_id(inspection: dict) -> str | None:
    incoming_batch = inspection.get("incoming_batch", {})

    if isinstance(incoming_batch, dict):
        batch_id = incoming_batch.get("batch_id")

        if batch_id:
            return batch_id

    return inspection.get("batch_id")


if __name__ == "__main__":
    inspections = load_inspection_manifests()

    print(f"Inspection manifests: {len(inspections)}")

    for inspection in inspections:
        batch_id = get_batch_id(inspection)

        if not batch_id:
            print("SKIP: inspection has no batch_id")
            continue

        batch_dir = BATCHES_DIR / batch_id
        source_path = batch_dir / "source.json"

        if not source_path.is_file():
            print(f"SKIP: {batch_id} — source.json missing")
            continue

        source_manifest = json.loads(
            source_path.read_text(encoding="utf-8")
        )

        decision = evaluate_training_rights(
            source_manifest,
            batch_id,
        )

        if decision.allowed:
            print(
                f"ALLOW: {batch_id} — {decision.reason}"
            )
        else:
            print(
                f"BLOCK: {batch_id} — {decision.reason}"
            )