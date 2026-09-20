import torch
import torch.nn as nn

# Keep random numbers the same on every run
torch.manual_seed(42)

data = "i love coffee"

# Tokenization: Text → Tokens
words = data.split()

# Vocabulary: Token → ID mapping
vocabulary = {
    word: i for i, word in enumerate(words)
}

# Encoding: Tokens → Token IDs 
token_ids = [vocabulary[word] for word in words]

# Embedding: Token IDs → Vectors
# Convert Token IDs into a PyTorch Tensor
ids = torch.tensor(token_ids)

# Create the Embedding layer
embedding = nn.Embedding(
    # Number of tokens in our vocabulary
   num_embeddings=len(vocabulary),
    # Number of values in each embedding vector
    embedding_dim=3
)
# Convert Token IDs into embedding vectors
vectors = embedding(ids)

# Show the shape of the embedding output
print("Embedding shape:", vectors.shape)

# Get only the embedding for "love"
love_id = vocabulary["love"]

print("love ID:", love_id)
print("love embedding:", embedding.weight[love_id])

# Show each word with its embedding vector
for word, vector in zip(words, vectors):
    print(word, "→", vector)


# Decoding: Token IDs → Tokens
id_to_word = {i: word for word, i in vocabulary.items()}
decoded_words = [id_to_word[i] for i in token_ids]

print(words)
print(vocabulary)
print(token_ids)
print(vectors)
print(decoded_words)
# See entire embedding weight matrix
print(embedding.weight)