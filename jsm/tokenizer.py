# data = "i love coffee"

# Read raw training text from file
with open("data/raw/plain1.txt", "r", encoding="utf-8") as file:
    data = file.read()


# Tokenization: Text → Tokens
words = data.split()


# Vocabulary: Token → ID mapping
vocabulary = {
    word: i for i, word in enumerate(words)
}


# Encoding: Tokens → Token IDs
token_ids = [vocabulary[word] for word in words]


# Decoding: Token IDs → Tokens
id_to_word = {
    i: word for word, i in vocabulary.items()
}

decoded_words = [
    id_to_word[i] for i in token_ids
]


if __name__ == "__main__":
    print("Raw text:", data)
    print("Tokens:", words)
    print("Vocabulary:", vocabulary)
    print("Token IDs:", token_ids)
    print("Decoded:", decoded_words)