# Parameter Scale Experiments

`scale_report.py` compares configurations using formulas only. Tiny is the current near-instant learning model. Mini is larger but still intended for careful local experiments with modest batches. The ~100M and ~1B configurations are architecture exercises only and must not be instantiated on this MacBook.

Increasing width raises most block parameters quadratically. Increasing layers raises block parameters linearly. Vocabulary primarily affects token embeddings/LM head, while context affects positional parameters and, more importantly, activation and quadratic attention memory. Head count alone does not increase dense projection parameters when total width stays fixed.
