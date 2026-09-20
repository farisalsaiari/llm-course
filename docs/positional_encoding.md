# Positional Representations

Self-attention alone does not know token order. The model needs a positional representation.

## Learned Absolute Embeddings

The current model learns one vector for each position from `0` through `max_seq_len - 1` and adds it to the token embedding. This is simple, trainable, and appropriate for the educational model. Its table has shape `[max_seq_len, embedding_dim]`, and positions beyond that table are unsupported.

## Sinusoidal Encoding

Sinusoidal encoding adds fixed sine/cosine patterns at different frequencies. It introduces no learned position parameters and gives positions structured relative patterns, although it is not the dominant choice in many current decoder LLMs.

## RoPE

Rotary Position Embeddings rotate pairs of query and key channels according to position before attention scores are computed. RoPE therefore belongs inside attention, after Q/K projection and before `Q @ K^T`; it is not simply added to token embeddings. It represents relative offsets naturally and is common in modern decoder models.

A later RoPE migration should:

1. Require an even head dimension.
2. Precompute or cache inverse frequencies.
3. Rotate Q and K for every batch, head, and position.
4. Remove learned absolute position addition only after equivalence tests pass.
5. Define explicit behavior when inference extends beyond the training context.

For now, learned absolute embeddings remain the clearest working choice. RoPE would improve architectural modernity, but it would not make the tiny corpus or local training setup inherently capable of very long contexts.
