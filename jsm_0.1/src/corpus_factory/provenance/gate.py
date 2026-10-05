import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from paths import PROVENANCE_CATALOG_DIR


@dataclass(frozen=True)
class RightsDecision:
    allowed: bool
    status: str
    reason: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def _verify_manifest(manifest_path: Path) -> bool:
    checksum_path = manifest_path.with_suffix(
        manifest_path.suffix + ".sha256"
    )

    if not checksum_path.is_file():
        return False

    expected = (
        checksum_path
        .read_text(encoding="utf-8")
        .strip()
        .split()[0]
    )

    actual = _sha256_file(manifest_path)

    return expected == actual


def find_latest_provenance_decision(
    batch_id: str,
) -> dict | None:

    if not PROVENANCE_CATALOG_DIR.exists():
        return None

    decisions = []

    for manifest_path in PROVENANCE_CATALOG_DIR.glob(
        "*/manifest.json"
    ):
        if not _verify_manifest(manifest_path):
            continue

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        if manifest.get("batch_id") == batch_id:
            decisions.append(manifest)

    if not decisions:
        return None

    decisions.sort(
        key=lambda item: item.get("created_at", "")
    )

    return decisions[-1]


def evaluate_training_rights(
    source_manifest: dict,
    batch_id: str,
) -> RightsDecision:

    provenance = find_latest_provenance_decision(
        batch_id
    )

    # Explicit provenance decision takes priority
    if provenance is not None:
        training_use = provenance.get(
            "training_use",
            "review_required",
        )

        basis = provenance.get(
            "basis",
            "unspecified",
        )

        if training_use == "allowed":
            return RightsDecision(
                allowed=True,
                status="allowed",
                reason=f"approved by provenance: {basis}",
            )

        if training_use == "denied":
            return RightsDecision(
                allowed=False,
                status="denied",
                reason=f"denied by provenance: {basis}",
            )

        return RightsDecision(
            allowed=False,
            status="review_required",
            reason=f"provenance review required: {basis}",
        )

    # No provenance decision yet
    license_info = source_manifest.get(
        "license",
        {}
    )

    training_use = license_info.get(
        "training_use",
        "review_required",
    )

    return RightsDecision(
        allowed=False,
        status=training_use,
        reason=f"training use status: {training_use}",
    )