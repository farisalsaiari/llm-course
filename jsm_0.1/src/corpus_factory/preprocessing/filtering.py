from dataclasses import dataclass


@dataclass(frozen=True)
class FilterResult:
    accepted: bool
    reason: str


def filter_text(text: str) -> FilterResult:
    if not text.strip():
        return FilterResult(
            accepted=False,
            reason="empty_document",
        )

    if len(text) < 20:
        return FilterResult(
            accepted=False,
            reason="too_short",
        )

    return FilterResult(
        accepted=True,
        reason="accepted",
    )