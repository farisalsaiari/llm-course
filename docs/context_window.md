# Context Window

The context window is the maximum number of tokens the model can process in one sequence. In this project, `max_seq_len` sizes the learned positional embedding table and guards model inputs.

Examples such as 128, 4K, 8K, 32K, and 128K all describe token counts, not words or batch size. A longer window lets a model use more prior text, but it also increases positional capacity, activation memory, and compute.

Vanilla self-attention compares every token with every token. For sequence length `T`, its score matrix has shape `[T, T]`, so score storage and attention work grow approximately as `O(T^2)`:

| Tokens | Attention scores per head |
| ---: | ---: |
| 16 | 256 |
| 128 | 16,384 |
| 4,096 | 16,777,216 |
| 128,000 | 16,384,000,000 |

Batch size and attention heads multiply those score matrices. Other activations and optimizer state consume additional memory.

The executable educational configuration uses `max_seq_len=16` because the corpus is tiny and local development may run on an 8 GB MacBook. `128` is a reasonable later learning configuration after batching and data windows are in place. Contexts such as 128K require specialized positional methods, memory-efficient attention, substantial hardware, and suitable training data; changing one integer is not enough.

During inference, generation must crop old tokens when the running sequence exceeds `max_seq_len`. During training, each input window must be no longer than this limit.
