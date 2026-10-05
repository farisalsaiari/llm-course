import hashlib


def choose_split(document_id: str) -> str:
    """
    Deterministic split based on document_id.

    90% train
    5% validation
    5% test
    """

    digest = hashlib.sha256(
        document_id.encode("utf-8")
    ).hexdigest()

    bucket = int(digest[:8], 16) % 100

    if bucket < 90:
        return "train"

    if bucket < 95:
        return "validation"

    return "test"