# Build JSM yourself: a beginner's course

This course is a **typing and reasoning guide**, not a second implementation. You create each Python file in `jsm_0.1` yourself. The working reference is the neighboring `jsm` folder. Start with plain UTF-8 text, then follow one piece of data all the way to a generated token.

## How to use this course

1. Work in `jsm_0.1`. Keep `jsm` open in another editor pane as a reference.
2. Create files in the order below. Type the code yourself, one small block at a time. Read the explanation **before** copying a line.
3. Run the checkpoint command after each stage. If it fails, inspect shapes and values before moving on.
4. For every `import`, ask: “Which file supplies this name?” For every tensor, write its shape on paper.
5. Do not copy `jsm/artifacts`: its model and tokenizer belong to a particular training run. Make your own artifacts after training.

All PowerShell commands below start from the repository root unless a `cd jsm_0.1` line appears. Your existing `jsm_0.1/steps.md`, `reminders.md`, `requirements.txt`, and `.venv` are left as they are. Use `jsm_0.1/.venv/Scripts/python.exe` if that environment already works, or activate it and use `python`. The only runtime dependency listed by the original project is `torch`. In this repository, the `.venv` has PyTorch; a warning about missing NumPy can appear, but it does not stop these lessons.

**Map of the journey**

```text
data/raw/*.txt
  -> data_loader.py: separate documents
  -> subword_tokenizer.py: UTF-8 bytes -> token IDs
  -> data_loader.py + dataset.py: input/target windows
  -> model.py: embeddings -> transformer blocks -> logits
  -> train.py: loss -> gradients -> updated weights
  -> checkpoint.py: saved model
  -> inference.py + generation.py: prompt -> continuation
```

`jsm/tokenizer.py` and some `jsm/lessons` scripts form an **older word-level teaching path**. The production path used by `train.py` and `inference.py` is `subword_tokenizer.py`. Both are worth learning; do not mix their vocabularies or checkpoints.

## 0. Make a safe workspace and read actual text

Create this layout as you work. The `data/raw` folder in this course contains copies of the eight original plain-text documents from `jsm/data/raw`, plus four Arabic documents (`arabic_*.txt`). They are ordinary UTF-8 text, not token ID lists or generated tensor examples. You can replace them later with your own writing. Use at least two reasonably long `.txt` documents so both training and validation can produce 16-token windows. The short `plain1.txt` and `plain2.txt` are useful for the word-level lessons, but too short by themselves for the full training loop.

```text
jsm_0.1/
  COURSE.md
  requirements.txt
  data/raw/*.txt
  artifacts/tokenizer/       # created by tokenizer training
  artifacts/tiny_model.pt    # created by model training
  paths.py                   # you create the Python files below
  ...
```

Open `data/raw/plain1.txt`: it says `i love coffee`. Open `plain2.txt`: it says `i drink coffee`. Open `arabic_learning.txt` to see ordinary Arabic prose. No token IDs exist in these files. Numbers first appear when *your tokenizer* assigns IDs. Every `.txt` file is treated as one document. Newlines inside a file stay inside that document. The loader strips leading and trailing whitespace, so a final newline will not become training text. Byte-level BPE can encode both English and Arabic from UTF-8 bytes. Adding Arabic changes the learned merges, so train a new tokenizer and model for this corpus.

**Checkpoint:** In PowerShell, run `Get-Content .\jsm_0.1\data\raw\plain1.txt`. Explain why the file is a document, not yet a training example.

## 1. Create `paths.py`: where files live

Reference: [`jsm/paths.py`](../jsm/paths.py). Create `jsm_0.1/paths.py` first, because the loader and tokenizer import it.

Read its statements in this order:

| Code idea | What it does |
| --- | --- |
| `from pathlib import Path` | Imports a path object that works with filesystem paths. |
| `Path(__file__).resolve().parent` | Finds the directory of **this** `paths.py`; commands work from any current directory. |
| `DATA_DIR = PROJECT_DIR / "data"` | `/` joins path pieces here; it is not numeric division. |
| `RAW_DATA_DIR = DATA_DIR / "raw"` | Sets the folder scanned for text. |
| `ARTIFACTS_DIR`, `TOKENIZER_DIR` | Set output folders for things learned during training. |
| `TOKENIZER_PATH`, `CHECKPOINT_PATH` | Set exact output filenames for tokenizer JSON and model weights. |

Write these seven assignments yourself. Print `RAW_DATA_DIR` once to check that it points into **`jsm_0.1`**, not `jsm`.

## 2. Create `data_loader.py`: load text and make next-token examples

Reference: [`jsm/data_loader.py`](../jsm/data_loader.py). This is the first file that actually touches the corpus.

### Read documents

`from paths import RAW_DATA_DIR` obtains the folder. `documents = []` starts an empty list. `for file_path in raw_folder.glob("*.txt")` visits direct `.txt` children only. `open(..., encoding="utf-8")` converts bytes from disk into Python text; `.read().strip()` reads each whole file and removes whitespace at both ends. `documents.append(text)` keeps document boundaries. `if __name__ == "__main__":` means the print runs when this file is executed directly, not when imported by `train.py`.

Type that first block and run:

```powershell
cd jsm_0.1
.\.venv\Scripts\python.exe data_loader.py
```

Find `i love coffee` in the list. **Why separate documents?** A next-token pair should not jump from the end of one file to the start of another.

### Split documents

Add `split_documents(documents, validation_fraction=0.2, seed=42)`. Its checks reject fewer than two documents and a fraction outside `(0, 1)`. `indices = list(range(len(documents)))` makes integer document positions. `random.Random(seed).shuffle(indices)` shuffles a private seeded random generator; repeating the call gives the same split. `round(... )` and `max(1, ...)` pick at least one validation document. A `set` makes membership checks cheap. The two comprehensions send whole documents to either training or validation, preserving boundaries.

**Question:** Why split **before** making overlapping windows? Because adjacent windows from one document share most tokens; putting some in validation would make validation deceptively easy.

### Make shifted windows

Add `create_language_model_windows(encoded_documents, sequence_length, stride=1)`. Reject nonpositive `sequence_length` and `stride`. For each token list, `final_start = len(token_ids) - sequence_length` and `range(0, final_start, stride)` enumerate starts that have a full input **and** one next target token. For each start, input is `token_ids[start:start + sequence_length]`; target is `token_ids[start + 1:start + sequence_length + 1]`. Append `(input_ids, target_ids)`.

Trace this *small explanation only* on paper: IDs `[10, 11, 12, 13]`, length `2` give `([10, 11], [11, 12])` and `([11, 12], [12, 13])`. Your actual corpus remains plain text; this list is just to see the indexing. If a document has `N` IDs, length `L`, stride `1`, it yields `max(N-L, 0)` windows.

## 3. Create `tokenizer.py`: the simplest word-level bridge

Reference: [`jsm/tokenizer.py`](../jsm/tokenizer.py). This is a *teaching stage*, not the tokenizer used by the final model. It helps you see what token IDs mean before learning byte-level BPE.

Read every operation in order: import `documents`; make `tokenized_documents`; call `document.split()` to split on whitespace; extend `all_words` only to build a vocabulary; `dict.fromkeys(all_words)` keeps the first occurrence of each unique word; enumerate words to make `word -> ID`; encode each document separately; invert the mapping to `ID -> word`; decode IDs; print under `if __name__ == "__main__"`.

Using `plain1.txt` and `plain2.txt`, words such as `i` and `coffee` repeat but should have one ID each. The six longer files add many other words. Punctuation stays attached (`coffee` and `coffee.` are different). Capitalization matters. A new word at inference has no ID and raises `KeyError`. These are reasons the real pipeline switches to byte-level BPE.

**Checkpoint:** `python tokenizer.py`. Verify that decoding each encoded document returns its original whitespace-separated words. Changing the set or order of text files can change IDs in this simple tokenizer. Do not use these IDs with a model trained by `subword_tokenizer.py`.

## 4. Create `embedding.py`: IDs become learned vectors

Reference: [`jsm/embedding.py`](../jsm/embedding.py). `torch.manual_seed(42)` makes initial random values reproducible. `nn.Embedding(num_embeddings=len(vocabulary), embedding_dim=3)` creates a table: one row per word, three trainable numbers per row. `torch.tensor(token_ids)` turns an ID list into an integer tensor. `embedding(ids)` selects rows; it does **not** look up definitions or understand meaning yet. The `zip(words, vectors)` loop prints a word beside its current vector.

**Shapes:** For three words, IDs have shape `[3]`; vectors have `[3, 3]`. After learning, the table changes. Without training, these are random values.

**Checkpoint:** `python embedding.py`; record the vector for `coffee`, rerun, and see the same initial value because of the seed.

## 5. Follow the small `lessons/` scripts before the transformer

Create a `lessons` folder and type each reference file as an experiment. Run from `jsm_0.1` as `python -m lessons.output`, etc. The word scripts use the **whole** `data/raw` corpus but expect literal words `i`, `love`, `drink`, and `coffee`; the copied `plain*.txt` files supply them. Several scripts execute immediately on import, so run them as scripts.

| Create in this order | Read these key lines and answer this question |
| --- | --- |
| [`lessons/output.py`](../jsm/lessons/output.py) | `embedding.weight[love_id]` selects one row; `nn.Linear(3, len(vocabulary))` makes one score per word; `softmax(dim=0)` normalizes scores. Why is `argmax` only a guess before training? |
| [`lessons/training.py`](../jsm/lessons/training.py) | Squared error against a manually chosen 3-number target; `loss.backward()` fills `.grad`; `torch.no_grad()` protects the manual update; `.grad.zero_()` prevents gradient accumulation. This target is a **demonstration**, not language-model data. |
| [`lessons/next_token_training.py`](../jsm/lessons/next_token_training.py) | Target is `coffee` after `love`; `CrossEntropyLoss` takes logits and an integer target; `unsqueeze(0)` adds a batch dimension; SGD updates the output layer. Why can this single example be memorized? |
| [`lessons/sequence_training.py`](../jsm/lessons/sequence_training.py) | Each document yields adjacent word pairs; optimizer owns both embedding and output weights; every pair clears gradients, computes loss, backpropagates, and steps. See the caution below before running. |
| [`lessons/context_training.py`](../jsm/lessons/context_training.py) | Two-word context predicts the third; `.mean(dim=0)` loses order. What happens if you swap the two context words? |
| [`lessons/position_test.py`](../jsm/lessons/position_test.py) | Position embedding adds an order signal; `.flatten()` preserves both positions in a six-number vector. Compare `['i','love']` with `['love','i']`. |
| [`lessons/attention_test.py`](../jsm/lessons/attention_test.py) | The weights `[0.2, 0.8]` are chosen by hand only to explain weighted sum. `unsqueeze(1)` changes `[2]` into `[2,1]`, so each weight multiplies all 3 numbers in a token vector. |
| [`lessons/qkv_test.py`](../jsm/lessons/qkv_test.py) | Three learned linear layers create Q, K, V; `Q @ K.T / sqrt(d_k)` gives scores; upper-triangular mask hides future words; softmax gives weights; weights `@ V` gives contextual vectors. |
| [`lessons/self_attention.py`](../jsm/lessons/self_attention.py) and [`self_attention_test.py`](../jsm/lessons/self_attention_test.py) | Move those Q/K/V operations into an `nn.Module.forward`; confirm input and output shapes both `[2,3]`. This simplified class is separate from the final multi-head class. |
| [`lessons/feed_forward_test.py`](../jsm/lessons/feed_forward_test.py) and [`transformer_block_test.py`](../jsm/lessons/transformer_block_test.py) | After building the final `feed_forward.py` and `transformer_block.py`, see that each preserves `[2,3]`. |
| [`lessons/overfitting_demo.py`](../jsm/lessons/overfitting_demo.py) | A model trains on one hard-coded ID sequence and evaluates on another. Both are **diagnostic tensors**, not your corpus. Train loss can fall while held-out loss does not. |

**Caution about `sequence_training.py`:** The reference ends by saving into a relative `artifacts/` path and has a duplicate final print block. Create `artifacts` first if you run it. It writes an *older word-level* checkpoint named `tiny_model.pt`; the later transformer training uses that same name for a different format. Either remove/rename the old teaching artifact before full training, or skip its save section. Do not load it in `inference.py`.

## 6. Create `subword_tokenizer.py`: real text to stable byte IDs

Reference: [`jsm/subword_tokenizer.py`](../jsm/subword_tokenizer.py). This is the tokenizer the final project uses. Create [`train_tokenizer.py`](../jsm/train_tokenizer.py) after it; that small CLI reads `--vocab-size`, trains from `data/raw/*.txt`, and prints the resulting size.

Read `subword_tokenizer.py` top to bottom in these groups:

1. **Imports and constants.** `json` serializes learned merges. `Path` reads and writes files. Four special tokens are reserved: `<BOS>` starts an empty prompt or document, `<EOS>` marks an end, `<PAD>` is reserved for possible padding, and `<UNK>` is reserved but ordinary UTF-8 text can already be represented by bytes. Their IDs are `0..3` in that order.
2. **`Encoding`.** The small dataclass wraps `ids: list[int]`; `tokenizer.encode(text).ids` accesses the list.
3. **`__init__`.** `merges or []` starts with no learned merges. `bytes([value])` makes each one-byte piece from `0` through `255`. A byte token's ID starts at `4`; therefore the minimum vocabulary is `4 + 256 = 260`. Merged byte strings get later IDs. `bytes_to_id` is a reverse lookup.
4. **`_merge_pair`.** Walk a sequence left to right. If adjacent pieces equal the chosen pair, append their concatenation and skip both; otherwise append the current piece. This is how a learned pair is applied to a document.
5. **`train`.** Reject vocabularies smaller than `260`. Convert each document to UTF-8 bytes, then to one-byte pieces. Count adjacent pairs across documents. Sort candidates by descending frequency, then by pair bytes so ties are deterministic. Choose the first pair that produces a new byte string. Add it, merge all document sequences, and repeat until the requested size or no candidate remains. `self.__init__(self.merges)` rebuilds lookup tables after training. With a small corpus, fewer than `vocab_size - 260` merges may be possible.
6. **`encode`.** Start from the text's UTF-8 bytes, replay the learned merges **in training order**, then map pieces to IDs. Unicode characters can occupy multiple bytes before merging; tokens are byte pieces, not necessarily whole words.
7. **`decode`.** Ignore special IDs by default, join byte pieces, and decode UTF-8. `errors="replace"` avoids crashing if a sequence ends in the middle of a multibyte character; a partial token can show `�` until more bytes arrive. `id_to_token` is useful for inspecting an ID, but its displayed string can also contain replacement characters.
8. **Save/load.** Each side of a merge is hex text in JSON. `save` makes the parent directory. `load` checks the artifact type and reconstructs the byte pairs. Never manually reorder merge rows: their order affects encoding.
9. **Helpers.** `train_tokenizer` reads sorted `.txt` paths and calls `.strip()`; `load_tokenizer` reads the JSON; `load_or_train_tokenizer` loads an existing artifact if present; `encode_documents` wraps each document with BOS and EOS IDs.

**First checkpoint:** Run `python train_tokenizer.py --vocab-size 300`; look at `artifacts/tokenizer/tokenizer.json`. Open a Python session from `jsm_0.1` and try:

```python
from subword_tokenizer import load_tokenizer
t = load_tokenizer()
text = "i love coffee"
ids = t.encode(text).ids
print(ids, t.decode(ids), t.get_vocab_size())
assert t.decode(ids) == text
```

This checks exact round-trip of **actual text**. Training the tokenizer again on changed raw text can assign different IDs while keeping the same vocabulary size. Delete or deliberately rebuild your own tokenizer and model artifacts **together** when you change the corpus; the project only checks vocabulary size at inference, not tokenizer identity.

## 7. Create `dataset.py`: PyTorch receives windows

Reference: [`jsm/dataset.py`](../jsm/dataset.py). `Dataset` is a protocol for indexed examples. `__init__` calls your `create_language_model_windows` once and rejects zero windows. `__len__` returns the window count. `__getitem__(index)` returns two `torch.long` tensors, because embedding tables and cross-entropy targets require integer IDs.

After `encode_documents`, a sample may start with BOS, then bytes from a `.txt` document, and end with EOS. For `sequence_length=16`, each sample's input and target shapes are `[16]`. `DataLoader(..., batch_size=2)` stacks them into `[2,16]`. `shuffle=True` reorders **training windows**, not words within a window.

**Checkpoint:** Inspect `dataset[0]`: print both tensors, verify `input_ids[1:]` equals `target_ids[:-1]`, and inspect the final target. Do this using your tokenizer on actual `documents`.

## 8. Create `config.py` and `device.py`: model rules and hardware

References: [`jsm/config.py`](../jsm/config.py), [`jsm/device.py`](../jsm/device.py).

`@dataclass(frozen=True)` makes a configuration object whose fields cannot be reassigned. `vocab_size` has no default because it must match the tokenizer. `max_seq_len=16` is the number of input positions, `embedding_dim=32` is vector width, `num_heads=4` gives head width `32/4=8`, `num_layers=2` repeats transformer blocks, and `ffn_multiplier=4` expands feed-forward width to `128`. `num_kv_heads=None` means as many key/value heads as query heads; a smaller divisor enables grouped-query attention. `dropout=0.0` disables random dropout here; `tie_embeddings=True` shares one weight table between input embeddings and output predictions.

In `__post_init__`, `asdict(self)` exposes field values for checks. Positive fields must be at least 1, embedding width must divide evenly by heads, key/value head count must divide query head count, and dropout must lie in `[0,1)`. `device.py` tries CUDA, then Apple's MPS, then CPU. A device decides where tensors are stored; every model input and model parameter must be on the same device.

**Checkpoint:** Construct `ModelConfig(vocab_size=300)`; then try `embedding_dim=30, num_heads=4` and explain the error.

## 9. Create `attention.py`: causal multi-head attention

Reference: [`jsm/attention.py`](../jsm/attention.py). Work through it with shape symbols: `B=batch`, `T=current token count`, `P=past cached token count`, `D=embedding_dim`, `H=num_heads`, `Hkv=num_kv_heads`, `d=D/H`.

| Statement or group | Shape and meaning |
| --- | --- |
| `super().__init__()` | Registers child layers with PyTorch. |
| Divisibility checks | Make `d` and repeated K/V heads whole numbers. |
| Query/key/value `nn.Linear(..., bias=False)` | Learned projections. Q output width is `D`; K and V widths are `Hkv*d`. |
| `output_projection` and `Dropout` | Mix heads back into width `D`; optionally drop attention weights during training. |
| `single_sequence = vectors.dim() == 2`; `unsqueeze(0)` | Accept `[T,D]` by temporarily making `[1,T,D]`. |
| `Q = query_layer(vectors)` etc. | Initial projections have `[B,T,D]` for Q and `[B,T,Hkv*d]` for K/V. |
| `.view(...).transpose(1,2)` | Q becomes `[B,H,T,d]`; K/V become `[B,Hkv,T,d]`. |
| `torch.cat([past_key, K], dim=-2)` | When generating, append new K/V after cached past; total key length is `P+T`. `new_cache` stores **unrepeated** K/V. |
| `repeat_interleave(repeats, dim=1)` | Repeat each K/V head to pair it with query heads. With default `Hkv=H`, repeats is 1. |
| `Q @ K.transpose(-2,-1) / sqrt(d)` | Dot products yield `[B,H,T,P+T]` attention scores. Division keeps scale manageable. |
| Position comparison and `masked_fill(-inf)` | Future key positions get negative infinity. Softmax then assigns them probability zero. `past_length` makes the mask valid with a cache. |
| `softmax(..., dim=-1)` | Each query's weights across available keys sum to 1. |
| `attention_weights @ V` | Weighted sum of value vectors gives `[B,H,T,d]`. |
| `.transpose(...).contiguous().view(B,T,D)` | Move heads beside one another and combine their widths. `contiguous()` makes the memory layout suitable for `view`. |
| Output projection, optional `squeeze(0)`, optional cache return | Restore original rank and optionally return `(output, new_cache)`. |

**Checkpoint:** In a 2-token sequence with no cache, the attention score matrix is `[2,2]` per head. The first token must not use the second token's value. Explain why this causal mask is essential for next-token training.

## 10. Create `feed_forward.py` and `transformer_block.py`

References: [`jsm/feed_forward.py`](../jsm/feed_forward.py), [`jsm/transformer_block.py`](../jsm/transformer_block.py).

In `FeedForward`, `linear1` expands `D -> 4D` by default; `GELU` bends the values; dropout can zero some values during training; `linear2` contracts `4D -> D`; final dropout follows. It applies the **same learned transformation to each position**. For `[B,T,D]`, output stays `[B,T,D]`.

In `TransformerBlock.__init__`, construct attention, two `LayerNorm`s, the feed-forward network, and residual dropout. In `forward`, first normalize `vectors`, run attention, add its result back to the original (`residual_1`), normalize again, run feed-forward, and add it to `residual_1`. These are **pre-norm residual** steps. If caching is enabled, unpack attention's `(output, cache)` and return `(block_output, cache)`; otherwise return only the output. The two additions require matching shapes. Run the two reference shape tests in `lessons/` now.

## 11. Create `model.py`: assemble a tiny decoder

Reference: [`jsm/model.py`](../jsm/model.py). `TinyModel(nn.Module)` owns the complete next-token model.

| Code group | What to understand |
| --- | --- |
| `self.config = config` | Saves all architecture choices with the model. |
| Token embedding | Maps IDs `[B,T]` to `[B,T,D]`; its row count is `vocab_size`. |
| Position embedding | Maps positions `0..max_seq_len-1` to `[T,D]`; addition broadcasts across batches. |
| Embedding dropout | Applied after token and position vectors are added. |
| `nn.ModuleList([... for _ in range(num_layers)])` | Registers each block's independent trainable parameters. A plain Python list would not register them correctly. |
| Final `LayerNorm` and `lm_head` | Normalize hidden vectors; make `vocab_size` scores at **every** position. |
| `lm_head.weight = embedding.weight` | Ties the weight matrix; output head bias remains separate. Count unique parameters once. |
| Input rank check | Accepts `[T]` or `[B,T]`. |
| Cache length check | Rejects prompt plus past cache beyond `max_seq_len`. |
| `torch.arange(past_length, past_length+T, device=...)` | Gives new tokens the correct positions during cached generation. |
| Block loop | Feeds each block's output into the next and keeps one K/V cache per block. |
| Return | Logits are `[T,V]` for a single sequence or `[B,T,V]` for a batch; with cache, return `(logits, new_caches)`. |

**Paper trace:** With `B=2`, `T=16`, `D=32`, `V=300`, input IDs are `[2,16]`, embeddings `[2,16,32]`, each block output `[2,16,32]`, and logits `[2,16,300]`. No softmax is needed before `CrossEntropyLoss`: it expects raw logits.

## 12. Create the small support files before training

| File | Read each operation in the original |
| --- | --- |
| [`utils.py`](../jsm/utils.py) | `count_parameters` sums `.numel()` for total and trainable parameters. `parameter_breakdown` uses object IDs to avoid double-counting the tied embedding/head weight. |
| [`metrics.py`](../jsm/metrics.py) | `perplexity(loss)` is `exp(loss)` with an overflow fallback to infinity. It is based on average token loss. |
| [`training_utils.py`](../jsm/training_utils.py) | Validate step counts and bounds; linearly warm up learning rate; then use a cosine curve down to `minimum_multiplier`. The returned number multiplies the optimizer's base learning rate. |
| [`precision.py`](../jsm/precision.py) | `fp32` returns `nullcontext` (no cast). `fp16` or `bf16` use CUDA autocast, with BF16 support checked. Start on `fp32`; the reference has no gradient scaler for `fp16`. |
| [`checkpoint.py`](../jsm/checkpoint.py) | Save model, optimizer, scheduler, epoch, step, and config with `torch.save`. Load with `weights_only=True`; rebuild `ModelConfig`, then `TinyModel`, then load weights. Restore optimizer and scheduler for a resume. |

The save function expects its parent `artifacts` folder to exist. Your tokenizer save creates `artifacts/tokenizer`, which also creates `artifacts`. If you skip tokenizer training, make `artifacts` before checkpointing.

## 13. Create `train.py`: one full training pass

Reference: [`jsm/train.py`](../jsm/train.py). This script runs at import time; execute it as a program. Type one section, then explain what it consumes and produces before typing the next.

1. **Imports and arguments.** Import all helpers. `--epochs` defaults to 50, `--resume` reloads a checkpoint, and `--precision` chooses numeric format. `torch.manual_seed(42)` controls random initialization and shuffling behavior within a run.
2. **Lengths and batch size.** `max_seq_len=16` caps input positions; `sequence_length=16` makes windows that size; `batch_size=2` stacks two windows.
3. **Tokenize and split.** `load_or_train_tokenizer()` gets a JSON tokenizer or trains one; `encode_documents()` adds BOS/EOS to every raw-text document; `split_documents(..., seed=42)` holds out whole encoded documents. `vocab_size` must come from this tokenizer.
4. **Datasets and loaders.** Make separate `LanguageModelDataset`s. Training loader shuffles; validation does not. Print the first batch shapes. An error about no windows means your held-out document is too short; add longer real text or reduce `sequence_length` consistently with `max_seq_len`.
5. **Model and loss.** Build `ModelConfig`, instantiate `TinyModel`, move it to `device`, print parameter counts. `nn.CrossEntropyLoss()` scores each target ID against a row of raw vocabulary logits.
6. **Optimizer and scheduler.** `AdamW` changes parameters using gradients; `weight_decay` penalizes many weights. `total_steps` counts all batches over all epochs. `LambdaLR` multiplies the base learning rate by your warmup/cosine helper. `clip_grad_norm_` limits extremely large gradient norms.
7. **Optional resume.** `torch.load(..., weights_only=True)` reads your checkpoint. Check config equality, then restore model/optimizer/scheduler and the next epoch number. Use the same tokenizer artifact, corpus, architecture, and training schedule for a meaningful resume.
8. **Training loop.** `model.train()` enables training behavior. Move both batches to the device. `model(input_batch)` gives `[B,T,V]`. `reshape(-1,V)` makes `[B*T,V]`; target `reshape(-1)` makes `[B*T]`. Loss compares all positions at once. `zero_grad`, `backward`, clip, `optimizer.step`, then `scheduler.step` is the update order. Sum `.item()` only for reporting.
9. **Validation.** Every five epochs and on the last epoch, `model.eval()` disables dropout; `torch.no_grad()` avoids building a gradient graph. Compute mean held-out loss and perplexity. Inspect both training and validation; low training loss alone can mean memorization.
10. **Quick prediction.** For `i love` and `i drink`, encode text and take `logits[-1]`, because the final input position predicts the next token. Softmax turns logits into probabilities; `topk` prints likely IDs. These prompts come from the short plain-text files.
11. **Save.** Store model, optimizer, scheduler, final epoch, global step, and config. The tokenizer JSON is already saved separately.

**Run:** `python train.py --epochs 2` first. Once the flow works, run more epochs if you want. Reusing an old checkpoint with `--resume` is meaningful only when its training settings match. In the reference, the learning-rate schedule is rebuilt from the current `--epochs`; changing that argument while resuming changes the schedule.

## 14. Create `evaluate.py`: measure what was held out

Reference: [`jsm/evaluate.py`](../jsm/evaluate.py). `evaluate_loader` uses `CrossEntropyLoss(reduction="sum")` so each token contributes to a total. It flattens logits and targets, counts exact `argmax` matches, and divides by `total_tokens`. It reports mean loss, `exp(loss)` perplexity, next-token accuracy, and token count. `main()` loads your tokenizer and model, recreates the same document split, builds a validation loader, then also prints deterministic (`temperature=0`) generation samples.

**Checkpoint:** Run `python evaluate.py`. This validation set is tiny and drawn from the same writing style, so metrics are teaching signals, not evidence of a useful general model. The reference trains its tokenizer on **all** raw documents before the model split; this exposes validation text to tokenizer training. For a rigorous study, split documents first, fit BPE only on training text, and reuse that tokenizer for validation.

## 15. Create `generation.py` and `inference.py`: use your model

References: [`jsm/generation.py`](../jsm/generation.py), [`jsm/inference.py`](../jsm/inference.py).

In `sample_next_token`, reject invalid temperature/top-k/top-p. Temperature `0` chooses `argmax` (same output for the same prompt). Positive temperature divides logits: smaller sharpens, larger flattens. `top_k` leaves the K highest scoring IDs; `top_p` sorts probabilities and keeps the smallest prefix reaching the probability threshold. Masked logits become `-inf`, softmax yields probabilities, and `torch.multinomial` samples one ID. Top-k and top-p are selection rules applied *after* the model makes logits; they do not change learned weights.

In `generate`, `@torch.no_grad()` prevents gradient tracking. Encode the prompt; use BOS for an empty one. Put IDs in shape `[1,T]` on the model's device. Each loop either supplies the last token with K/V cache or the last `max_seq_len` tokens without cache. Take `logits[:, -1, :]`, sample one ID, append it, stop on EOS, and decode the whole sequence. When the cache reaches the context limit, reset it so the next pass can rebuild from a cropped context. Generation cannot know facts absent from this tiny corpus; random output is expected.

In `inference.py`, parse a prompt and sampling options, load tokenizer JSON and model checkpoint, compare vocabulary sizes, then call `model.eval()`. `run_prompt` calls `generate`, separately computes next-token probabilities for the prompt, and prints both continuation and top five token candidates. The interactive loop repeats until `exit` or `quit`.

**Run:** `python inference.py "i love" --max-new-tokens 8 --temperature 0`. Try `--interactive` only after the single-prompt command works. A prompt longer than the model context is cropped for prediction. Generation uses the same tokenizer that was used to train the model.

## 16. Inspect shapes and scaling only after the basic run works

| File | Purpose and limits |
| --- | --- |
| [`shape_debug.py`](../jsm/shape_debug.py) | `inspect_shapes` accepts `[T]` or `[B,T]`, derives expected embedding/Q/K/V/score shapes from config, runs the model, and returns a dictionary. These are calculated shapes, not hooks into each internal layer. |
| [`debug_shapes.py`](../jsm/debug_shapes.py) | Loads your checkpoint and tokenizer, encodes `language models learn`, takes a context-sized slice, prints the shape dictionary. Run `python debug_shapes.py`. |
| [`scaling.py`](../jsm/scaling.py) | Estimates parameter counts from vocabulary, positions, attention, feed-forward, norms, and output head. Its simple `4*D*D` attention estimate assumes ordinary equal query/key/value head counts; it does not model smaller `num_kv_heads`. |
| [`scale_configs.py`](../jsm/scale_configs.py) | Stores named size examples in `ScaleConfig`; `parameter_estimate()` calls the estimator. “Conceptual” entries are planning examples, not trained models. |
| [`scale_report.py`](../jsm/scale_report.py) | Prints estimated parameters and context for each named size. |
| [`memory.py`](../jsm/memory.py) | Adds rough bytes for parameters, gradients, two AdamW state tensors, hidden activations, and attention scores. Its total is explicitly a **lower bound**, not a promise of actual RAM or VRAM use. |

## 17. Finish with a code-reading exercise

Take the real text `i love coffee` and write this chain in your own notes:

```text
raw UTF-8 text
-> byte pieces and BPE merges
-> integer token IDs, with BOS and EOS for documents
-> 16-token input/target window
-> [B,T] integer tensors
-> [B,T,D] token+position vectors
-> Q/K/V, masked attention, feed-forward blocks
-> [B,T,V] logits
-> cross-entropy against the shifted targets
-> backward gradients and AdamW update
-> checkpoint, then a next-token sample
```

At each arrow, name the **exact file and function** that performs it. Then answer without looking: Why is the target shifted by one? Why is the attention mask triangular? Why does the output have one vocabulary score per position? What is saved in the tokenizer JSON versus the `.pt` checkpoint? If you can answer those, you can read the project rather than merely run it.

## Reference inventory: every original file

Use this list to confirm you have accounted for the whole `jsm` folder. Create the files in lesson order, which differs from alphabetical order.

| Original files | Role in this course |
| --- | --- |
| `requirements.txt`, `paths.py`, `data_loader.py`, `data/raw/*.txt` | Environment, paths, source documents, and windows: lessons 0–2. |
| `tokenizer.py`, `embedding.py`, all 13 `lessons/*.py` scripts | Word-level and tensor intuition: lessons 3–5 and the individual script table. |
| `subword_tokenizer.py`, `train_tokenizer.py`, `artifacts/tokenizer/tokenizer.json` | Byte-level BPE and saved merge rules: lesson 6. JSON is learned data, not a Python file to type. |
| `dataset.py`, `config.py`, `device.py` | Training examples and model settings: lessons 7–8. |
| `attention.py`, `feed_forward.py`, `transformer_block.py`, `model.py` | Decoder architecture: lessons 9–11. |
| `utils.py`, `metrics.py`, `training_utils.py`, `precision.py`, `checkpoint.py`, `artifacts/tiny_model.pt` | Training helpers and checkpoint: lesson 12. `.pt` is binary learned state, not text code. |
| `train.py`, `evaluate.py`, `generation.py`, `inference.py` | Fit, score, and use the model: lessons 13–15. |
| `shape_debug.py`, `debug_shapes.py`, `scaling.py`, `scale_configs.py`, `scale_report.py`, `memory.py` | Shape and resource inspection: lesson 16. |

The original `jsm/artifacts/tiny_model.pt` is a binary checkpoint, so read it through `checkpoint.py`; the original tokenizer JSON can be opened as text to see its special tokens and hex merge pairs. The original six `mini_*.txt` files and two `plain*.txt` files are copied into this course's `data/raw` so each stage starts with actual plain text.
