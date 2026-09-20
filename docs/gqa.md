# MHA, GQA, And MQA

All three use multiple query heads. They differ in how many key/value heads are projected and cached:

- MHA: `num_kv_heads == num_heads`; every query head has its own K/V head.
- GQA: `1 < num_kv_heads < num_heads`; groups of query heads share K/V heads.
- MQA: `num_kv_heads == 1`; every query head shares one K/V head.

For `H=8` query heads and `K=2` KV heads, each KV head is repeated for four query heads before score calculation. Output shape remains `[B,T,C]`, while K/V projection parameters and future KV-cache memory shrink.

GQA primarily improves autoregressive inference efficiency. It does not remove the quadratic training attention matrix, and fewer KV heads can trade representational capacity for speed/memory. The local default leaves `num_kv_heads=None`, meaning ordinary MHA.
