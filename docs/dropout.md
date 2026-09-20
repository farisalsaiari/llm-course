# Dropout

Dropout randomly zeros activations during training and rescales the survivors. This discourages fragile co-adaptation and can reduce overfitting. In evaluation mode it becomes an identity operation.

The model supports one configurable rate for embedding dropout, attention-weight dropout, FFN dropout, and residual-branch dropout. The tiny corpus uses `dropout=0.0` because its purpose is to demonstrate fitting; random regularization can obscure that lesson. Larger datasets can use a small nonzero value.

Always use:

- `model.train()` while optimizing, so dropout is active.
- `model.eval()` for validation and generation, so outputs are deterministic.
