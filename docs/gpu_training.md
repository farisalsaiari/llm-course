# GPU Training Basics

Training data is read and tokenized in CPU RAM. A DataLoader creates CPU tensors, which are copied to GPU VRAM. The GPU runs the forward pass, stores activations needed by autograd, computes loss and gradients during backward, and applies optimizer updates. Checkpoints then move through host storage.

Major VRAM consumers are model parameters, gradients, AdamW's two moment tensors, saved forward activations, and attention matrices. For batch `B`, heads `H`, sequence `T`, and layers `L`, attention scores alone contain approximately `B*H*T*T*L` values. This quadratic `T*T` term is why context length can dominate memory.

`memory.estimate_training_memory()` reports transparent lower-bound components. It omits temporary kernels, allocator fragmentation, dataloader buffers, some autograd tensors, and mixed-precision master weights, so it must not be treated as an exact capacity calculator.

Rough FP32 parameter-state example: one billion parameters require about 4 GB for parameters, 4 GB for gradients, and 8 GB for AdamW moments before activations and temporary memory. Real training generally needs more memory and often shards states across GPUs.

The local MPS/CPU run validates correctness. NVIDIA throughput depends on GPU model, dtype, kernels, batch shape, and communication; no throughput claim is inferred from this MacBook.
