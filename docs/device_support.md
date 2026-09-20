# Device Support

Training and inference select devices in this order:

```text
CUDA -> MPS -> CPU
```

CUDA targets NVIDIA GPUs. MPS targets supported Apple Silicon GPUs. CPU is the universal fallback. Model parameters, input IDs, targets, and loaded checkpoint tensors must share one device; otherwise PyTorch raises a device-mismatch error.

DataLoader batches begin in CPU memory and are moved immediately before the forward pass. Checkpoints are loaded with `map_location=device`, so a checkpoint saved on one hardware type can be restored on another when its operations and dtypes are supported.
