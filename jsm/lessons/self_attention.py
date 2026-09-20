import torch
import torch.nn as nn


# -----------------------------------
# Self-Attention Class
# -----------------------------------

class SelfAttention(nn.Module):

    def __init__(self, embedding_dim):

        super().__init__()

        self.query_layer = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.key_layer = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.value_layer = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )


    # -----------------------------------
    # Forward
    # -----------------------------------

    def forward(self, vectors):

        # -----------------------------------
        # Embeddings → Q, K, V
        # -----------------------------------

        Q = self.query_layer(vectors)

        K = self.key_layer(vectors)

        V = self.value_layer(vectors)


        # -----------------------------------
        # Q × Kᵀ / √d_k
        # -----------------------------------

        d_k = K.shape[-1]

        attention_scores = (
            Q @ K.T
        ) / (d_k ** 0.5)


        # -----------------------------------
        # Create Causal Mask
        # -----------------------------------

        mask = torch.triu(
            torch.ones_like(attention_scores),
            diagonal=1
        ).bool()


        # -----------------------------------
        # Block Future Tokens
        # -----------------------------------

        attention_scores = attention_scores.masked_fill(
            mask,
            float("-inf")
        )


        # -----------------------------------
        # Masked Scores → Attention Weights
        # -----------------------------------

        attention_weights = torch.softmax(
            attention_scores,
            dim=-1
        )


        # -----------------------------------
        # Attention Weights × V
        # -----------------------------------

        attention_output = (
            attention_weights @ V
        )


        # -----------------------------------
        # Return Final Output
        # -----------------------------------

        return attention_output