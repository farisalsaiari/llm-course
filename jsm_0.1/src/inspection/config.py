import json
from pathlib import Path

from paths import PROJECT_DIR


INSPECTION_CONFIG_PATH = (
    PROJECT_DIR
    / "configs"
    / "inspection.json"
)


def load_inspection_config() -> dict:
    if not INSPECTION_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Inspection config not found: "
            f"{INSPECTION_CONFIG_PATH}"
        )

    try:
        with INSPECTION_CONFIG_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            config = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid inspection config JSON: "
            f"{INSPECTION_CONFIG_PATH}"
        ) from error

    if not isinstance(config, dict):
        raise ValueError(
            "Inspection config must contain a JSON object"
        )

    return config