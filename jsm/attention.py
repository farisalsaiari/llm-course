import torch
import torch.nn as nn


# -----------------------------------
# Causal Self-Attention
# -----------------------------------

class SelfAttention(nn.Module):

    def __init__(
        self,
        embedding_dim,
        num_heads=1,
        num_kv_heads=None,
        dropout=0.0
    ):

        super().__init__()

        if embedding_dim % num_heads != 0:
            raise ValueError(
                "embedding_dim must be divisible by num_heads."
            )

        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads or num_heads

        if self.num_heads % self.num_kv_heads != 0:
            raise ValueError("num_kv_heads must divide num_heads.")

        self.head_dim = embedding_dim // num_heads
        kv_dim = self.num_kv_heads * self.head_dim

        self.query_layer = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.key_layer = nn.Linear(
            embedding_dim,
            kv_dim,
            bias=False
        )

        self.value_layer = nn.Linear(
            embedding_dim,
            kv_dim,
            bias=False
        )

        self.output_projection = nn.Linear(
            embedding_dim,
            embedding_dim,
            bias=False
        )

        self.attention_dropout = nn.Dropout(dropout)


    def forward(self, vectors, cache=None, use_cache=False):

        single_sequence = vectors.dim() == 2

        if single_sequence:
            vectors = vectors.unsqueeze(0)

        batch_size, sequence_length, embedding_dim = vectors.shape

        # Embeddings → Q, K, V

        Q = self.query_layer(vectors)

        K = self.key_layer(vectors)

        V = self.value_layer(vectors)

        Q = Q.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim
        ).transpose(1, 2)

        K = K.view(
            batch_size,
            sequence_length,
            self.num_kv_heads,
            self.head_dim
        ).transpose(1, 2)

        V = V.view(
            batch_size,
            sequence_length,
            self.num_kv_heads,
            self.head_dim
        ).transpose(1, 2)

        past_length = 0

        if cache is not None:
            past_key, past_value = cache
            past_length = past_key.shape[-2]
            K = torch.cat([past_key, K], dim=-2)
            V = torch.cat([past_value, V], dim=-2)

        new_cache = (K, V)

        repeats = self.num_heads // self.num_kv_heads
        K = K.repeat_interleave(repeats, dim=1)
        V = V.repeat_interleave(repeats, dim=1)


        # Q × Kᵀ / √d_k

        attention_scores = (
            Q @ K.transpose(-2, -1)
        ) / (self.head_dim ** 0.5)


        # Causal Mask

        key_length = K.shape[-2]
        query_positions = torch.arange(
            sequence_length,
            device=vectors.device
        ) + past_length
        key_positions = torch.arange(
            key_length,
            device=vectors.device
        )
        mask = key_positions.unsqueeze(0) > query_positions.unsqueeze(1)

        attention_scores = attention_scores.masked_fill(
            mask,
            float("-inf")
        )


        # Softmax

        attention_weights = torch.softmax(
            attention_scores,
            dim=-1
        )

        attention_weights = self.attention_dropout(
            attention_weights
        )


        # Attention Weights × V

        attention_output = (
            attention_weights @ V
        )

        attention_output = attention_output.transpose(
            1,
            2
        ).contiguous().view(
            batch_size,
            sequence_length,
            embedding_dim
        )

        attention_output = self.output_projection(
            attention_output
        )

        if single_sequence:
            attention_output = attention_output.squeeze(0)

        if use_cache:
            return attention_output, new_cache

        return attention_output
