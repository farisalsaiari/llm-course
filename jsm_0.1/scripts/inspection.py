"""Inspect pending batches, or explicitly re-inspect one batch."""
import argparse

from paths import BATCHES_DIR
from src.corpus_factory.inspection.config import INSPECTION_CONFIG_PATH, load_inspection_config
from src.corpus_factory.inspection.inspector import inspect_batch
from src.corpus_factory.inspection.quarantine import quarantine_batch
from src.corpus_factory.inspection.report import completed_batches, write_inspection_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch_id', nargs='?')
    parser.add_argument('--latest', action='store_true', help='re-inspect the most recently acquired batch')
    parser.add_argument('--policy', type=type(INSPECTION_CONFIG_PATH), default=INSPECTION_CONFIG_PATH)
    args = parser.parse_args()
    if args.batch_id and args.latest:
        parser.error('choose a batch ID or --latest')
    policy = load_inspection_config(args.policy)
    batches = sorted(p for p in BATCHES_DIR.glob('*') if p.is_dir() or p.is_symlink())
    if args.batch_id:
        if '/' in args.batch_id or '\\' in args.batch_id or args.batch_id in {'.', '..'}:
            parser.error('batch_id must be a directory name')
        batches = [p for p in batches if p.name == args.batch_id]
        if not batches:
            parser.error('batch not found')
    elif args.latest:
        batches = sorted(batches, key=lambda p: (p.lstat().st_mtime_ns, p.name))[-1:]
    else:
        completed = completed_batches(policy)
        batches = [p for p in batches if str(p.absolute()) not in completed]
    if not batches:
        print('No pending batches. Acquire uploads first, or select a batch to re-inspect.')
    for batch_dir in batches:
        result = inspect_batch(batch_dir, policy)
        report = write_inspection_report(batch_dir, result)
        quarantine = quarantine_batch(batch_dir, result, report.parent.name)
        summary = result.summary
        print(f'{batch_dir.name}: accepted={summary["accepted"]} quarantined={summary["quarantined"]} rejected={summary["rejected"]}')
        for error in result.errors:
            print(f'  batch quarantine: {error}')
        print(f'  report: {report}')
        if quarantine:
            print(f'  quarantine: {quarantine}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
