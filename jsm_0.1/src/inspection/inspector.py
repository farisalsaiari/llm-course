"""Batch trust gate and artifact-level orchestration."""
from copy import deepcopy
from pathlib import Path

from src.inspection.checks import (
    apply_malware_result, inspect_artifact, read_manifest, scan_malware_batch,
)
from src.inspection.config import load_inspection_config, validate_inspection_config
from src.inspection.result import CheckResult, InspectionDecision as D, InspectionResult


def inspect_batch(batch_dir: Path, policy: dict | None = None) -> InspectionResult:
    policy = deepcopy(load_inspection_config() if policy is None else validate_inspection_config(policy))
    batch_dir = Path(batch_dir).absolute()
    try:
        manifest, digest = read_manifest(batch_dir, policy)
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        return InspectionResult(batch_dir.name, None, policy,
                                checks=(CheckResult('manifest', D.QUARANTINED, (str(error),)),))
    artifacts = []
    remaining = policy['max_batch_size_bytes']
    for index, artifact in enumerate(manifest['artifacts']):
        result = inspect_artifact(batch_dir, artifact, policy, remaining,
                                  within_count=index < policy['max_files_per_batch'])
        artifacts.append(result)
        # Only bytes actually read consume the inspection budget. An oversized
        # rejected object cannot deprive later small artifacts of their budget.
        if result.sha256:
            remaining -= result.size_bytes
    malware = scan_malware_batch(batch_dir, artifacts, policy)
    artifacts = tuple(apply_malware_result(a, malware[a.artifact_id], policy)
                      if a.artifact_id in malware else a for a in artifacts)
    return InspectionResult(batch_dir.name, digest, policy, artifacts,
                            (CheckResult('manifest'),))
