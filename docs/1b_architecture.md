# Conceptual Dense 1B Architecture

This is a verified architecture estimate, not a local training configuration:

```text
vocabulary_size = 32,000
hidden_size = 2,048
layers = 18
attention_heads = 16
head_dimension = 128
FFN_dimension = 8,192
context_length = 4,096
tied_embeddings = true
```

With learned absolute positions and the current dense GELU block formula, this is approximately 980 million parameters. Replacing learned positions with RoPE removes about 8.4 million parameters. Real architecture choices may use RMSNorm, SwiGLU, RoPE, no linear biases, and GQA, which change the exact total.

The estimate is computed without constructing tensors. Training it locally is prohibited: parameters, gradients, AdamW states, activations, and attention matrices exceed this MacBook's practical capacity. A real training design also requires a sufficiently large cleaned token corpus, validation, distributed state management, mixed precision, efficient attention kernels, and repeatable checkpoints.

Parameter labels must come from a formula or instantiated count. Calling a configuration "1B" based only on layer count is not acceptable.
