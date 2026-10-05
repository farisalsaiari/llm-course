import sys

from src.provenance.decision import write_rights_decision


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage:\n"
            "python -m scripts.provenance_review "
            "<batch-id> <allowed|denied|review_required> <basis>"
        )

    batch_id = sys.argv[1]
    training_use = sys.argv[2]
    basis = sys.argv[3]

    manifest_path = write_rights_decision(
        batch_id=batch_id,
        training_use=training_use,
        basis=basis,
    )

    print(f"Created provenance decision:")
    print(manifest_path)