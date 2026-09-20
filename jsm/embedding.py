import torch
import torch.nn as nn

# Get data from tokenizer.py
from tokenizer import vocabulary, token_ids, words


torch.manual_seed(42)

# Token IDs → Tensor
ids = torch.tensor(token_ids)

# Create Embedding layer
embedding = nn.Embedding(
    num_embeddings=len(vocabulary),
    embedding_dim=3
)

# Token IDs → Embedding vectors
vectors = embedding(ids)


if __name__ == "__main__":
    for word, vector in zip(words, vectors):
        print(word, "→", vector)