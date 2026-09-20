# Get raw documents from data_loader.py
from data_loader import documents


# -----------------------------------
# Tokenization: Documents → Tokens
# -----------------------------------

tokenized_documents = []

for document in documents:
    words = document.split()
    tokenized_documents.append(words)


# -----------------------------------
# Combine tokens ONLY to build vocabulary
# -----------------------------------

all_words = []

for document_words in tokenized_documents:
    all_words.extend(document_words)


# -----------------------------------
# Build vocabulary from unique tokens
# -----------------------------------

unique_words = list(dict.fromkeys(all_words))

vocabulary = {
    word: i for i, word in enumerate(unique_words)
}


# -----------------------------------
# Encoding: Tokens → Token IDs
# Keep each document separate
# -----------------------------------

encoded_documents = []

for document_words in tokenized_documents:

    token_ids = [
        vocabulary[word]
        for word in document_words
    ]

    encoded_documents.append(token_ids)


# -----------------------------------
# Decoding: Token IDs → Tokens
# -----------------------------------

id_to_word = {
    i: word for word, i in vocabulary.items()
}

decoded_documents = []

for token_ids in encoded_documents:

    decoded_words = [
        id_to_word[i]
        for i in token_ids
    ]

    decoded_documents.append(decoded_words)


# -----------------------------------
# Show results only when running this file
# -----------------------------------

if __name__ == "__main__":

    print("Tokenized documents:")
    print(tokenized_documents)

    print("Vocabulary:")
    print(vocabulary)

    print("Encoded documents:")
    print(encoded_documents)

    print("Decoded documents:")
    print(decoded_documents)