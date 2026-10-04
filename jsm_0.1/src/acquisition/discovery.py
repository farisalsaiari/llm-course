import json
from pathlib import Path


def existing_fingerprints(
    batches_dir: Path,
) -> set[tuple[str, tuple[str, ...]]]:
    fingerprints = set()

    if not batches_dir.exists():
        return fingerprints

    for batch_dir in batches_dir.iterdir():
        manifest_path = batch_dir / "source.json"

        if not manifest_path.is_file():
            continue

        try:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            continue

        source_name = manifest.get("source", {}).get("platform")

        hashes = tuple(
            sorted(
                artifact["sha256"]
                for artifact in manifest.get("artifacts", [])
                if "sha256" in artifact
            )
        )

        if source_name and hashes:
            fingerprints.add(
                (
                    source_name,
                    hashes,
                )
            )

    return fingerprints