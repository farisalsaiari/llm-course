def clean_text(text: str) -> str:
    """
    Minimal production-safe cleaning.

    This stage only removes technical formatting noise.
    It does NOT normalize Arabic or change linguistic content.
    """

    # Normalize line endings:
    # Windows \r\n and old Mac \r -> Unix \n
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove trailing whitespace from each line
    lines = [
        line.rstrip()
        for line in text.split("\n")
    ]

    # Remove empty lines from the beginning
    while lines and not lines[0].strip():
        lines.pop(0)

    # Remove empty lines from the end
    while lines and not lines[-1].strip():
        lines.pop()

    return "\n".join(lines)