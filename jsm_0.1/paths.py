from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"
TOKENIZER_DIR = ARTIFACTS_DIR / "tokenizer"
TOKENIZER_PATH = TOKENIZER_DIR / "tokenizer.json"
CHECKPOINT_PATH = ARTIFACTS_DIR / "tiny_model.pt"

STORAGE_DIR = PROJECT_DIR / "storage"
INCOMING_DIR = STORAGE_DIR / "incoming"
BATCHES_DIR = INCOMING_DIR / "batches"