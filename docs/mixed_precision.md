# Mixed Precision

FP32 is the stable baseline. FP16 uses less memory and can accelerate supported CUDA hardware, but its narrow numeric range often requires gradient scaling. BF16 keeps FP32-like exponent range with fewer mantissa bits and is usually easier to train when the GPU supports it.

This project defaults to FP32 everywhere. `--precision fp16` and `--precision bf16` enable CUDA autocast only; unsupported CPU/MPS requests fail clearly rather than silently changing numerics. FP16 optimizer scaling is deliberately not enabled yet, so FP16 remains an architecture-ready experimental path rather than the recommended training mode. CUDA BF16 support is checked at runtime.

Local Apple Silicon testing remains FP32. Production NVIDIA training should validate loss stability, operation support, gradient scaling for FP16, and throughput before selecting a dtype.
