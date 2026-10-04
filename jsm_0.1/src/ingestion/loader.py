from pathlib import Path

from paths import RAW_DATA_DIR
from src.ingestion.dispatcher import dispatch


def load_documents(workers: int = 4):
    files = RAW_DATA_DIR.rglob("*.txt")

    yield from dispatch(files, workers=workers)