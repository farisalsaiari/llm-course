import json

from paths import PROJECT_DIR


INSPECTION_CONFIG_PATH = (
    PROJECT_DIR
    / "configs"
    / "inspection.json"
)


def load_inspection_config() -> dict:
    with INSPECTION_CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)