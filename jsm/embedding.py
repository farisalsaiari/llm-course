import torch
import torch.nn as nn

from tokenizer import vocabulary, encoded_documents, tokenized_documents


# Keep random embedding values the same every run
torch.manual_seed(42)


# Create Embedding layer
embedding = nn.Embedding(

    # Number of unique tokens
    num_embeddings=len(vocabulary),

    # 3 numbers for each token
    embedding_dim=3
)


if __name__ == "__main__":

    # Process each document separately
    for words, token_ids in zip(
        tokenized_documents,
        encoded_documents
    ):

        # Token IDs → Tensor
        ids = torch.tensor(token_ids)

        # Tensor IDs → Embedding vectors
        vectors = embedding(ids)

        print("Document:")

        for word, vector in zip(words, vectors):
            print(word, "→", vector)

        print()