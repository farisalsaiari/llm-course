# Pre-Norm Transformer Blocks

The earlier educational block used post-norm:

```text
x = LayerNorm(x + Attention(x))
x = LayerNorm(x + FFN(x))
```

The production block now uses pre-norm:

```text
x = x + Attention(LayerNorm(x))
x = x + FFN(LayerNorm(x))
```

Pre-norm leaves a direct identity path through each residual branch, which generally improves gradient flow and makes deeper Transformer optimization more stable. A final LayerNorm is applied after the complete block stack and before the language-model head.

Post-norm remains useful for learning the original Transformer formulation, so lesson files are preserved.
