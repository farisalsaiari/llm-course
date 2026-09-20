# LLM Upgrade Handoff Report

## Repository

- Project root: `/Users/farisalsaiari/Desktop/Learning/llm-course`
- Production code: `jsm/`
- Detailed phase ledger: `LLM_UPGRADE_PROGRESS.md`
- Completed roadmap phases: 1-40
- Exact continuation point: roadmap complete; use `LLM_UPGRADE_REPORT.md`.
- Git state: upgrade work is uncommitted; preserve all existing changes.

## Original State

The model was an educational decoder with whitespace tokenization, fixed two-token contexts, one sequence at a time, single-head attention, post-norm blocks, ReLU, SGD, manually saved component weights, and one prediction produced by flattening the complete sequence.

## Current Architecture

```text
Local raw documents
-> pure-Python, from-scratch Byte-Level BPE tokenizer
-> document-aware shifted token windows
-> Dataset and shuffled DataLoader batches [B,T]
-> tied token embeddings [B,T,C]
-> learned absolute positional embeddings
-> embedding dropout
-> pre-norm TransformerBlock x N
   -> LayerNorm
   -> manual multi-head causal self-attention
   -> residual
   -> LayerNorm
   -> Linear -> GELU -> Linear FFN
   -> residual
-> final LayerNorm
-> tied LM head
-> per-token logits [B,T,V]
-> shifted cross-entropy targets [B,T]
```

Default local model configuration:

- `max_seq_len=16`
- `embedding_dim=32`
- `num_heads=4`
- `num_layers=2`
- `ffn_multiplier=4`
- `dropout=0.0`
- tied input/output embeddings
- current BPE vocabulary: 275 tokens
- current unique parameter count: 34,803

## Completed Work

1. Removed full-sequence flattening and added per-token `[B,T,V]` vocabulary logits.
2. Added shifted causal targets so every position predicts the next token.
3. Replaced fixed two-token architecture assumptions with `max_seq_len`.
4. Added and documented a bounded context window and `O(T^2)` attention scaling.
5. Implemented multi-head causal self-attention manually, including Q/K/V split, masking, merge, and output projection.
6. Added full batch support across model, attention, logits, targets, and loss.
7. Added overlapping/chunked document-aware training windows without cross-document transitions.
8. Added `LanguageModelDataset` and PyTorch `DataLoader`.
9. Implemented and trained Byte-Level BPE from scratch in pure Python; no Hugging Face, SentencePiece, pretrained tokenizer, or tokenizer dependency is used.
10. Added autoregressive text generation with EOS and context truncation.
11. Added greedy, temperature, top-k, and top-p decoding.
12. Added validated `ModelConfig` and centralized architecture settings.
13. Added total/trainable parameter counting and unique component breakdowns.
14. Added GPT-style embedding/LM-head weight tying.
15. Documented learned positions, sinusoidal encoding, and a safe RoPE migration path.
16. Refactored production blocks from post-norm to pre-norm and added final LayerNorm.
17. Replaced ReLU with GELU; documented SiLU and SwiGLU.
18. Added configurable embedding, attention, FFN, and residual dropout.
19. Replaced SGD with AdamW (`lr=3e-3`, betas `(0.9,0.95)`, weight decay `0.01`).
20. Added linear warmup plus cosine LR decay.
21. Added global gradient clipping at norm `1.0`.
22. Added full resumable checkpoints with model/optimizer/scheduler/config/epoch/global step.
23. Added CUDA -> MPS -> CPU device selection and consistent tensor placement.
24. Added explicit FP32/FP16/BF16 selection; FP32 is local default, mixed precision is CUDA-only and guarded.

## Main Files Added

- `jsm/config.py`: validated model configuration.
- `jsm/dataset.py`: shifted language-model Dataset.
- `jsm/subword_tokenizer.py`: from-scratch byte initialization, pair counting, merge learning, encoding, decoding, and JSON persistence.
- `jsm/generation.py`: autoregressive generation and sampling.
- `jsm/checkpoint.py`: full save/load/resume helpers.
- `jsm/device.py`: runtime device selection.
- `jsm/precision.py`: guarded autocast contexts.
- `jsm/training_utils.py`: warmup/cosine schedule math.
- `jsm/utils.py`: parameter counts.
- `docs/*.md`: focused teaching notes for phases 4 and 9-24.

Existing educational files under `jsm/lessons/` and the old whitespace `jsm/tokenizer.py` were preserved.

## Important Tests Passed

- Per-token shape: `[4] -> [4,100]`; batched shape: `[3,5] -> [3,5,13]`.
- Four-head attention shapes: Q/K/V `[2,4,5,2]`, scores `[2,4,5,5]`, output `[2,5,8]`.
- Causal isolation: changing a future token did not change earlier outputs.
- Shifted cross-entropy and backward gradients passed.
- Sequence lengths up to the configured maximum passed; overflow raised `ValueError`.
- Dataset full/partial batches and document-boundary preservation passed.
- BPE encode/decode round-trip passed.
- Greedy, top-k, top-p, and invalid sampling configuration tests passed.
- Hand-derived parameter count matched code exactly.
- Weight tying reduced parameters by exactly `V*C`.
- Zeroed pre-norm branches produced an exact residual identity and identity gradient.
- Dropout was stochastic in `train()` and deterministic in `eval()`.
- AdamW reduced toy loss from about 18.23 to below 0.4.
- LR warmup/cosine endpoints passed exact checks.
- Artificial gradient norm around 84,024 clipped to 1.0.
- Checkpoint resume advanced epoch 49/step 150 to epoch 51/step 156.
- Local model/input/output all ran on MPS (`mps:0`).
- FP32 training passed; unsupported MPS FP16 was rejected clearly.

## Commands

From `jsm/`:

```bash
python3 train.py
python3 train.py --resume --epochs 60
python3 inference.py
python3 train.py --precision fp32
```

## Current Artifacts And Caveats

- Tokenizer: `jsm/artifacts/tokenizer/tokenizer.json`.
- Resume checkpoint: `jsm/artifacts/tiny_model.pt`.
- The latest checkpoint was overwritten by a three-epoch tokenizer-integration smoke test, so it is structurally valid but undertrained. Run a fresh normal training command before judging generation quality.
- The corpus still contains only `i love coffee` and `i drink coffee`; high confidence demonstrates memorization, not intelligence or generalization.
- CUDA FP16 autocast exists, but gradient scaling is not implemented yet. FP32 remains recommended.
- Learned absolute positions remain in use; RoPE is documented but not implemented.
- DataLoader shuffle RNG state is not checkpointed, so resume is practical but not bit-for-bit reproducible.
- `artifacts/vocabulary.json` is a stale educational artifact and is no longer used by production training/inference.

## Roadmap Status

Phases 1-40 are complete. `LLM_UPGRADE_PROGRESS.md` contains per-phase evidence, and `LLM_UPGRADE_REPORT.md` is the authoritative final architecture/report. Future work should begin as a new roadmap rather than repeating completed phases.
