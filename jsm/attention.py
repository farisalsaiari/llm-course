import torch
import torch.nn as nn


# -----------------------------------
# Causal Self-Attention
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


    def forward(self, vectors):

        # Embeddings → Q, K, V

        Q = self.query_layer(vectors)

        K = self.key_layer(vectors)

        V = self.value_layer(vectors)


        # Q × Kᵀ / √d_k

        d_k = K.shape[-1]

        attention_scores = (
            Q @ K.T
        ) / (d_k ** 0.5)


        # Causal Mask

        mask = torch.triu(
            torch.ones_like(attention_scores),
            diagonal=1
        ).bool()

        attention_scores = attention_scores.masked_fill(
            mask,
            float("-inf")
        )


        # Softmax

        attention_weights = torch.softmax(
            attention_scores,
            dim=-1
        )


        # Attention Weights × V

        attention_output = (
            attention_weights @ V
        )

        return attention_output