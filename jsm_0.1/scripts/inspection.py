from paths import BATCHES_DIR

from src.inspection.inspector import inspect_batch
from src.inspection.report import write_inspection_report
from src.inspection.quarantine import quarantine_batch


if __name__ == "__main__":
    if not BATCHES_DIR.exists():
        raise ValueError(f"Batches directory not found: {BATCHES_DIR}")

    batch_dirs = sorted(
        path
        for path in BATCHES_DIR.iterdir()
        if path.is_dir()
    )

    if not batch_dirs:
        raise ValueError(f"No batches found under {BATCHES_DIR}")

    for batch_dir in batch_dirs:
        result = inspect_batch(batch_dir)

        report_path = write_inspection_report(
            batch_dir=batch_dir,
            result=result,
        )

        if result.passed:
            print(f"PASS: {batch_dir.name}")
            print(f"  report: {report_path.name}")

        else:
            print(f"QUARANTINE: {batch_dir.name}")

            for error in result.errors:
                print(f"  - {error}")

            quarantine_path = quarantine_batch(
                batch_dir=batch_dir,
                result=result,
            )

            print(f"  report: {report_path.name}")
            print(f"  quarantine: {quarantine_path}")