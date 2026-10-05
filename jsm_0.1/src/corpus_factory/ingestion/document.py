from dataclasses import dataclass


@dataclass
class Document:
    source_path: str
    source_type: str
    raw_text: str