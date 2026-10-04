from pathlib import Path
from datetime import datetime, timezone

from src.acquisition.batch import acquire_batch


if __name__ == "__main__":
    source_files = [
        Path("data/raw/plain1.txt"),
        Path("data/raw/plain2.txt"),
    ]

    source_info = {
        "source_url": None,
        "collection_time": datetime.now(timezone.utc).isoformat(),
        "license_status": "unknown",
    }

    batch_dir = acquire_batch(
        source_files=source_files,
        source_info=source_info,
    )

    print(batch_dir)