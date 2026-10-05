import hashlib
from pathlib import Path


def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    sha256 = hashlib.sha256()

    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest()