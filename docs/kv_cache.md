# KV Cache

Without caching, autoregressive generation sends the complete prefix through every layer for every new token. Old keys and values are projected repeatedly.

With a KV cache, each attention layer stores K/V tensors shaped `[B, K, T, D]`, where `K` is the number of KV heads. The next step projects only the new token, appends its K/V values, and attends its query over cached history. GQA and MQA reduce cache size by using fewer KV heads.

The cache changes inference compute, not model weights. Training still processes full sequences in parallel and does not use the cache. When learned-position context becomes full, generation discards the cache and rebuilds it from the most recent context window so positions remain valid.

Cached and uncached logits should match in evaluation mode up to floating-point tolerance. The implementation tests that invariant directly.
