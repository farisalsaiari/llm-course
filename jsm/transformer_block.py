import torch.nn as nn

from attention import SelfAttention
from feed_forward import FeedForward


# -----------------------------------
# Transformer Block
# -----------------------------------

class TransformerBlock(nn.Module):

    def __init__(
        self,
        embedding_dim,
        num_heads=1,
        num_kv_heads=None,
        ffn_multiplier=4,
        dropout=0.0
    ):

        super().__init__()


        # -----------------------------------
        # Self-Attention
        # -----------------------------------

        self.attention = SelfAttention(
            embedding_dim=embedding_dim,
            num_heads=num_heads,
            num_kv_heads=num_kv_heads,
            dropout=dropout
        )


        # -----------------------------------
        # First LayerNorm
        # -----------------------------------

        self.layer_norm_1 = nn.LayerNorm(
            embedding_dim
        )


        # -----------------------------------
        # Feed-Forward Network
        # -----------------------------------

        self.feed_forward = FeedForward(
            embedding_dim=embedding_dim,
            ffn_multiplier=ffn_multiplier,
            dropout=dropout
        )

        self.residual_dropout = nn.Dropout(dropout)


        # -----------------------------------
        # Second LayerNorm
        # -----------------------------------

        self.layer_norm_2 = nn.LayerNorm(
            embedding_dim
        )


    # -----------------------------------
    # Forward
    # -----------------------------------

    def forward(self, vectors, cache=None, use_cache=False):


        # -----------------------------------
        # First Pre-Norm
        # -----------------------------------

        normalized_1 = self.layer_norm_1(
            vectors
        )


        # -----------------------------------
        # Self-Attention + Residual
        # -----------------------------------

        attention_result = self.attention(
            normalized_1,
            cache=cache,
            use_cache=use_cache
        )

        if use_cache:
            attention_output, new_cache = attention_result
        else:
            attention_output = attention_result

        residual_1 = (
            vectors +
            self.residual_dropout(attention_output)
        )


        # -----------------------------------
        # Second Pre-Norm
        # -----------------------------------

        normalized_2 = self.layer_norm_2(
            residual_1
        )


        # -----------------------------------
        # Feed-Forward Network
        # -----------------------------------

        ffn_output = self.feed_forward(
            normalized_2
        )


        # -----------------------------------
        # Second Residual Connection
        # -----------------------------------

        output = (
            residual_1 +
            self.residual_dropout(ffn_output)
        )


        if use_cache:
            return output, new_cache

        return output
