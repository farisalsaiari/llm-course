from src.ingestion.loader import load_documents
from src.extraction.extractor import extract


if __name__ == "__main__":
    for document in load_documents(workers=4):
        # print(document)
        extracted_document = extract(document)
        print(extracted_document)