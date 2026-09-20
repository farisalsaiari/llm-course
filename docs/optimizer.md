# AdamW Optimizer

SGD applies updates directly from the current gradient and was useful for learning backpropagation. Transformer training typically benefits from adaptive updates.

AdamW tracks moving averages of gradients and squared gradients. `beta1` controls gradient momentum, while `beta2` controls the second-moment estimate used to scale updates. AdamW decouples weight decay from the adaptive gradient update, making regularization easier to reason about than adding an L2 term inside Adam.

The local configuration uses:

```text
learning_rate = 3e-3
betas = (0.9, 0.95)
weight_decay = 0.01
```

This relatively high learning rate is for a very small educational model and corpus. It should be tuned with model scale, effective batch size, schedule, and validation behavior rather than copied into large-model training.
