import json
from dataclasses import dataclass
from pathlib import Path


ORIGIN_FILE = "origin.json"
UNATTRIBUTED = "unattributed"


@dataclass(frozen=True)
class IntakeSource:
    name: str
    files: tuple[Path, ...]
    origin: dict


def read_uploads(root: Path) -> list[IntakeSource]:
    if not root.is_dir():
        raise ValueError(f"Uploads directory not found: {root}")

    sources = []

    # Each folder = one source
    for folder in sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
        origin_path = folder / ORIGIN_FILE
        origin = {}

        if origin_path.is_file():
            try:
                origin = json.loads(
                    origin_path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid origin.json: {origin_path}"
                ) from error

            if not isinstance(origin, dict):
                raise ValueError(
                    f"{origin_path} must contain a JSON object"
                )

        files = tuple(
            sorted(
                path
                for path in folder.rglob("*")
                if path.is_file()
                and path.name != ORIGIN_FILE
                and not path.name.startswith(".")
            )
        )

        if files:
            sources.append(
                IntakeSource(
                    name=folder.name,
                    files=files,
                    origin=origin,
                )
            )

    # Files directly inside uploads/
    loose_files = tuple(
        sorted(
            path
            for path in root.iterdir()
            if path.is_file()
            and path.name != ORIGIN_FILE
            and not path.name.startswith(".")
        )
    )

    if loose_files:
        sources.append(
            IntakeSource(
                name=UNATTRIBUTED,
                files=loose_files,
                origin={},
            )
        )

    return sources