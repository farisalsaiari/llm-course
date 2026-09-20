import torch


@torch.no_grad()
def inspect_shapes(model, token_ids):

    if token_ids.dim() == 1:
        batch_size = 1
        sequence_length = token_ids.shape[0]
    elif token_ids.dim() == 2:
        batch_size, sequence_length = token_ids.shape
    else:
        raise ValueError("token_ids must have shape [T] or [B,T].")

    config = model.config
    head_dim = config.embedding_dim // config.num_heads
    kv_heads = config.num_kv_heads or config.num_heads
    logits = model(token_ids)

    return {
        "tokens": tuple(token_ids.shape),
        "embeddings": (
            batch_size,
            sequence_length,
            config.embedding_dim
        ),
        "queries": (
            batch_size,
            config.num_heads,
            sequence_length,
            head_dim
        ),
        "keys_values": (
            batch_size,
            kv_heads,
            sequence_length,
            head_dim
        ),
        "attention_scores": (
            batch_size,
            config.num_heads,
            sequence_length,
            sequence_length
        ),
        "attention_output": (
            batch_size,
            sequence_length,
            config.embedding_dim
        ),
        "hidden": (
            batch_size,
            sequence_length,
            config.embedding_dim
        ),
        "logits": tuple(logits.shape)
    }
