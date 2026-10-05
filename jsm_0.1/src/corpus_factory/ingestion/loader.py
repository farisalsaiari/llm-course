from paths import RAW_STORAGE_DIR
from src.corpus_factory.ingestion.dispatcher import dispatch


def load_documents(workers: int = 4):
    files = (
        path
        for path in RAW_STORAGE_DIR.rglob("*")
        if path.is_file()
    )

    yield from dispatch(files, workers=workers)