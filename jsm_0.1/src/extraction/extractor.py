from src.ingestion.document import Document


def extract(document: Document) -> Document:
    if document.source_type == "txt":
        return document

    raise ValueError(
        f"Unsupported source type: {document.source_type}"
    )