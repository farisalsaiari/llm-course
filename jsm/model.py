import torch
import torch.nn as nn

from config import ModelConfig
from transformer_block import TransformerBlock


class TinyModel(nn.Module):

    def __init__(self, config: ModelConfig):
        super().__init__()

        self.config = config


        # -----------------------------------
        # Token Embedding
        # -----------------------------------

        self.embedding = nn.Embedding(
            num_embeddings=config.vocab_size,
            embedding_dim=config.embedding_dim
        )


        # -----------------------------------
        # Position Embedding
        # -----------------------------------

        self.position_embedding = nn.Embedding(
            num_embeddings=config.max_seq_len,
            embedding_dim=config.embedding_dim
        )

        self.max_seq_len = config.max_seq_len
        self.embedding_dropout = nn.Dropout(config.dropout)


        # -----------------------------------
        # Transformer Blocks
        # -----------------------------------

        self.blocks = nn.ModuleList([
            TransformerBlock(
                embedding_dim=config.embedding_dim,
                num_heads=config.num_heads,
                num_kv_heads=config.num_kv_heads,
                ffn_multiplier=config.ffn_multiplier,
                dropout=config.dropout
            )
            for _ in range(config.num_layers)
        ])

        self.final_norm = nn.LayerNorm(
            config.embedding_dim
        )


        # -----------------------------------
        # Language Model Head
        #
        # One vocabulary prediction per token
        # -----------------------------------

        self.lm_head = nn.Linear(
            config.embedding_dim,
            config.vocab_size
        )

        if config.tie_embeddings:
            self.lm_head.weight = self.embedding.weight


    # -----------------------------------
    # Forward Pass
    # -----------------------------------

    def forward(self, token_ids, caches=None, use_cache=False):

        if token_ids.dim() not in (1, 2):
            raise ValueError(
                "token_ids must have shape [T] or [B, T]."
            )

        sequence_length = token_ids.shape[-1]
        past_length = 0

        if caches:
            past_length = caches[0][0].shape[-2]

        if sequence_length + past_length > self.max_seq_len:
            raise ValueError(
                "Sequence length "
                f"{sequence_length + past_length} exceeds max_seq_len "
                f"{self.max_seq_len}."
            )


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
            past_length,
            past_length + sequence_length,
            device=token_ids.device
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

        context_vectors = self.embedding_dropout(
            context_vectors
        )


        # -----------------------------------
        # Pass Through Transformer Blocks
        # -----------------------------------

        transformer_output = context_vectors

        new_caches = []

        for index, block in enumerate(self.blocks):

            block_cache = caches[index] if caches else None
            block_result = block(
                transformer_output,
                cache=block_cache,
                use_cache=use_cache
            )

            if use_cache:
                transformer_output, new_cache = block_result
                new_caches.append(new_cache)
            else:
                transformer_output = block_result

        transformer_output = self.final_norm(
            transformer_output
        )


        # -----------------------------------
        # Per-Token Vocabulary Logits
        # -----------------------------------

        logits = self.lm_head(
            transformer_output
        )


        if use_cache:
            return logits, new_caches

        return logits
