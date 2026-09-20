import random

from paths import RAW_DATA_DIR


# Folder containing raw text files
raw_folder = RAW_DATA_DIR

# Store each document separately
documents = []


# Read every .txt file
for file_path in raw_folder.glob("*.txt"):

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read().strip()

    documents.append(text)


if __name__ == "__main__":
    print(documents)


def split_documents(documents, validation_fraction=0.2, seed=42):

    if len(documents) < 2:
        raise ValueError("At least two documents are required for a split.")

    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be in (0, 1).")

    indices = list(range(len(documents)))
    random.Random(seed).shuffle(indices)
    validation_count = max(
        1,
        round(len(documents) * validation_fraction)
    )
    validation_indices = set(indices[:validation_count])

    training = [
        document for index, document in enumerate(documents)
        if index not in validation_indices
    ]
    validation = [
        document for index, document in enumerate(documents)
        if index in validation_indices
    ]

    return training, validation


def create_language_model_windows(
    encoded_documents,
    sequence_length,
    stride=1
):

    if sequence_length < 1:
        raise ValueError("sequence_length must be positive.")

    if stride < 1:
        raise ValueError("stride must be positive.")

    windows = []

    for token_ids in encoded_documents:

        final_start = len(token_ids) - sequence_length

        for start in range(0, final_start, stride):

            input_ids = token_ids[
                start:start + sequence_length
            ]

            target_ids = token_ids[
                start + 1:start + sequence_length + 1
            ]

            windows.append((input_ids, target_ids))

    return windows
