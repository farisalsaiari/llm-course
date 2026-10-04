from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


# Corpus storage pipeline
STORAGE_DIR = PROJECT_DIR / "storage"

UPLOADS_DIR = STORAGE_DIR / "uploads"

INCOMING_DIR = STORAGE_DIR / "incoming"
BATCHES_DIR = INCOMING_DIR / "batches"

QUARANTINE_DIR = STORAGE_DIR / "quarantine"
RAW_STORAGE_DIR = STORAGE_DIR / "raw"
EXTRACTED_DIR = STORAGE_DIR / "extracted"
PROCESSED_DIR = STORAGE_DIR / "processed"
TRAINING_DATA_DIR = STORAGE_DIR / "training"


# Model / training artifacts
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"

TOKENIZER_DIR = ARTIFACTS_DIR / "tokenizer"
TOKENIZER_PATH = TOKENIZER_DIR / "tokenizer.json"

CHECKPOINTS_DIR = ARTIFACTS_DIR / "checkpoints"
CHECKPOINT_PATH = CHECKPOINTS_DIR / "tiny_model.pt"

LOGS_DIR = ARTIFACTS_DIR / "logs"
EVALUATIONS_DIR = ARTIFACTS_DIR / "evaluations"