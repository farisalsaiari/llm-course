# Distributed Training Basics

## One GPU

Use one process and one full model replica. Increase utilization with batching, mixed precision, gradient accumulation, and efficient kernels before adding distributed complexity.

## Multiple GPUs, One Machine

**DistributedDataParallel (DDP)** gives each GPU a complete model and a different data shard. Gradients are averaged after backward. It improves throughput but does not make a model fit if one full replica already exceeds a GPU's memory.

**FSDP** and DeepSpeed ZeRO shard parameters, gradients, and/or optimizer states. They reduce per-GPU state memory at the cost of communication and more complex checkpointing.

## Model Too Large For One GPU

**Tensor parallelism** splits large matrix operations across devices. **Pipeline parallelism** assigns groups of layers to different devices and passes microbatches through stages. Large training systems often combine data, tensor, pipeline, and state-sharding strategies.

## Multiple Machines

Multi-node training adds network bandwidth, topology, process launch, failure recovery, and distributed checkpoint concerns. Fast interconnects matter because collective communication can dominate compute.

## Practical Scale Guide

| Scale | Typical first approach |
| --- | --- |
| Fits one GPU | Single process |
| Fits one GPU, needs throughput | DDP |
| Optimizer/model state does not fit | FSDP or ZeRO |
| Individual layers/matrices do not fit | Tensor parallelism |
| Many layers across devices | Pipeline parallelism |
| 1B parameters | One high-memory GPU may handle inference; training often uses state sharding depending on context/batch/precision |
| 7B+ | Multi-GPU sharding is normally required for full training |
| 30B+ | Multi-node combinations are common |

These are engineering guides, not fixed thresholds. Dtype, optimizer, sequence length, batch size, activation checkpointing, and hardware determine the actual boundary. The local project intentionally does not initialize process groups or add FSDP/DeepSpeed dependencies.
