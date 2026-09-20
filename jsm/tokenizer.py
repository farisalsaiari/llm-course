data = "i love coffee"

# Tokenization: Text → Tokens
words = data.split()

# Vocabulary: Token → ID
vocabulary = {
    word: i for i, word in enumerate(words)
}

# Encoding: Tokens → Token IDs
token_ids = [vocabulary[word] for word in words]

# Decoding: Token IDs → Tokens
id_to_word = {i: word for word, i in vocabulary.items()}
decoded_words = [id_to_word[i] for i in token_ids]