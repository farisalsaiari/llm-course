def estimate_decoder_parameters(
    vocab_size,
    max_seq_len,
    embedding_dim,
    num_layers,
    ffn_multiplier=4,
    tie_embeddings=True,
    learned_positions=True
):

    token_embedding = vocab_size * embedding_dim
    position_embedding = (
        max_seq_len * embedding_dim
        if learned_positions
        else 0
    )
    attention_per_layer = 4 * embedding_dim * embedding_dim
    ffn_per_layer = (
        2 * ffn_multiplier * embedding_dim * embedding_dim
        + (ffn_multiplier + 1) * embedding_dim
    )
    norms_per_layer = 4 * embedding_dim
    blocks = num_layers * (
        attention_per_layer
        + ffn_per_layer
        + norms_per_layer
    )
    final_norm = 2 * embedding_dim
    lm_head = vocab_size

    if not tie_embeddings:
        lm_head += vocab_size * embedding_dim

    components = {
        "token_embedding": token_embedding,
        "position_embedding": position_embedding,
        "transformer_blocks": blocks,
        "final_norm": final_norm,
        "lm_head": lm_head
    }
    components["total"] = sum(components.values())

    return components
