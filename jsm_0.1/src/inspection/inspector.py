import json
from pathlib import Path

from src.inspection.checks import (
    check_manifest,
    check_integrity,
    inspect_artifact,
)
from src.inspection.result import (
    CheckResult,
    ArtifactInspectionResult,
    InspectionResult,
)


def inspect_batch(batch_dir: Path) -> InspectionResult:
    batch_checks = []
    batch_errors = []

    # -------------------------------------------------
    # Batch-level checks
    # -------------------------------------------------

    batch_check_functions = [
        ("manifest", check_manifest),
        ("integrity", check_integrity),
    ]

    for name, check_function in batch_check_functions:
        result = check_function(batch_dir)

        batch_checks.append(
            CheckResult(
                name=name,
                passed=result.passed,
                errors=result.errors,
            )
        )

        batch_errors.extend(result.errors)

    # -------------------------------------------------
    # Load manifest
    # -------------------------------------------------

    manifest_path = batch_dir / "source.json"

    try:
        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )

    except (OSError, json.JSONDecodeError):
        return InspectionResult(
            passed=False,
            checks=batch_checks,
            artifacts=[],
            errors=batch_errors,
        )

    # -------------------------------------------------
    # Artifact-level inspection
    # -------------------------------------------------

    artifact_results: list[ArtifactInspectionResult] = []

    for artifact in manifest.get("artifacts", []):
        artifact_id = artifact.get(
            "artifact_id",
            "unknown",
        )

        filename = artifact.get(
            "original_filename",
            "unknown",
        )

        relative_path = artifact.get(
            "stored_relative_path"
        )

        # Cannot inspect without storage path
        if not relative_path:
            artifact_results.append(
                ArtifactInspectionResult(
                    artifact_id=artifact_id,
                    filename=filename,
                    passed=False,
                    checks=[],
                    errors=[
                        "stored_relative_path is missing"
                    ],
                )
            )
            continue

        file_path = batch_dir / relative_path

        artifact_result = inspect_artifact(
            file_path=file_path,
            artifact=artifact,
        )

        artifact_results.append(
            artifact_result
        )

    # -------------------------------------------------
    # Final batch result
    # -------------------------------------------------

    batch_structure_passed = (
        len(batch_errors) == 0
    )

    artifacts_passed = all(
        artifact.passed
        for artifact in artifact_results
    )

    passed = (
        batch_structure_passed
        and artifacts_passed
    )

    return InspectionResult(
        passed=passed,
        checks=batch_checks,
        artifacts=artifact_results,
        errors=batch_errors,
    )