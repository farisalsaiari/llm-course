import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from src.inspection.config import load_inspection_config
from src.inspection.result import InspectionResult

from src.inspection.result import (
    InspectionResult,
    CheckResult,
    ArtifactInspectionResult,
)

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".json",
    ".csv",
    ".xml",
    ".html",
    ".htm",
}


SIGNATURES = {
    "pdf": b"%PDF-",
    "zip": b"PK",
}


def _sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def _objects_dir(batch_dir: Path) -> Path:
    return batch_dir / "objects"


# ---------------------------------------------------------
# Manifest
# ---------------------------------------------------------

def check_manifest(batch_dir: Path) -> InspectionResult:
    errors = []

    manifest_path = batch_dir / "source.json"

    if not manifest_path.is_file():
        return InspectionResult(
            passed=False,
            errors=["source.json is missing"],
        )

    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except (json.JSONDecodeError, OSError) as error:
        return InspectionResult(
            passed=False,
            errors=[
                f"source.json cannot be read: {error}"
            ],
        )

    if not isinstance(manifest, dict):
        return InspectionResult(
            passed=False,
            errors=[
                "source.json must contain a JSON object"
            ],
        )

    required_fields = {
        "schema_version",
        "record_type",
        "batch_id",
        "source",
        "license",
        "artifacts",
    }

    for field in required_fields:
        if field not in manifest:
            errors.append(
                f"source.json missing required field: {field}"
            )

    if manifest.get("batch_id") != batch_dir.name:
        errors.append(
            "source.json batch_id does not match directory name"
        )

    artifacts = manifest.get("artifacts")

    if not isinstance(artifacts, list):
        errors.append(
            "artifacts must be a list"
        )

    elif not artifacts:
        errors.append(
            "artifacts list is empty"
        )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Integrity
# ---------------------------------------------------------

def check_integrity(batch_dir: Path) -> InspectionResult:
    errors = []

    manifest_path = batch_dir / "source.json"
    checksum_path = batch_dir / "source.json.sha256"

    if not manifest_path.is_file():
        errors.append(
            "source.json is missing"
        )

    if not checksum_path.is_file():
        errors.append(
            "source.json.sha256 is missing"
        )

    if errors:
        return InspectionResult(
            passed=False,
            errors=errors,
        )

    try:
        expected_manifest_hash = checksum_path.read_text(
            encoding="utf-8"
        ).strip()

        actual_manifest_hash = _sha256_file(
            manifest_path
        )

        if expected_manifest_hash != actual_manifest_hash:
            errors.append(
                "source.json.sha256 mismatch"
            )

        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )

    except (OSError, json.JSONDecodeError) as error:
        return InspectionResult(
            passed=False,
            errors=[
                f"cannot verify source.json: {error}"
            ],
        )

    for artifact in manifest.get("artifacts", []):
        artifact_id = artifact.get(
            "artifact_id",
            "unknown",
        )

        relative_path = artifact.get(
            "stored_relative_path"
        )

        expected_hash = artifact.get(
            "sha256"
        )

        if not relative_path:
            errors.append(
                f"{artifact_id}: stored_relative_path is missing"
            )
            continue

        if not expected_hash:
            errors.append(
                f"{artifact_id}: sha256 is missing"
            )
            continue

        artifact_path = batch_dir / relative_path

        if not artifact_path.is_file():
            errors.append(
                f"{artifact_id}: file is missing"
            )
            continue

        actual_hash = _sha256_file(
            artifact_path
        )

        if actual_hash != expected_hash:
            errors.append(
                f"{artifact_id}: sha256 mismatch"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Limits
# ---------------------------------------------------------

def check_limits(batch_dir: Path) -> InspectionResult:
    errors = []

    config = load_inspection_config()

    max_file_size = config["max_file_size_bytes"]
    max_batch_size = config["max_batch_size_bytes"]
    max_files_per_batch = config["max_files_per_batch"]

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    files = [
        path
        for path in objects_dir.iterdir()
        if path.is_file()
    ]

    if len(files) > max_files_per_batch:
        errors.append(
            f"batch contains too many files: {len(files)}"
        )

    total_size = 0

    for file_path in files:
        try:
            size = file_path.stat().st_size
        except OSError as error:
            errors.append(
                f"{file_path.name}: cannot read file size: {error}"
            )
            continue

        total_size += size

        if size == 0:
            errors.append(
                f"{file_path.name}: empty file"
            )

        if size > max_file_size:
            errors.append(
                f"{file_path.name}: file exceeds size limit"
            )

    if total_size > max_batch_size:
        errors.append(
            f"batch exceeds total size limit: "
            f"{total_size} bytes"
        )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# File Type
# ---------------------------------------------------------

def check_file_type(batch_dir: Path) -> InspectionResult:
    errors = []

    config = load_inspection_config()

    known_file_types = config[
        "known_file_types"
    ]

    allowed_extensions = {
        extension.lower()
        for extension in config[
            "allowed_extensions"
        ]
    }

    unknown_policy = config.get(
        "unknown_file_policy",
        "quarantine",
    )

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    for file_path in objects_dir.iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix not in allowed_extensions:
            if unknown_policy == "quarantine":
                errors.append(
                    f"{file_path.name}: "
                    f"unsupported or unknown file extension"
                )

            continue

        file_type = known_file_types.get(
            suffix
        )

        if file_type is None:
            continue

        expected_signature = SIGNATURES.get(
            file_type
        )

        if expected_signature is None:
            continue

        try:
            with file_path.open("rb") as file:
                actual_signature = file.read(
                    len(expected_signature)
                )

        except OSError as error:
            errors.append(
                f"{file_path.name}: "
                f"cannot read file signature: {error}"
            )
            continue

        if actual_signature != expected_signature:
            errors.append(
                f"{file_path.name}: "
                f"content does not match expected "
                f"{file_type} type"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Security
# ---------------------------------------------------------

def check_security(batch_dir: Path) -> InspectionResult:
    errors = []

    config = load_inspection_config()

    blocked_extensions = {
        extension.lower()
        for extension in config[
            "blocked_extensions"
        ]
    }

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    for file_path in objects_dir.iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix in blocked_extensions:
            errors.append(
                f"{file_path.name}: "
                f"blocked executable/script type"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Archive
# ---------------------------------------------------------

def check_archives(batch_dir: Path) -> InspectionResult:
    errors = []

    config = load_inspection_config()

    max_archive_files = config[
        "max_archive_files"
    ]

    max_uncompressed_bytes = config[
        "max_uncompressed_bytes"
    ]

    max_compression_ratio = config[
        "max_compression_ratio"
    ]

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    for file_path in objects_dir.iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix not in {
            ".zip",
            ".docx",
        }:
            continue

        try:
            with zipfile.ZipFile(
                file_path,
                "r",
            ) as archive:

                entries = archive.infolist()

                if len(entries) > max_archive_files:
                    errors.append(
                        f"{file_path.name}: "
                        f"too many archive entries"
                    )

                total_uncompressed = sum(
                    entry.file_size
                    for entry in entries
                )

                total_compressed = sum(
                    entry.compress_size
                    for entry in entries
                )

                if (
                    total_uncompressed
                    > max_uncompressed_bytes
                ):
                    errors.append(
                        f"{file_path.name}: "
                        f"uncompressed size exceeds limit"
                    )

                if total_compressed > 0:
                    ratio = (
                        total_uncompressed
                        / total_compressed
                    )

                    if ratio > max_compression_ratio:
                        errors.append(
                            f"{file_path.name}: "
                            f"suspicious compression ratio"
                        )

                for entry in entries:
                    parts = Path(
                        entry.filename
                    ).parts

                    if ".." in parts:
                        errors.append(
                            f"{file_path.name}: "
                            f"unsafe archive path"
                        )
                        break

        except zipfile.BadZipFile:
            errors.append(
                f"{file_path.name}: "
                f"invalid ZIP container"
            )

        except OSError as error:
            errors.append(
                f"{file_path.name}: "
                f"cannot inspect archive: {error}"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Malware
# ---------------------------------------------------------

def check_malware(batch_dir: Path) -> InspectionResult:
    """
    Placeholder.

    Later this will call a real malware scanner
    such as ClamAV or an external sandbox.
    """

    return InspectionResult(
        passed=True,
        errors=[],
    )


# ---------------------------------------------------------
# Readability
# ---------------------------------------------------------

def check_readability(batch_dir: Path) -> InspectionResult:
    errors = []

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    for file_path in objects_dir.iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        try:
            if suffix in TEXT_EXTENSIONS:
                with file_path.open(
                    "r",
                    encoding="utf-8",
                    errors="strict",
                ) as file:
                    file.read(4096)

            else:
                with file_path.open(
                    "rb"
                ) as file:
                    file.read(4096)

        except (
            OSError,
            UnicodeError,
        ) as error:
            errors.append(
                f"{file_path.name}: "
                f"unreadable file: {error}"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Text Content
# ---------------------------------------------------------

def check_text_content(
    batch_dir: Path,
) -> InspectionResult:
    errors = []

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    for file_path in objects_dir.iterdir():
        if not file_path.is_file():
            continue

        if (
            file_path.suffix.lower()
            not in TEXT_EXTENSIONS
        ):
            continue

        try:
            with file_path.open(
                "r",
                encoding="utf-8",
                errors="strict",
            ) as file:
                sample = file.read(8192)

        except UnicodeDecodeError:
            errors.append(
                f"{file_path.name}: "
                f"invalid UTF-8 text"
            )
            continue

        except OSError as error:
            errors.append(
                f"{file_path.name}: "
                f"cannot read text: {error}"
            )
            continue

        if "\x00" in sample:
            errors.append(
                f"{file_path.name}: "
                f"contains null bytes and "
                f"may not be plain text"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


# ---------------------------------------------------------
# Structured Content
# ---------------------------------------------------------

def check_structured_content(
    batch_dir: Path,
) -> InspectionResult:
    errors = []

    objects_dir = _objects_dir(batch_dir)

    if not objects_dir.is_dir():
        return InspectionResult(
            passed=False,
            errors=[
                "objects directory is missing"
            ],
        )

    for file_path in objects_dir.iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        try:
            if suffix == ".json":
                with file_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    json.load(file)

            elif suffix == ".xml":
                ET.parse(file_path)

        except json.JSONDecodeError as error:
            errors.append(
                f"{file_path.name}: "
                f"invalid JSON: {error}"
            )

        except ET.ParseError as error:
            errors.append(
                f"{file_path.name}: "
                f"invalid XML: {error}"
            )

        except OSError as error:
            errors.append(
                f"{file_path.name}: "
                f"cannot read file: {error}"
            )

    return InspectionResult(
        passed=len(errors) == 0,
        errors=errors,
    )


def inspect_artifact(
    file_path: Path,
    artifact: dict,
) -> ArtifactInspectionResult:

    artifact_id = artifact.get(
        "artifact_id",
        "unknown",
    )

    filename = artifact.get(
        "original_filename",
        file_path.name,
    )

    checks = []
    errors = []

    config = load_inspection_config()

    suffix = file_path.suffix.lower()

    # -------------------------------------------------
    # Exists
    # -------------------------------------------------

    exists_errors = []

    if not file_path.is_file():
        exists_errors.append("file is missing")

    checks.append(
        CheckResult(
            name="exists",
            passed=len(exists_errors) == 0,
            errors=exists_errors,
        )
    )

    errors.extend(exists_errors)

    if exists_errors:
        return ArtifactInspectionResult(
            artifact_id=artifact_id,
            filename=filename,
            passed=False,
            checks=checks,
            errors=errors,
        )

    # -------------------------------------------------
    # Size
    # -------------------------------------------------

    size_errors = []

    size = file_path.stat().st_size

    if size == 0:
        size_errors.append("empty file")

    if size > config["max_file_size_bytes"]:
        size_errors.append("file exceeds size limit")

    checks.append(
        CheckResult(
            name="limits",
            passed=len(size_errors) == 0,
            errors=size_errors,
        )
    )

    errors.extend(size_errors)

    # -------------------------------------------------
    # Extension / File Type
    # -------------------------------------------------

    type_errors = []

    allowed_extensions = {
        ext.lower()
        for ext in config["allowed_extensions"]
    }

    blocked_extensions = {
        ext.lower()
        for ext in config["blocked_extensions"]
    }

    if suffix in blocked_extensions:
        type_errors.append(
            "blocked executable/script type"
        )

    elif suffix not in allowed_extensions:
        type_errors.append(
            "unsupported or unknown file extension"
        )

    file_type = config["known_file_types"].get(suffix)

    if file_type:
        expected_signature = SIGNATURES.get(file_type)

        if expected_signature:
            with file_path.open("rb") as file:
                actual_signature = file.read(
                    len(expected_signature)
                )

            if actual_signature != expected_signature:
                type_errors.append(
                    f"content does not match expected "
                    f"{file_type} type"
                )

    checks.append(
        CheckResult(
            name="file_type",
            passed=len(type_errors) == 0,
            errors=type_errors,
        )
    )

    errors.extend(type_errors)

    # -------------------------------------------------
    # Readability / Text
    # -------------------------------------------------

    readability_errors = []

    if suffix in TEXT_EXTENSIONS:
        try:
            with file_path.open(
                "r",
                encoding="utf-8",
                errors="strict",
            ) as file:
                sample = file.read(8192)

            if "\x00" in sample:
                readability_errors.append(
                    "contains null bytes"
                )

        except UnicodeDecodeError:
            readability_errors.append(
                "invalid UTF-8 text"
            )

        except OSError as error:
            readability_errors.append(
                f"cannot read file: {error}"
            )

    else:
        try:
            with file_path.open("rb") as file:
                file.read(4096)

        except OSError as error:
            readability_errors.append(
                f"cannot read file: {error}"
            )

    checks.append(
        CheckResult(
            name="readability",
            passed=len(readability_errors) == 0,
            errors=readability_errors,
        )
    )

    errors.extend(readability_errors)

    return ArtifactInspectionResult(
        artifact_id=artifact_id,
        filename=filename,
        passed=len(errors) == 0,
        checks=checks,
        errors=errors,
    )