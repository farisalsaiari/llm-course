# Parameter Counting

Parameters are learned tensor values. Token and LM-head parameters scale with vocabulary size `V` and width `C`; positional embeddings scale with context `T` and width; each dense attention projection scales approximately with `C^2`; and FFN parameters scale approximately with `ffn_multiplier * C^2`.

For each block in this implementation:

- Q, K, V, and attention output projections contribute `4 * C^2` weights.
- The two FFN projections dominate at roughly `2 * ffn_multiplier * C^2` weights.
- LayerNorm and bias vectors add smaller terms proportional to `C`.

More layers repeat the whole block cost. Increasing attention heads while keeping total `C` fixed changes how channels are partitioned but does not increase Q/K/V projection parameter counts. Increasing `C` does, approximately quadratically.

`utils.count_parameters()` reports both total and trainable parameters. `utils.parameter_breakdown()` groups counts by the model's top-level components.

The default configuration ties `lm_head.weight` to `embedding.weight`. Input tokens and output vocabulary scores therefore learn one shared `[V,C]` matrix instead of two independent matrices, reducing unique parameter count by `V * C`. The state dictionary still exposes both named paths, but PyTorch's parameter iterator counts the shared object once.
