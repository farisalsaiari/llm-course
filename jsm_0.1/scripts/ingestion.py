import json
from pathlib import Path

from paths import (
    BATCHES_DIR,
    INSPECTIONS_CATALOG_DIR,
)

from src.ingestion.ingest import (
    ingest_artifact,
    write_ingestion_manifest,
)
from src.provenance.gate import evaluate_training_rights


def load_latest_inspections() -> dict[str, dict]:
    latest = {}

    for manifest_path in sorted(
        INSPECTIONS_CATALOG_DIR.glob("*/manifest.json")
    ):
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        incoming_batch = manifest.get("incoming_batch")

        if isinstance(incoming_batch, dict):
            batch_id = incoming_batch.get("batch_id")

        elif isinstance(incoming_batch, str):
            batch_id = Path(incoming_batch).name

        else:
            batch_id = manifest.get("batch_id")

        if batch_id:
            latest[batch_id] = manifest

    return latest

if __name__ == "__main__":
    inspections = load_latest_inspections()

    for batch_id, inspection in inspections.items():
        batch_dir = BATCHES_DIR / batch_id
        source_path = batch_dir / "source.json"

        if not source_path.is_file():
            print(f"SKIP: {batch_id} — source manifest missing")
            continue

        source_manifest = json.loads(
            source_path.read_text(encoding="utf-8")
        )

        rights = evaluate_training_rights(
            source_manifest,
            batch_id,
        )

        if not rights.allowed:
            print(f"BLOCK: {batch_id} — {rights.reason}")
            continue

        documents = []

        for artifact in inspection.get("artifacts", []):
            decision = artifact.get("decision")

            if decision != "accepted_for_ingestion":
                continue

            artifact_id = artifact["artifact_id"]
            relative_path = artifact["stored_relative_path"]
            sha256 = artifact["sha256"]

            incoming_file = batch_dir / relative_path

            document = ingest_artifact(
                source_path=incoming_file,
                batch_id=batch_id,
                artifact_id=artifact_id,
                sha256=sha256,
            )

            documents.append(document)

        if not documents:
            print(f"SKIP: {batch_id} — no accepted artifacts")
            continue

        manifest_path = write_ingestion_manifest(
            batch_id=batch_id,
            documents=documents,
        )

        print(
            f"INGESTED: {batch_id} "
            f"({len(documents)} documents)"
        )
        print(f"  manifest: {manifest_path}")