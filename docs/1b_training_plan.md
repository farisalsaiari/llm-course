# Realistic Dense 1B Training Plan

## Scope

This is a production planning exercise. It must not be run on the local MacBook. Every numerical budget below is an explicit estimate, not measured throughput or a purchasing promise.

## Architecture

The current dense-decoder formula gives 980,262,144 parameters:

```text
vocabulary             32,000 Byte-Level BPE tokens
hidden width            2,048
layers                     18
query heads                 16
head dimension              128
FFN width                  8,192
context                    4,096
embedding/LM head          tied
normalization              pre-norm + final norm
position                   learned in exact estimate; prefer tested RoPE for production
```

A production variant should evaluate RMSNorm, RoPE, SwiGLU, GQA, and efficient attention. Those changes require a fresh exact parameter calculation.

## Tokenizer

Train the project's own Byte-Level BPE on a representative training-only sample. A 32K vocabulary is the planning assumption. Freeze and version the tokenizer before model training; changing token IDs invalidates embeddings and checkpoints. Reserve document boundary and padding/control tokens deliberately.

## Data Target And Storage

Planning assumption: 20 billion cleaned training tokens, roughly 20 tokens per parameter. This is a scaling heuristic, not a guaranteed optimum.

- Packed token IDs as uint32: about 80 GB (`20B * 4 bytes`).
- Raw/clean text: assume roughly 5-15 bytes per token after metadata/compression choices, giving approximately 100-300 GB. Measure the real corpus instead of relying on this range.
- Keep raw, normalized, deduplicated, tokenized, validation, and audit manifests as separately versioned stages.

Data processing should normalize encoding, remove corruption, deduplicate exact and near duplicates, filter quality/safety issues, detect language/domain, preserve source/license metadata, and prevent validation/test contamination.

## Sequence Packing

Tokenize documents independently, append EOS, then pack documents into 4,096-token training sequences. Record boundaries so evaluation can remain document-aware. Packing reduces padding waste; it must not silently erase boundary semantics. Shuffle at shard/document/sequence levels with reproducible seeds.

## Compute Estimate

A common dense-Transformer approximation is `6 * parameters * training_tokens` FLOPs:

```text
6 * 1B * 20B = 1.2e20 FLOPs
```

Duration estimate:

```text
seconds = total_FLOPs / (GPU_count * sustained_FLOPs_per_GPU)
```

Illustrative assumption only: if each GPU sustains 100 TFLOP/s on this workload, one GPU is about 333 hours and eight GPUs about 42 hours before communication, validation, checkpoint, failure, and input-pipeline overhead. Actual sustained utilization must be benchmarked on the chosen stack.

## GPU And VRAM Planning

Approximate 1B-model state before activations:

- BF16 parameters: 2 GB.
- BF16 gradients: 2 GB.
- FP32 AdamW moments: 8 GB.
- Optional FP32 master weights: 4 GB.
- Total state: roughly 12-16 GB, depending on optimizer implementation.

Activations, attention, temporary kernels, allocator fragmentation, and communication buffers add substantial memory. A 24 GB GPU may require microbatch one, activation checkpointing, efficient attention, and/or optimizer sharding. 48-80 GB devices offer more margin. Multi-GPU FSDP/ZeRO is recommended when state plus desired batch/context does not fit safely.

## Batch And Gradient Accumulation

Planning example: global batch 524,288 tokens = 128 sequences of length 4,096. With eight GPUs, microbatch one sequence per GPU and 16 accumulation steps reaches that global batch:

```text
8 GPUs * 1 sequence * 4,096 tokens * 16 steps = 524,288 tokens
```

This is an example, not an optimal batch claim. Tune using stability, throughput, and validation. LR schedules should be expressed in optimizer steps or consumed tokens.

## Precision And Optimization

Prefer BF16 on supported accelerators; use FP16 only with tested gradient scaling. Keep numerically sensitive operations in suitable precision. Start with AdamW, warmup, cosine decay, gradient clipping, and decoupled weight decay, then tune on short controlled runs. Use activation checkpointing to trade extra compute for memory.

## Distributed Strategy

Start with DDP if one full training state fits each GPU. Use FSDP/ZeRO to shard parameters, gradients, and optimizer state when it does not. Add tensor or pipeline parallelism only if individual model components or layer stacks require it; unnecessary parallel dimensions increase communication and failure modes.

## Checkpoints And Resume

Save model, optimizer, scheduler, scaler, consumed tokens, global step, config, tokenizer hash/version, data-shard state, RNG states, and code revision. A BF16 weights-only file is roughly 2 GB. Full AdamW resume state is roughly 12-16 GB before serialization overhead and distributed sharding metadata. Save atomically, retain periodic and milestone checkpoints, and test restore on a separate job.

## Validation And Evaluation

Maintain immutable, deduplicated validation data across key domains. Track token-weighted loss and perplexity, but also controlled next-token tasks, generation suites, memorization/privacy checks, toxicity/bias/safety tests, and downstream benchmarks appropriate to intended use. Evaluate checkpoints throughout training, not only at the end.

## Inference

BF16 weights require roughly 2 GB before runtime buffers and KV cache. KV-cache memory scales with layers, batch, context, head dimension, and KV heads; GQA reduces it. Benchmark prompt processing and token generation separately. Quantization can reduce memory but requires quality evaluation.

## Recommended Execution Sequence

1. Freeze tokenizer/data manifests and run contamination checks.
2. Validate architecture and loss on Tiny/Mini configs.
3. Run a short 1B systems smoke test on synthetic data.
4. Benchmark memory, throughput, and dataloader saturation.
5. Run a small token-budget pilot and inspect loss/generation.
6. Test checkpoint interruption and restore.
7. Launch full training with monitoring and periodic validation.
8. Preserve final and intermediate checkpoints for evaluation.

This plan scales the same mechanisms implemented in JSM; production success additionally depends on data engineering, optimized kernels, distributed reliability, security, and rigorous evaluation.
