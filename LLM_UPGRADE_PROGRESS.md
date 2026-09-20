# LLM Upgrade Progress

## Current State

- Production code lives in `jsm/`; educational experiments remain in `jsm/lessons/`.
- The production model is a batched pre-norm GPT-style decoder with manual multi-head causal attention, GELU FFNs, residuals, final normalization, and tied per-token LM head.
- Inputs are `[B,T]`, hidden states `[B,T,C]`, attention scores `[B,H,T,T]`, and logits `[B,T,V]`.
- Training uses document-aware shifted windows, AdamW, warmup/cosine decay, gradient clipping, resumable checkpoints, and CPU/MPS/CUDA placement.
- Production tokenization is pure-Python Byte-Level BPE trained on local files; whitespace tokenization remains only as educational history.

## What Is Already Correct

- Causal masking prevents attention to future positions.
- Transformer blocks preserve sequence shape.
- Residual paths, normalization, and FFN parameters are trainable.
- Multiple blocks are registered correctly through `nn.ModuleList`.
- Checkpoint code currently saves embeddings, blocks, and the output layer.

## What Is Educational / Simplified

- Full-sequence flattening produces only one prediction.
- Training does not use shifted targets at every position.
- Sequence length is fixed at two and there is no batch dimension.
- Attention is single-head and assumes rank-2 tensors.
- Tokenization, data windows, optimizer, checkpoints, generation, and evaluation are minimal.

## What Must Change

- Preserve sequence dimensions through the LM head and train shifted next-token targets.
- Add configurable context length, multi-head batched attention, datasets/loaders, and a local subword tokenizer.
- Add generation and sampling, configuration, modern block details, robust training/checkpoints/devices, validation, evaluation, tests, and documentation.
- Document realistic scaling without attempting large local training.

## Order Of Implementation

- [x] Phase 1: Real GPT output head
- [x] Phase 2: Shifted next-token training
- [x] Phase 3: Remove fixed two-token assumptions
- [x] Phase 4: Real context window
- [x] Phase 5: Multi-head self-attention
- [x] Phase 6: Add batch dimension
- [x] Phase 7: Real training data windows
- [x] Phase 8: Dataset and DataLoader
- [x] Phase 9: Real tokenizer
- [x] Phase 10: Text generation loop
- [x] Phase 11: Sampling
- [x] Phase 12: Better model configuration
- [x] Phase 13: Parameter counting
- [x] Phase 14: Weight tying
- [x] Phase 15: Positional encoding discussion
- [x] Phase 16: Pre-norm vs post-norm
- [x] Phase 17: Activation functions
- [x] Phase 18: Dropout
- [x] Phase 19: Optimizer
- [x] Phase 20: Learning-rate scheduler
- [x] Phase 21: Gradient clipping
- [x] Phase 22: Checkpoint design
- [x] Phase 23: Device support
- [x] Phase 24: Mixed precision
- [x] Phase 25: GPU training basics
- [x] Phase 26: Distributed training basics
- [x] Phase 27: Scaling toward a real 1B model
- [x] Phase 28: GQA / MQA
- [x] Phase 29: KV cache
- [x] Phase 30: Training / validation split
- [x] Phase 31: Perplexity
- [x] Phase 32: Basic evaluation
- [x] Phase 33: Overfitting demonstration
- [x] Phase 34: Real mini corpus
- [x] Phase 35: Clean project architecture
- [x] Phase 36: Tests
- [x] Phase 37: Shape logging / debug mode
- [x] Phase 38: Parameter scale experiments
- [x] Phase 39: What makes an LLM intelligent
- [x] Phase 40: Realistic 1B training plan

## Completed Phases

PHASE 1 — REAL GPT OUTPUT HEAD
Status: DONE ✅

Completed:
- Removed full-sequence flattening from the production model.
- Added a per-token LM head that maps hidden states `[T, C]` to logits `[T, V]`.
- Updated checkpoint save/load keys from `output_layer` to `lm_head`.
- Verified gradients reach the LM head.

Files changed:
- `jsm/model.py`
- `jsm/train.py`
- `jsm/inference.py`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- `python3 -m py_compile model.py train.py inference.py`
- Shape test: tokens `[4]` produce logits `[4, 100]`.
- Backward test: `lm_head.weight.grad` is populated.

Next phase:
PHASE 2 — SHIFTED NEXT-TOKEN TRAINING

---

PHASE 2 — SHIFTED NEXT-TOKEN TRAINING
Status: DONE ✅

Completed:
- Replaced one-target context pairs with document-local shifted input/target sequences.
- Trained every token position simultaneously with logits `[T, V]` and targets `[T]`.
- Updated training and inference predictions to use final-position logits for one-step prediction.
- Regenerated the checkpoint with the per-token LM head format.

Files changed:
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `jsm/artifacts/vocabulary.json`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- `python3 train.py`: loss decreased from `3.1308` to `0.8336`.
- `python3 inference.py`: checkpoint loaded and predicted successfully.
- Shape test: input `[3]`, targets `[3]`, logits `[3, 7]`.
- Backward test: shifted cross-entropy populated model gradients.

Next phase:
PHASE 3 — REMOVE FIXED TWO-TOKEN ASSUMPTIONS

---

PHASE 3 — REMOVE FIXED TWO-TOKEN ASSUMPTIONS
Status: DONE ✅

Completed:
- Replaced `context_size` with configurable `max_seq_len` in production code.
- Sized positional embeddings by the maximum supported sequence length.
- Derived positions from each actual input length on the input device.
- Added a clear error when input exceeds the context window.

Files changed:
- `jsm/model.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Variable sequence lengths `1`, `4`, and `8` produced `[T, 11]` logits.
- Length `9` correctly failed for `max_seq_len=8`.
- `python3 train.py` completed and saved the resized positional embedding.
- `python3 inference.py` loaded the new checkpoint successfully.

Next phase:
PHASE 4 — REAL CONTEXT WINDOW

---

PHASE 4 — REAL CONTEXT WINDOW
Status: DONE ✅

Completed:
- Documented context length, positional capacity, training windows, and inference truncation.
- Explained vanilla attention's `[T, T]` matrix and approximate `O(T^2)` scaling.
- Recorded practical local limits versus architectural examples such as 4K and 128K.
- Kept the executable learning configuration at `max_seq_len=16`.

Files changed:
- `docs/context_window.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- A full 16-token input produced logits `[16, 32]`.
- Positional table shape verified as `[16, 8]`.
- Attention score count verified as `16^2 = 256` per head.

Next phase:
PHASE 5 — MULTI-HEAD SELF-ATTENTION

---

PHASE 5 — MULTI-HEAD SELF-ATTENTION
Status: DONE ✅

Completed:
- Implemented manual Q/K/V projection, head splitting, per-head scaled attention, head merging, and output projection.
- Applied one causal `[T, T]` mask correctly across batches and heads.
- Added `embedding_dim % num_heads == 0` validation.
- Threaded configurable `num_heads` through `TinyModel` and `TransformerBlock`.
- Preserved rank-2 single-sequence support while preparing attention for batched input.

Files changed:
- `jsm/attention.py`
- `jsm/transformer_block.py`
- `jsm/model.py`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Four-head test: Q/K/V `[2,4,5,2]`, scores `[2,4,5,5]`, output `[2,5,8]`.
- Causal isolation test: changing the final token did not change earlier outputs.
- Backward test: output-projection gradients populated.
- Invalid `embedding_dim=7, num_heads=4` correctly raised `ValueError`.
- Training and checkpoint inference completed after the architecture change.

Next phase:
PHASE 6 — ADD BATCH DIMENSION

---

PHASE 6 — ADD BATCH DIMENSION
Status: DONE ✅

Completed:
- Added explicit model support and validation for token IDs `[T]` and `[B,T]`.
- Updated training to process document sequences together as one batch.
- Computed cross-entropy across every token in every sequence.
- Updated inference to use batched input and final-position logits `[0,-1,:]`.

Files changed:
- `jsm/model.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Tokens `[3,5]` produced hidden states `[3,5,8]` and logits `[3,5,13]`.
- Four-head attention score shape verified conceptually as `[3,4,5,5]`.
- Batched shifted cross-entropy and backward pass succeeded.
- Batched `python3 train.py` and `python3 inference.py` completed.

Next phase:
PHASE 7 — REAL TRAINING DATA WINDOWS

---

PHASE 7 — REAL TRAINING DATA WINDOWS
Status: DONE ✅

Completed:
- Added configurable shifted-window creation from encoded token documents.
- Supported overlapping (`stride=1`) and chunked (`stride=sequence_length`) windows.
- Preserved document boundaries so unrelated files never form false transitions.
- Updated training to consume token-ID windows instead of manually assembled word pairs.

Files changed:
- `jsm/data_loader.py`
- `jsm/train.py`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Exact overlapping and chunked windows matched expected shifted IDs.
- Sentinel test confirmed windows never mixed separate documents.
- `python3 train.py` and `python3 inference.py` completed successfully.

Next phase:
PHASE 8 — DATASET + DATALOADER

---

PHASE 8 — DATASET + DATALOADER
Status: DONE ✅

Completed:
- Added `LanguageModelDataset` over document-aware shifted windows.
- Added PyTorch `DataLoader` batching and shuffling to training.
- Kept token and target tensors as `torch.long` with shape `[B,T]`.
- Added a clear error when the corpus cannot produce any windows.

Files changed:
- `jsm/dataset.py`
- `jsm/train.py`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Three samples batched as `[2,3]` and final `[1,3]` batches.
- Dataset input and target shapes matched for every batch.
- `python3 train.py` and `python3 inference.py` completed successfully.

Next phase:
PHASE 9 — REAL TOKENIZER

---

PHASE 9 — REAL TOKENIZER
Status: DONE ✅

Completed:
- Added a Byte-Level BPE tokenizer trained only on local corpus files.
- Added BOS/EOS document boundaries and reserved PAD/UNK special tokens.
- Saved the independent tokenizer artifact under `artifacts/tokenizer/`.
- Updated production training and inference to use subword IDs.
- Preserved the whitespace tokenizer and lesson code for educational history.
- Documented characters, words, subwords, BPE, special tokens, and tokenizer/embedding separation.
- Replaced the initial library-backed implementation with a pure-Python Byte-Level BPE implementation: byte vocabulary, pair counting, deterministic merge learning, encoding, decoding, and JSON persistence.

Files changed:
- `jsm/subword_tokenizer.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/requirements.txt`
- `jsm/artifacts/tokenizer/tokenizer.json`
- `jsm/artifacts/tiny_model.pt`
- `docs/tokenizer.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- BPE encode/decode round-trip reproduced `i love coffee` exactly.
- Vocabulary size loaded as `275`; both documents encoded with boundaries.
- `python3 train.py` completed with subword IDs.
- `python3 inference.py` loaded tokenizer/checkpoint and predicted subword tokens.
- From-scratch tokenizer learned 18 merges with a 278-token vocabulary.
- ASCII, unseen text, and Arabic UTF-8 round-trips passed without third-party tokenizer code.

Next phase:
PHASE 10 — TEXT GENERATION LOOP

---

PHASE 10 — TEXT GENERATION LOOP
Status: DONE ✅

Completed:
- Added autoregressive generation from a text prompt.
- Selected next-token logits from the final sequence position and appended one token per step.
- Added EOS stopping, `max_new_tokens`, and context-window truncation.
- Updated inference to print a generated continuation.

Files changed:
- `jsm/generation.py`
- `jsm/inference.py`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Greedy generation returned decoded text.
- A prompt longer than the model window generated without shape errors.
- `max_new_tokens=0` returned the original prompt unchanged.
- `python3 inference.py` generated ten tokens and retained one-step diagnostics.

Next phase:
PHASE 11 — SAMPLING

---

PHASE 11 — SAMPLING
Status: DONE ✅

Completed:
- Added greedy decoding through the safe `temperature=0` path.
- Added temperature scaling, top-k filtering, and top-p nucleus filtering.
- Retained the first token that crosses the top-p threshold.
- Added validation for invalid temperature, top-k, and top-p settings.
- Exposed sampling controls through `generate()` and inference.

Files changed:
- `jsm/generation.py`
- `jsm/inference.py`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Greedy decoding selected the maximum logit.
- Twenty seeded top-k=1 samples stayed in the allowed set.
- Twenty seeded top-p=0.5 samples stayed in the minimal nucleus.
- Invalid sampling configurations raised `ValueError`.
- `python3 inference.py` generated text with temperature/top-k/top-p.

Next phase:
PHASE 12 — BETTER MODEL CONFIGURATION

---

PHASE 12 — BETTER MODEL CONFIGURATION
Status: DONE ✅

Completed:
- Added a validated `ModelConfig` dataclass for vocabulary, context, width, heads, layers, and FFN multiplier.
- Refactored `TinyModel` to consume one configuration object.
- Threaded configurable FFN width through blocks.
- Unified training and inference on a small local `C=32`, four-head, two-layer configuration.

Files changed:
- `jsm/config.py`
- `jsm/model.py`
- `jsm/transformer_block.py`
- `jsm/feed_forward.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Three-layer config produced logits `[2,8,100]`.
- FFN expansion verified as `32 -> 128`.
- Invalid `embedding_dim=30, num_heads=4` was rejected.
- Training and inference completed with the shared configuration.

Next phase:
PHASE 13 — PARAMETER COUNTING

---

PHASE 13 — PARAMETER COUNTING
Status: DONE ✅

Completed:
- Added reusable total and trainable parameter counting.
- Added top-level component parameter breakdown.
- Printed parameter counts during training startup.
- Documented scaling with vocabulary, width, layers, FFN size, and attention heads.

Files changed:
- `jsm/utils.py`
- `jsm/train.py`
- `docs/parameters.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Programmatic and hand-derived counts both equaled `31,908` for the test config.
- Component breakdown summed exactly to the total.
- Current training config reported `43,539` total/trainable parameters.

Next phase:
PHASE 14 — WEIGHT TYING

---

PHASE 14 — WEIGHT TYING
Status: DONE ✅

Completed:
- Added configurable input/output embedding weight tying, enabled by default.
- Shared one `[V,C]` parameter object between token embeddings and the LM head.
- Fixed component breakdowns to count shared parameters only once.
- Documented the parameter and representation-sharing tradeoff.

Files changed:
- `jsm/config.py`
- `jsm/model.py`
- `jsm/utils.py`
- `docs/parameters.md`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Identity test confirmed `lm_head.weight is embedding.weight`.
- Tied model used exactly `V*C = 3,200` fewer parameters in the test.
- Unique component breakdown summed to the tied model total.
- Training and checkpoint inference completed with tied weights.

Next phase:
PHASE 15 — POSITIONAL ENCODING DISCUSSION

---

PHASE 15 — POSITIONAL ENCODING DISCUSSION
Status: DONE ✅

Completed:
- Documented learned absolute, sinusoidal, and rotary positional methods.
- Explained that RoPE rotates Q/K inside attention rather than adding position vectors.
- Defined a safe future migration path and long-context limitations.
- Retained learned absolute embeddings as the appropriate current implementation.

Files changed:
- `docs/positional_encoding.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Position table shape verified as `[8,16]`.
- Used positions received gradients; unused positions remained zero.

Next phase:
PHASE 16 — PRE-NORM VS POST-NORM

---

PHASE 16 — PRE-NORM VS POST-NORM
Status: DONE ✅

Completed:
- Refactored production blocks to `x + Attention(LN(x))` and `x + FFN(LN(x))`.
- Added final LayerNorm after the block stack and before the LM head.
- Updated checkpoint save/load for final normalization.
- Preserved educational lesson implementations and documented both norm orders.

Files changed:
- `jsm/transformer_block.py`
- `jsm/model.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/pre_norm.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Block preserved `[2,4,8]` shape.
- Zeroed attention/FFN branches produced an exact residual identity.
- Identity path propagated unit gradients unchanged.
- Training and checkpoint inference completed with final LayerNorm.

Next phase:
PHASE 17 — ACTIVATION FUNCTIONS

---

PHASE 17 — ACTIVATION FUNCTIONS
Status: DONE ✅

Completed:
- Replaced production FFN ReLU with GELU.
- Documented ReLU, GELU, SiLU/Swish, and SwiGLU tradeoffs.
- Preserved the simple two-projection FFN structure for inspectability.

Files changed:
- `jsm/feed_forward.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/activations.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- FFN preserved `[2,5,8]` and propagated gradients.
- Activation instance verified as `nn.GELU`.
- Negative GELU output verified as smooth/nonzero.
- Training and inference completed after the activation change.

Next phase:
PHASE 18 — DROPOUT

---

PHASE 18 — DROPOUT
Status: DONE ✅

Completed:
- Added configurable embedding, attention-weight, FFN, and residual dropout.
- Added dropout range validation and retained `0.0` for the tiny corpus.
- Made training mode explicit; generation/inference already use evaluation mode.
- Documented train/eval behavior and when regularization is useful.

Files changed:
- `jsm/config.py`
- `jsm/attention.py`
- `jsm/feed_forward.py`
- `jsm/transformer_block.py`
- `jsm/model.py`
- `jsm/train.py`
- `docs/dropout.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Nonzero dropout produced stochastic train-mode outputs.
- Eval-mode outputs were exactly deterministic.
- Rates outside `[0,1)` were rejected.
- Training and inference completed with local dropout disabled.

Next phase:
PHASE 19 — OPTIMIZER

---

PHASE 19 — OPTIMIZER
Status: DONE ✅

Completed:
- Replaced SGD with AdamW.
- Set local learning rate `3e-3`, betas `(0.9,0.95)`, and weight decay `0.01`.
- Documented adaptive moments, decoupled weight decay, and tuning scope.

Files changed:
- `jsm/train.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/optimizer.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- `python3 train.py` completed with AdamW.
- Training loss fell from `18.2264` to the sub-`0.4` range.
- Final model predicted the expected `coffee` continuation above `99.9%` for both toy prompts.

Next phase:
PHASE 20 — LEARNING RATE SCHEDULER

---

PHASE 20 — LEARNING RATE SCHEDULER
Status: DONE ✅

Completed:
- Added linear warmup followed by cosine learning-rate decay.
- Added a configurable 10% minimum LR multiplier.
- Stepped the scheduler per optimizer update and logged LR periodically.
- Documented constant rates, warmup, decay, and step semantics.

Files changed:
- `jsm/training_utils.py`
- `jsm/train.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/learning_rate.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Five-step warmup matched `[0.2,0.4,0.6,0.8,1.0]` multipliers.
- Cosine section was monotonic and ended at `0.1`.
- Training completed from LR warmup through final `3e-4` LR.

Next phase:
PHASE 21 — GRADIENT CLIPPING

---

PHASE 21 — GRADIENT CLIPPING
Status: DONE ✅

Completed:
- Added global gradient-norm clipping at `1.0`.
- Positioned clipping after backward and before the optimizer update.
- Documented exploding gradients and uniform norm scaling.

Files changed:
- `jsm/train.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/gradient_clipping.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Artificial gradient norm `~84,024` clipped to `1.0`.
- Training completed successfully with clipping enabled.

Next phase:
PHASE 22 — CHECKPOINT DESIGN

---

PHASE 22 — CHECKPOINT DESIGN
Status: DONE ✅

Completed:
- Replaced component saves with complete model state and serialized config.
- Added optimizer, scheduler, epoch, and global-step state.
- Added `--resume --epochs <new-total>` training continuation.
- Rebuilt inference models directly from checkpoint configuration.
- Documented weights-only versus training-resume checkpoints.

Files changed:
- `jsm/checkpoint.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/checkpoints.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Fresh checkpoint contained all six required keys at epoch 49/step 150.
- Resume continued to epoch 51/step 156 with populated AdamW state.
- Inference loaded the full model from checkpoint config/state.

Next phase:
PHASE 23 — DEVICE SUPPORT

---

PHASE 23 — DEVICE SUPPORT
Status: DONE ✅

Completed:
- Added CUDA, then MPS, then CPU device selection.
- Moved models, training batches, evaluation inputs, and inference inputs consistently.
- Added checkpoint `map_location` support across hardware types.
- Printed the selected device in training and inference.

Files changed:
- `jsm/device.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/artifacts/tiny_model.pt`
- `docs/device_support.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Local runtime selected MPS.
- Model parameters, inputs, and outputs all reported `mps:0`.
- Two-epoch MPS training completed.
- MPS checkpoint inference and generation completed.

Next phase:
PHASE 24 — MIXED PRECISION

---

PHASE 24 — MIXED PRECISION
Status: DONE ✅

Completed:
- Added explicit FP32/FP16/BF16 training precision selection.
- Kept FP32 as the safe default on CPU and MPS.
- Added CUDA autocast paths and CUDA BF16 capability validation.
- Rejected unsupported device/precision combinations clearly.
- Documented numeric formats, benefits, risks, and the remaining FP16 gradient-scaling limitation.

Files changed:
- `jsm/precision.py`
- `jsm/train.py`
- `docs/mixed_precision.md`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- FP32 context preserved `torch.float32`.
- Unsupported MPS FP16 request raised `ValueError`.
- One-epoch MPS FP32 training completed.

Next phase:
PHASE 25 — GPU TRAINING BASICS
Status: DONE ✅

Completed:
- Documented CPU RAM to GPU VRAM data flow through forward, backward, and optimizer update.
- Explained parameters, gradients, optimizer states, activations, attention matrices, and temporary memory.
- Added a transparent lower-bound training-memory estimator.
- Removed unused NumPy so PyTorch is the only project runtime dependency.
- Reconciled the stale progress summary and roadmap checklist.

Files changed:
- `jsm/memory.py`
- `jsm/requirements.txt`
- `docs/gpu_training.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- One-billion-parameter FP32 example computed 4 GB parameters, 4 GB gradients, and 8 GB AdamW moments.
- Attention and hidden lower-bound formulas matched exact expected values.
- Component sum matched the reported total lower bound.

Limitations:
- Memory estimates intentionally exclude allocator, kernel workspace, and several autograd/precision costs.

Next phase:
PHASE 26 — DISTRIBUTED TRAINING BASICS

---

PHASE 26 — DISTRIBUTED TRAINING BASICS
Status: DONE ✅

Completed:
- Documented single-GPU, DDP, FSDP/ZeRO, tensor-parallel, pipeline-parallel, and multi-node roles.
- Explained which methods improve throughput versus which reduce per-device memory.
- Added practical scale guidance from one GPU through 30B+ models.
- Kept distributed dependencies and process groups out of the local learning project.

Files changed:
- `docs/distributed_training.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Documentation audit confirms every requested distributed strategy and hardware tier is covered.

Limitations:
- No distributed runtime was added or benchmarked locally.

Next phase:
PHASE 27 — SCALING TOWARD A REAL 1B MODEL

---

PHASE 27 — SCALING TOWARD A REAL 1B MODEL
Status: DONE ✅

Completed:
- Added a tensor-free dense-decoder parameter estimator.
- Defined a conceptual 32K-vocab, 2048-wide, 18-layer, 16-head architecture.
- Verified the configuration at 980,262,144 parameters with learned positions.
- Documented modern architecture differences and why local training is prohibited.

Files changed:
- `jsm/scaling.py`
- `docs/1b_architecture.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Exact component formula summed to `980,262,144`.
- Estimate fell inside the asserted 950M-1.05B target range.
- Learned-position contribution verified as `8,388,608` parameters.

Limitations:
- This is an architecture estimate only; no 1B tensors were allocated.

Next phase:
PHASE 28 — GQA / MQA

---

PHASE 28 — GQA / MQA
Status: DONE ✅

Completed:
- Added configurable KV-head count to manual causal attention.
- Implemented MHA (`K=H`), GQA (`1<K<H`), and MQA (`K=1`) through KV-head repetition.
- Added configuration validation and documented cache/parameter tradeoffs.

Files changed:
- `jsm/config.py`
- `jsm/attention.py`
- `jsm/transformer_block.py`
- `jsm/model.py`
- `docs/gqa.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- MHA/GQA/MQA each preserved `[2,5,16]` output shape.
- Attention parameters decreased `1024 -> 768 -> 640` as KV heads decreased.
- GQA causal isolation passed.
- Invalid `H=4, K=3` configuration was rejected.

Limitations:
- Default remains MHA; architecture comparisons need a larger corpus.

Next phase:
PHASE 29 — KV CACHE

---

PHASE 29 — KV CACHE
Status: DONE ✅

Completed:
- Added per-layer K/V cache creation, append, and reuse.
- Preserved compact KV-head shape for MHA/GQA/MQA caches.
- Added cache-aware positions and causal masks.
- Enabled cached generation by default with context-window rebuild on overflow.
- Kept training on the unchanged full-sequence path.

Files changed:
- `jsm/attention.py`
- `jsm/transformer_block.py`
- `jsm/model.py`
- `jsm/generation.py`
- `docs/kv_cache.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Full-prefix and token-by-token cached logits differed by at most `2.87e-6`.
- GQA cache shape verified as `[1,2,5,4]`.
- Cached and uncached greedy generation produced identical text.
- Existing checkpoint inference completed with cache enabled.

Limitations:
- A full context rebuild is used when the learned-position window rolls over.

Next phase:
PHASE 30 — TRAINING / VALIDATION SPLIT

---

PHASE 30 — TRAINING / VALIDATION SPLIT
Status: DONE ✅

Completed:
- Added deterministic seeded document-level train/validation splitting.
- Created independent datasets/loaders after splitting to prevent window leakage.
- Added no-gradient validation loss reporting during training.
- Documented overfitting signals and split semantics.

Files changed:
- `jsm/data_loader.py`
- `jsm/train.py`
- `docs/validation.md`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Ten-document test split deterministically into 8 train / 2 validation documents.
- Sets were disjoint and their union preserved every document.
- Three-epoch MPS training reported both train and validation loss.

Limitations:
- The current two-document corpus yields only one BPE window per split.

Next phase:
PHASE 31 — PERPLEXITY

---

PHASE 31 — PERPLEXITY
Status: DONE ✅

Completed:
- Added perplexity as `exp(mean cross-entropy)` with overflow handling.
- Added validation perplexity to training reports.
- Documented tokenizer/data comparability and tiny-validation limitations.

Files changed:
- `jsm/metrics.py`
- `jsm/train.py`
- `docs/validation.md`
- `jsm/artifacts/tiny_model.pt`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Loss `0` produced perplexity `1`.
- Loss `ln(2)` produced perplexity `2`.
- Extreme loss returned infinity instead of crashing.
- Training printed validation loss and perplexity.

Limitations:
- Current validation perplexity is not meaningful with one held-out window.

Next phase:
PHASE 32 — BASIC EVALUATION

---

PHASE 32 — BASIC EVALUATION
Status: DONE ✅

Completed:
- Added standalone no-gradient held-out evaluation.
- Reported token-weighted loss, perplexity, argmax next-token accuracy, and token count.
- Added deterministic generation samples and an explicit memorization warning.
- Documented metric strengths and limitations.

Files changed:
- `jsm/evaluate.py`
- `docs/evaluation.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- `python3 evaluate.py` loaded tokenizer/checkpoint on MPS.
- Evaluator returned all four metrics over two held-out target tokens.
- Two deterministic generation samples completed.

Limitations:
- Current checkpoint is undertrained and validation contains only two target tokens.

Next phase:
PHASE 33 — OVERFITTING DEMONSTRATION

---

PHASE 33 — OVERFITTING DEMONSTRATION
Status: DONE ✅

Completed:
- Added a controlled lesson with disjoint train and validation token patterns.
- Demonstrated memorization as near-zero training loss without held-out improvement.
- Documented why high confidence on the original two sentences is not intelligence.

Files changed:
- `jsm/lessons/overfitting_demo.py`
- `docs/overfitting.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Training loss fell from `12.3242` to `0.00075`.
- Validation loss worsened from `9.5141` to `13.1592`.
- Assertions confirmed the final train/validation gap.

Limitations:
- Demonstration is intentionally synthetic and isolates one concept.

Next phase:
PHASE 34 — REAL MINI CORPUS

---

PHASE 34 — REAL MINI CORPUS
Status: DONE ✅

Completed:
- Added six original local documents across varied educational topics.
- Added an explicit pure-Python tokenizer training command.
- Regenerated a 300-token vocabulary with 40 learned BPE merges.
- Increased production training/evaluation windows to 16 tokens.
- Preserved all eight document boundaries.

Files changed:
- `jsm/data/raw/mini_*.txt`
- `jsm/train_tokenizer.py`
- `jsm/train.py`
- `jsm/evaluate.py`
- `jsm/artifacts/tokenizer/tokenizer.json`
- `jsm/artifacts/tiny_model.pt`
- `docs/mini_corpus.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Corpus loaded 8 separate documents.
- Dataset produced 647 training and 140 validation windows.
- Five-epoch MPS run reduced train loss from `5.39` to `1.53`.
- Evaluation processed 2,240 held-out tokens with 12.5% next-token accuracy.
- Generation completed for both controlled prompts.

Limitations:
- Validation loss rose to `5.43`, demonstrating overfitting; corpus remains intentionally tiny.

Next phase:
PHASE 35 — CLEAN PROJECT ARCHITECTURE

---

PHASE 35 — CLEAN PROJECT ARCHITECTURE
Status: DONE ✅

Completed:
- Centralized corpus, artifact, tokenizer, and checkpoint paths.
- Made production entry points work from repository root or `jsm/`.
- Documented module ownership and retained a beginner-readable flat production layout.
- Removed the stale production whitespace-vocabulary artifact.
- Added repository command/layout documentation.

Files changed:
- `jsm/paths.py`
- `jsm/data_loader.py`
- `jsm/subword_tokenizer.py`
- `jsm/train.py`
- `jsm/inference.py`
- `jsm/evaluate.py`
- `jsm/artifacts/vocabulary.json` (removed)
- `README.md`
- `docs/project_architecture.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Production modules compiled after path refactor.
- Inference and evaluation ran from repository root.
- Inference also ran from inside `jsm/`.

Limitations:
- Production modules remain flat intentionally; no packaging abstraction was added without need.

Next phase:
PHASE 36 — TESTS

---

PHASE 36 — TESTS
Status: DONE ✅

Completed:
- Added dependency-free `unittest` coverage for tokenizer, attention, blocks, model, KV cache, generation, and checkpoints.
- Kept tests isolated with temporary tokenizer/checkpoint files.

Files changed:
- `tests/test_pipeline.py`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Five test cases passed in under one second.
- Verified UTF-8 tokenizer round-trip/persistence.
- Verified GQA causal isolation and `[B,T,V]` model shapes.
- Verified cached/full logits and checkpoint metadata round-trip.

Limitations:
- Tests are lightweight correctness checks, not performance or large-data tests.

Next phase:
PHASE 37 — SHAPE LOGGING / DEBUG MODE

---

PHASE 37 — SHAPE LOGGING / DEBUG MODE
Status: DONE ✅

Completed:
- Added opt-in shape inspection without changing normal training output.
- Added a runnable checkpoint/tokenizer debug script.
- Reported tokens, embeddings, Q, compact K/V, scores, attention output, hidden state, and logits.

Files changed:
- `jsm/shape_debug.py`
- `jsm/debug_shapes.py`
- `README.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Current checkpoint reported tokens `[1,16]`, scores `[1,4,16,16]`, and logits `[1,16,300]`.
- GQA test reported Q `[3,4,5,4]`, KV `[3,2,5,4]`, and logits `[3,5,50]`.

Limitations:
- Utility reports architecture-derived intermediate shapes rather than retaining large intermediate tensors.

Next phase:
PHASE 38 — PARAMETER SCALE EXPERIMENTS

---

PHASE 38 — PARAMETER SCALE EXPERIMENTS
Status: DONE ✅

Completed:
- Added Tiny, Mini, conceptual ~100M, and conceptual ~1B configurations.
- Added a formula-only scale report with explicit local/conceptual labels.
- Documented width, depth, vocabulary, context, and head-count scaling effects.

Files changed:
- `jsm/scale_configs.py`
- `jsm/scale_report.py`
- `docs/scale_experiments.md`
- `README.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Estimates were `35,628`, `6,854,464`, `96,243,968`, and `980,262,144`.
- Every configuration fell inside its asserted scale range.
- Parameter estimates increased monotonically without allocating model tensors.

Limitations:
- Formula reflects the current dense GELU/learned-position architecture, not every modern variant.

Next phase:
PHASE 39 — WHAT MAKES AN LLM INTELLIGENT

---

PHASE 39 — WHAT MAKES AN LLM INTELLIGENT
Status: DONE ✅

Completed:
- Documented architecture, data quality/diversity, tokenization, capacity, compute, optimization, context, post-training, and evaluation interactions.
- Explained why depth increases potential capacity but cannot guarantee generalization or intelligence.
- Connected the original coffee prediction to memorization rather than understanding.

Files changed:
- `docs/what_makes_an_llm_capable.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Documentation audit covers all nine required capability factors and the layer-count misconception.

Limitations:
- This phase is conceptual; capability claims require empirical evaluation on suitable data.

Next phase:
PHASE 40 — REALISTIC 1B TRAINING PLAN

---

PHASE 40 — REALISTIC 1B TRAINING PLAN
Status: DONE ✅

Completed:
- Created a realistic, assumption-labeled dense 1B training plan.
- Covered architecture, exact parameter estimate, tokenizer, token target, storage, preprocessing, packing, compute, GPU/VRAM, batch/accumulation, precision, optimizer, distributed strategy, checkpoints, throughput, validation, evaluation, and inference.
- Clearly separated executable educational work from production recommendations.
- Did not instantiate or train a 1B model locally.

Files changed:
- `docs/1b_training_plan.md`
- `LLM_UPGRADE_PROGRESS.md`

Tests passed:
- Full Python tree compiled successfully.
- All five automated pipeline tests passed.
- Shape debug and all four scale reports completed.
- Final 1B-plan topic audit passed.

Limitations:
- Throughput/duration figures are formula-based scenarios and require hardware benchmarks.

Next phase:
ROADMAP COMPLETE — CREATE AND MAINTAIN FINAL REPORT
