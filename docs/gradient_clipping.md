# Gradient Clipping

Deep networks can occasionally produce very large gradients. Those gradients can cause unstable parameter updates, exploding loss, or NaNs.

After `loss.backward()` and before `optimizer.step()`, training now clips the global L2 norm of all parameter gradients to `1.0`:

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
```

If the norm is already below the threshold, gradients are unchanged. If it is above the threshold, all gradients are scaled together, preserving their relative direction. Clipping is a stability guard, not a replacement for a suitable learning rate, initialization, normalization, or clean data.
