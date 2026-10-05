import unicodedata


def normalize_text(text: str) -> str:
    """
    Minimal normalization.

    This stage keeps linguistic meaning intact.
    It does NOT remove tatweel, diacritics, or change Arabic letters.
    """

    # Canonical Unicode normalization only
    text = unicodedata.normalize("NFC", text)

    return text