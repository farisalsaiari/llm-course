# Acquisition

The Acquisition stage receives externally collected or manually uploaded files and publishes them into immutable incoming batches.

## Purpose

Acquisition is responsible only for receiving and recording source bytes.

It does **not**:

- inspect files
- extract text
- clean content
- normalize content
- classify quality
- approve training use

## Flow

```text
storage/uploads/
        ↓
   Acquisition
        ↓
storage/incoming/batches/
```

## Upload Structure

Files may be grouped by source:

```text
storage/uploads/
├── aramco/
│   ├── origin.json
│   ├── report.pdf
│   └── notes.txt
│
├── wikipedia-ar/
│   ├── origin.json
│   └── article.txt
│
└── random-file.pdf
```

Each source folder becomes its own batch.

Files placed directly inside `uploads/` are grouped into:

```text
unattributed
```

## origin.json

Optional source declaration:

```json
{
  "platform": "Aramco",
  "source_type": "corporate_documents",
  "source_url": "https://aramco.example/internal",
  "license_identifier": "All rights reserved",
  "attribution": "Aramco"
}
```

`origin.json` describes the source.

It is never treated as corpus data.

## Incoming Batch

Example:

```text
storage/incoming/batches/
└── aramco-20261004T105815Z-24cde35f/
    ├── objects/
    │   ├── 00000001-report.pdf
    │   └── 00000002-notes.txt
    │
    ├── source.json
    └── source.json.sha256
```

## source.json

The generated manifest records:

- batch ID
- source
- connector
- collection time
- creation time
- license information
- training-use status
- immutability policy
- artifact IDs
- original filenames
- SHA-256 hashes
- sizes
- stored paths
- summary
- next stage

Training permission remains:

```text
review_required
```

Acquisition never grants training approval.

## Immutability

Incoming batches are treated as immutable.

```text
append_only = true
never_modify_in_place = true
```

Source bytes must remain unchanged after publication.

## Duplicate Protection

Before creating a new batch, Acquisition compares:

```text
source/platform
+
artifact SHA-256 fingerprints
```

Previously acquired identical sources are skipped.

Changed bytes create new work.

## Main Code

```text
src/corpus_factory/acquisition/
├── batch.py
├── intake.py
├── discovery.py
└── hashing.py
```

Entry point:

```text
scripts/acquisition.py
```

Run:

```bash
python -m scripts.acquisition
```

## Output

Successful Acquisition produces immutable batches ready for:

```text
Inspection
```