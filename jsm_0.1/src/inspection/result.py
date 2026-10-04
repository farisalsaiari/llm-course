from dataclasses import dataclass, field


@dataclass
class CheckResult:
    name: str
    passed: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class ArtifactInspectionResult:
    artifact_id: str
    filename: str
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class InspectionResult:
    passed: bool

    checks: list[CheckResult] = field(default_factory=list)

    artifacts: list[ArtifactInspectionResult] = field(
        default_factory=list
    )

    errors: list[str] = field(default_factory=list)