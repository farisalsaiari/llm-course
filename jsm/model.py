import torch
import torch.nn as nn

from attention import SelfAttention


class TinyModel(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim=3,
        context_size=2
    ):
        super().__init__()


        # -----------------------------------
        # Token Embedding
        # -----------------------------------

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim
        )


        # -----------------------------------
        # Position Embedding
        # -----------------------------------

        self.position_embedding = nn.Embedding(
            num_embeddings=context_size,
            embedding_dim=embedding_dim
        )


        # -----------------------------------
        # Self-Attention
        # -----------------------------------

        self.attention = SelfAttention(
            embedding_dim=embedding_dim
        )


        # -----------------------------------
        # Output Layer
        #
        # 2 tokens × 3 values
        # = 6 input values
        # -----------------------------------

        self.output_layer = nn.Linear(
            context_size * embedding_dim,
            vocab_size
        )


    # -----------------------------------
    # Forward Pass
    # -----------------------------------

    def forward(self, token_ids):


        # -----------------------------------
        # Token IDs → Token Embeddings
        # -----------------------------------

        token_vectors = self.embedding(
            token_ids
        )


        # -----------------------------------
        # Create Positions
        #
        # [0, 1]
        # -----------------------------------

        positions = torch.arange(
            len(token_ids)
        )


        # -----------------------------------
        # Positions → Position Embeddings
        # -----------------------------------

        position_vectors = self.position_embedding(
            positions
        )


        # -----------------------------------
        # Token Meaning + Position
        # -----------------------------------

        context_vectors = (
            token_vectors +
            position_vectors
        )


        # -----------------------------------
        # Context → Self-Attention
        #
        # 2 × 3
        # ↓
        # 2 × 3
        # -----------------------------------

        attention_output = self.attention(
            context_vectors
        )


        # -----------------------------------
        # Residual Connection
        #
        # Original Context
        # +
        # Attention Output
        # -----------------------------------

        residual_output = (
            context_vectors +
            attention_output
        )


        # -----------------------------------
        # Keep Token Order
        #
        # 2 × 3
        # ↓
        # 6 values
        # -----------------------------------

        context_vector = (
            residual_output.flatten()
        )


        # -----------------------------------
        # Context → Vocabulary Logits
        # -----------------------------------

        logits = self.output_layer(
            context_vector
        )


        return logits