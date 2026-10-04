from dataclasses import dataclass


@dataclass(frozen=True)
class RightsDecision:
    allowed: bool
    reason: str


def evaluate_training_rights(source_manifest: dict) -> RightsDecision:
    license_info = source_manifest.get("license", {})

    training_use = license_info.get(
        "training_use",
        "review_required",
    )

    if training_use == "allowed":
        return RightsDecision(
            allowed=True,
            reason="training use explicitly allowed",
        )

    return RightsDecision(
        allowed=False,
        reason=f"training use status: {training_use}",
    )