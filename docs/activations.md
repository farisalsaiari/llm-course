# Transformer Activations

- **ReLU** computes `max(0, x)`. It is simple and cheap but has a hard corner and discards all negative activations.
- **GELU** smoothly weights values by their magnitude. GPT-style models commonly use it, and this project now uses it as the next clear step after ReLU.
- **SiLU / Swish** computes `x * sigmoid(x)`. It is another smooth activation used in modern networks.
- **SwiGLU** uses a learned SiLU gate over one projection and multiplies it by another projection. It often performs well in modern LLM FFNs but changes both the FFN structure and parameter-count calculation.

GELU keeps the current two-linear-layer FFN easy to inspect:

```text
C -> multiplier*C -> GELU -> C
```

SwiGLU is a sensible later experiment after this baseline is trained on enough data to compare architectures meaningfully.
