from datetime import datetime, timezone

from paths import UPLOADS_DIR
from src.acquisition.batch import acquire_batch


if __name__ == "__main__":
    source_files = [
        path
        for path in UPLOADS_DIR.iterdir()
        if path.is_file()
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