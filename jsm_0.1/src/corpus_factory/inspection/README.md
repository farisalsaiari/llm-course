# Inspection

Inspection answers **“Can this artifact safely and structurally continue?”**
It observes source bytes. It does not extract corpus text, clean data, score
language quality, approve training rights, deduplicate content, or run later stages.

## Run

From `jsm_0.1/`:

```bash
python -m scripts.inspection                 # pending batches under the current policy/version
python -m scripts.inspection <batch-id>      # explicit re-inspection; new record every time
python -m scripts.inspection --latest        # newest acquired directory, including inspected batches
python -m scripts.inspection --policy configs/inspection.json
python -m unittest discover -s tests -p test_inspection.py -v
```

If incoming storage is empty, run the existing `python -m scripts.acquisition`
first. Acquisition behavior and `source.json` remain unchanged.

## Decisions and batch trust

Severity only increases: `accepted_for_ingestion < quarantined < rejected`.

| Evidence | Decision |
| --- | --- |
| Supported, structurally valid file with required checks satisfied | Accepted |
| Empty file, fake extension, invalid encoding, corrupt structure, hash/size mismatch | Quarantined |
| Missing validator, or required malware scan unavailable/failed | Quarantined |
| Legacy `.doc` without a safe cross-platform validator | Quarantined |
| Symlink/reparse point, non-regular file, unsafe stored path | Rejected |
| Blocked executable/macro extension or executable MIME | Rejected |
| Hard resource limit, archive traversal/bomb/active content, XML entities | Rejected |
| Malware infection | Rejected |

Only manifest trust failures block the entire batch: missing or invalid
`source.json`, checksum mismatch, wrong batch ID, unsupported schema, malformed
metadata/artifact entries, or duplicate manifest IDs/paths. Artifact content
failures never make accepted siblings ineligible.

File-count limits apply in manifest order. Files exceeding the remaining byte
budget are rejected individually; oversized or blocked files are not read and do
not consume that byte budget. Summary bytes count observed regular-file sizes,
including rejected files, so they can exceed the inspection read budget.

## Safety and format coverage

Incoming objects must use Acquisition's `objects/<filename>` layout. Inspection
checks every filesystem component for links, rejects special files before opening,
and pins directory handles with `O_NOFOLLOW` on POSIX. Windows uses `CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT`, checks handle
attributes, and keeps parents open without delete sharing. See the
[Windows file-opening contract](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew).
Incoming storage must remain append-only and unavailable to untrusted writers. Content checks use a private, bounded snapshot of the exact bytes
hashed; ClamAV receives separate hash-verified snapshots with generated filenames.
Temporary disk space is required; incoming files are never moved or rewritten.

Content signatures and bounded ZIP metadata provide portable MIME evidence.
Optional `python-magic`/libmagic supplements unknown binary types. Missing detection
is recorded as unavailable and quarantines the artifact. Detection never relies
on the filename alone or a hard-coded `/usr/bin/file`.

- Text: `.txt`, `.text`, `.md`, `.markdown`, `.csv`, `.tsv`, `.json`, `.jsonl`,
  `.ndjson`, `.html`, `.htm`, `.xml`, `.yaml`, `.yml`, `.log`.
- Incremental decoding supports UTF-8, UTF-8 BOM, and BOM-declared UTF-16.
  Character counts exclude BOMs and include original newline characters. Line
  counts recognize LF, CRLF, and CR; a trailing newline does not add an empty line.
  Maximum line length excludes newline characters. Binary controls, invalid
  encodings, and excessive line lengths quarantine the artifact. No normalization.
- JSON is parsed within a configured memory bound; JSONL/NDJSON is validated per
  nonblank line after line-length checks. CSV/TSV/YAML/Markdown/log files receive
  text safety checks, not application-schema validation or YAML object construction.
- XML is parsed incrementally with no retained tree. DTDs and entities are rejected
  by parser callbacks before expansion, including UTF-16 declarations. Depth and
  structural byte limits apply. HTML is parsed without fetching resources and
  rejects active elements, event handlers, embedded content, and redirects.
- `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods`, `.epub`: bounded central directory,
  entry count, member and total expanded size, compression ratios, safe paths,
  no encryption, links, duplicate names, executables, macros, or Office embeddings.
  Required document XML and package metadata are checked. XML is parsed safely;
  external Office relationships are rejected. All members are streamed to verify
  decompression and CRC. ZIP64/multi-volume archives are conservatively quarantined.
  Generic `.zip` is intentionally unsupported.
- PDF: signature/trailer checks, streamed active-name detection (`JavaScript`,
  `JS`, `Launch`, `EmbeddedFile`, `OpenAction`, `AA`, including `#xx` escapes),
  and `pdfinfo` structural validation with a timeout. Encrypted PDFs are rejected.
  Required deep validation quarantines PDFs if `pdfinfo` is unavailable; if that
  requirement is explicitly disabled, static checks still run and the missing
  validator is flagged. Static inspection is not exhaustive PDF deobfuscation.
- RTF: signature, balanced groups, and active/embedded/binary control screening.
  Legacy `.doc` is recognized but always quarantined; there is no textutil dependency.

Ordinary links are not classified for phishing, and no network resources are
visited. Consequently, the fixture `10-pdf-with-phishing-links.pdf` passes structural
inspection. Acceptance does not approve the document's content or training rights.

## Malware

Statuses are `not_run`, `unavailable`, `clean`, `infected`, and `error`, with engine,
signature, and error evidence. Installed `clamdscan` is preferred; unresolved files
fall back to `clamscan`. Each process handles a chunk bounded by file count and total bytes, never one
process per file.
No shell is used; timeouts and explicit per-file verdicts are required. An absent
or failed scanner is never labeled clean. Hard-rejected and empty files may remain
`not_run`. Infection always rejects, even with `require_malware_scan: false`.

The default policy requires malware scans and deep validation. For development,
setting `require_malware_scan` to false allows otherwise safe files to proceed when
scanning is unavailable; their actual scan status remains visible. No mandatory
Python dependency was added. ClamAV with signature databases and `pdfinfo` are
external tools; libmagic is optional. This implementation was exercised on macOS;
Windows behavior has not been exercised on a Windows runner.

## Policy

`configs/inspection.json` holds all tunable limits and MIME/extension policy.
`config.py` only loads and validates it, failing before inspection on invalid values.

| Policy keys | Current defaults |
| --- | --- |
| `max_file_size_bytes`, `max_batch_size_bytes`, `max_files_per_batch` | 2 GiB, 100 GiB, 100,000 |
| `max_line_characters` | 1,000,000 |
| `max_manifest_bytes`, `max_structured_bytes`, `max_xml_depth` | 64 MiB, 16 MiB, 256 |
| `max_archive_files`, `max_archive_member_bytes` | 10,000, 100 MiB |
| `max_uncompressed_bytes`, `max_compression_ratio` | 5 GiB, 200 |
| `allowed_extensions`, `blocked_extensions` | supported corpus types; executable/script/macro blocks |
| `expected_mime_types`, `blocked_mime_types` | extension-to-MIME lists; executable MIME blocks |
| `unknown_file_policy` | `quarantine` (or `reject`) |
| `require_malware_scan`, `require_deep_container_inspection` | `true`, `true` |
| `malware_chunk_size`, `max_malware_chunk_bytes` | 128 files, 2 GiB of temporary scan snapshots |
| `malware_timeout_seconds`, `pdf_timeout_seconds` | 120 seconds per engine/chunk, 30 seconds |

Structural bounds deliberately quarantine documents that exceed validator capacity,
even when they fit the larger per-file limit. Tune resource limits to your host's
memory and temporary disk capacity before processing large corpora.

## Immutable output

```text
storage/catalog/inspections/
  inspection_<UTC-timestamp>_<uuid>/
    manifest.json
    manifest.json.sha256
storage/quarantine/<batch-id>/
  inspection_<UTC-timestamp>_<uuid>/
    quarantine.json
    quarantine.json.sha256
```

Each record is written and synced in a temporary directory, then renamed into
place with its checksum. Existing nonempty records are never overwritten.
Historical batch-local `inspection.json` and quarantine records remain untouched;
they do not satisfy the new report contract.

Reports contain the inspection ID, schema/inspector versions, time, incoming batch
reference, source manifest hash, policy snapshot, batch checks, artifact evidence,
summary, duplicate groups, `next_stage`, and explicit `eligible_artifact_ids`.
A valid mixed batch can have `next_stage: ingestion`; only its accepted artifact
IDs are eligible. Nothing invokes Ingestion automatically.

Byte-duplicate groups use observed hashes within each inspected batch, including
quarantined content when hashing succeeded. Cross-batch deduplication is not done.
No duplicate bytes are deleted. Quarantine records contain per-artifact decisions,
reasons, inspection IDs, and source references, or batch errors for untrusted
manifests. Summaries include each decision and all five malware statuses.

Pending selection is policy/version-aware and verifies report and required
quarantine-reference checksums. Interrupted publication remains pending for retry. It assumes
incoming batches remain immutable. Use an explicit batch ID for re-inspection,
a retry after scanner installation, or investigation of changed incoming bytes.

## Package

```text
src/corpus_factory/inspection/
  __init__.py
  checks.py
  deep_inspection.py
  inspector.py
  result.py
  report.py
  quarantine.py
  config.py
  README.md
```

`deep_inspection.py` isolates the bounded container parsers. Obsolete batch-wide
checks and boolean pass/fail models were removed. The unused duplicate policy
loader `src/config.py` was deleted; configuration has one owner.
