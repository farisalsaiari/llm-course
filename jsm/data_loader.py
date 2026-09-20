from pathlib import Path


# Folder containing raw text files
raw_folder = Path("data/raw")

# Store each document separately
documents = []


# Read every .txt file
for file_path in raw_folder.glob("*.txt"):

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read().strip()

    documents.append(text)


if __name__ == "__main__":
    print(documents)