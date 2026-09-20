# JSM LLM Upgrade Final Report

## 1. Original Architecture

JSM began as a two-token educational model: whitespace words -> embeddings -> single-head attention -> post-norm residual/FFN blocks -> flatten the full sequence -> one vocabulary prediction. Training used manually assembled pairs, SGD, and component-level checkpoints.

## 2. Problems Found

The flatten shortcut prevented per-position language modeling. Sequence length was fixed, batching was absent, tokenization could not handle unseen words, attention had one head, inference predicted once, evaluation reused tiny training patterns, and checkpoints could not fully resume optimization.

## 3. What Changed

The project now implements per-token causal logits, shifted targets, variable bounded contexts, batches, local training windows, Dataset/DataLoader, pure-Python Byte-Level BPE, manual MHA/GQA/MQA, pre-norm blocks, GELU, dropout, generation/sampling, KV caching, AdamW/scheduling/clipping, full checkpoints, devices/precision, validation/evaluation, tests, debugging, and scaling tools.

## 4. Final Architecture

```text
Local documents
  -> from-scratch Byte-Level BPE
  -> document-aware shifted windows [B,T]
  -> tied token embeddings + learned positions [B,T,C]
  -> dropout
  -> pre-norm Transformer block x N
       -> LayerNorm
       -> manual causal MHA/GQA/MQA
       -> residual
       -> LayerNorm
       -> Linear -> GELU -> Linear FFN
       -> residual
  -> final LayerNorm
  -> tied LM head
  -> logits [B,T,V]
  -> shifted cross-entropy
  -> backward -> clipping -> AdamW -> LR schedule
```

## 5. Tokenizer Design

`subword_tokenizer.py` owns UTF-8 byte initialization, pair counting, deterministic BPE merge learning, encoding, decoding, special tokens, and JSON persistence. It uses no Hugging Face, SentencePiece, pretrained tokenizer, or tokenizer dependency. PyTorch remains the tensor/autograd/device framework; JSM does not reimplement PyTorch itself.

## 6. Dataset Pipeline

Documents remain separate. Deterministic train/validation splitting happens before shifted overlapping windows are built. `LanguageModelDataset` returns long tensors and `DataLoader` batches/shuffles training windows without cross-document transitions.

## 7. Multi-Head Attention

Q/K/V projections, head reshaping, scaled scores, causal masking, softmax, head merge, and output projection are manually implemented. Configurable KV heads support MHA (`K=H`), GQA (`1<K<H`), and MQA (`K=1`).

## 8. Context Window

`max_seq_len` controls learned positional capacity and rejects overflow. Vanilla training attention remains approximately `O(T^2)`. Cached generation rebuilds from the newest window when learned positions fill.

## 9. Batching

Inputs/targets are `[B,T]`, hidden states `[B,T,C]`, attention scores `[B,H,T,T]`, and logits `[B,T,V]`. Loss covers all valid batch/sequence positions.

## 10. Shifted Training

For tokens `A B C D`, input is `A B C`, target is `B C D`, and every position contributes to cross-entropy. Training uses AdamW, linear warmup, cosine decay, global norm clipping, optional dropout, and device-aware tensors.

## 11. Generation

Autoregressive generation encodes a prompt, selects final-position logits, appends one token, respects EOS/context/max-new-token limits, and repeats. KV caching avoids recomputing old K/V projections.

## 12. Sampling

Generation supports greedy decoding through temperature zero, positive temperature scaling, top-k filtering, and mathematically ordered top-p nucleus filtering with configuration validation.

## 13. Parameter Count

Utilities report unique total/trainable parameters and component breakdowns while handling tied weights. Formula-only scale configs estimate Tiny 35,628; Mini 6,854,464; conceptual 100M 96,243,968; conceptual 1B 980,262,144.

## 14. Training System

Training supports MPS/CUDA/CPU selection, FP32 default, guarded CUDA autocast, AdamW, warmup/cosine scheduling, clipping, train/eval modes, parameter reporting, validation loss, and perplexity.

## 15. Checkpoint/Resume

Checkpoints store full model, optimizer, scheduler, epoch, global step, and model config. Inference rebuilds architecture from config. Resume works across supported map locations; exact DataLoader RNG replay is not yet stored.

## 16. Device Support

Selection order is CUDA -> MPS -> CPU. Models, batches, targets, inference IDs, and checkpoint tensors are colocated. Local verification used MPS. CUDA performance was not claimed without measurement.

## 17. Evaluation

`evaluate.py` reports token-weighted validation loss, perplexity, next-token accuracy, token count, and deterministic generation samples. A synthetic lesson demonstrates near-zero training loss alongside worsening validation loss.

## 18. Current Limitations

- The eight-document corpus remains far too small for broad language ability.
- Learned absolute positions remain; RoPE is documented but not implemented.
- FP16 gradient scaling is not implemented; FP32 is the safe local default.
- Training attention is dense quadratic attention without optimized kernels.
- Resume does not preserve DataLoader/RNG position exactly.
- Validation is useful for pipeline behavior but still statistically small.
- PyTorch is a required external framework for tensors, autograd, optimizers, and hardware kernels; LLM/tokenizer mechanisms are project-owned.

## 19. Educational Versus Production-Ready

The model is production-shaped but educational-scale. Core math and data flow are explicit and tested. Production training additionally needs much larger licensed/clean data, optimized kernels, robust distributed execution, experiment tracking, security, contamination checks, broader evaluation, and operational monitoring.

## 20. Path Toward A Real 1B Model

The verified conceptual configuration uses 32K vocabulary, width 2048, 18 layers, 16 heads, FFN 8192, context 4096, and tied embeddings for 980,262,144 parameters. The full assumption-labeled plan is in `docs/1b_training_plan.md`: 20B-token planning target, preprocessing/packing, compute formula, VRAM/state accounting, microbatch/accumulation example, BF16, sharding choices, checkpoints, validation, evaluation, and inference. No 1B model was instantiated locally.

## Verification

- Full Python tree compiles.
- Five automated pipeline tests pass.
- Cached and uncached logits agree within floating-point tolerance.
- Root and `jsm/` entry points work.
- Shape and scale reports pass asserted dimensions/ranges.
- Detailed evidence for every phase is preserved in `LLM_UPGRADE_PROGRESS.md`.
