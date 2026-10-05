from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable

from src.corpus_factory.ingestion.worker import process_file


def dispatch(files: Iterable[Path], workers: int = 4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for document in executor.map(process_file, files):
            yield document