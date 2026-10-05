# JSM from scratch — the backend course

This course walks through every backend and AI file in this project as it exists today: what each file is for, what goes in, what comes out, and what each important line does, both in Python and in terms of how a language model works.

It describes the **current MVP baseline**. Nothing here is a plan or a proposal; where the code has gaps or oddities, they are described as they are and collected in Appendix B.

**What is covered:** `paths.py`, `configs/`, everything under `src/` (corpus factory, dataset, tokenization, model, training, evaluation, inference, serving), `scripts/`, and `tests/`.

**What is not covered:** the frontend apps under `apps/`. The serving chapter mentions only that the server hands out their pre-built files.

**How to read it**

- Chapters follow the life of the data: a file is uploaded, checked, cleaned, turned into token ids, used to train a model, and finally the model answers a request.
- Every file section shows the real code in small pieces, each followed by its explanation.
- Each major stage opens with an INPUT / PROCESS / OUTPUT / WHY IT EXISTS table.
- Each chapter ends with "What I should understand before moving on" and a self-test. The answers are folded away beneath the questions; try first, then open them.
- All paths are relative to the project directory, `jsm_0.1/`. Commands are run from there.

## Contents

1. Project and root architecture
2. `paths.py`
3. `configs/`
4. The corpus factory
   - 4.1 Acquisition
   - 4.2 Inspection
   - 4.3 Provenance
   - 4.4 Ingestion
   - 4.5 Extraction
   - 4.6 Preprocessing: cleaning, normalization, filtering, deduplication
5. Dataset
6. Tokenization
7. The model
8. Training
9. Evaluation
10. Inference
11. The serving backend
12. Scripts — what each command runs
13. End to end: from an uploaded file to a live response
14. Numbers from our current JSM MVP
15. The full system map

- Appendix A. The test suite
- Appendix B. Things to revisit after the course

---

## 1. Project and root architecture

| | |
|---|---|
| **INPUT** | Files you drop into `storage/uploads/`, plus two JSON settings files in `configs/`. |
| **PROCESS** | A chain of small scripts. The first half turns uploaded files into clean training text (the corpus factory). The second half turns that text into a tokenizer, a trained model, and an HTTP API. |
| **OUTPUT** | Data under `storage/` and model outputs under `artifacts/`. |
| **WHY IT EXISTS** | So that every step from "a file on disk" to "a model answering a request" is a separate piece of code you can read, run and check on its own. |

### 1.1 Directory map

Everything below is relative to the project directory, `jsm_0.1/`. All commands in this course are run from there.

**Top level**

| Entry | What it holds |
|---|---|
| `paths.py` | Every directory and file location the project uses, defined once (chapter 2). |
| `config.py` | Empty file (0 bytes). Nothing imports it. |
| `requirements.txt` | The four third-party packages to install. |
| `configs/` | Two JSON settings files: `training.json` and `inspection.json` (chapter 3). |
| `src/` | All library code. Functions and classes live here; nothing in `src/` runs by itself. |
| `scripts/` | One small entry-point script per pipeline step. These are what you run. |
| `storage/` | Data: uploads, batches, extracted and processed text, training datasets. |
| `artifacts/` | Model outputs: tokenizer, checkpoints, run records. |
| `tests/` | One test file, `test_inspection.py`, for the inspection stage. |
| `docs/` | Four notes files (described in 1.4). |
| `COURSE.md` | This course. |
| `apps/` | Frontend clients, not covered by this course. |
| `.venv/` | The Python virtual environment (the installed interpreter and packages). Not project code. |

**`src/`**

| Entry | What it holds |
|---|---|
| `src/README.md` | A flow diagram of the whole pipeline. |
| `src/corpus_factory/` | The data half. One sub-folder per stage, listed in the next table. |
| `src/dataset/` | `builder.py` (splits documents into train/validation/test files) and `loader.py` (reads them back). |
| `src/tokenization/` | `bpe.py` (learns the vocabulary) and `tokenizer.py` (text to token ids and back). |
| `src/model/` | `config.py`, `embeddings.py`, `attention.py`, `transformer.py`, `model.py`: the neural network. |
| `src/training/` | `config.py`, `run.py`, `checkpoint.py`, `trainer.py`, and `optimizer.py` (empty). |
| `src/evaluation/` | `evaluator.py`: measures loss on held-out data. |
| `src/inference/` | `generator.py`: produces text from a prompt. |
| `src/serving/` | `server.py`, `model_manager.py`, `admin.py`: the HTTP API. |

`src/` also contains six folders named `acquisition`, `extraction`, `ingestion`, `inspection`, `preprocessing` and `provenance` directly under `src/`. They contain no source files, only `__pycache__` folders left behind from before these stages were moved into `src/corpus_factory/`. Ignore them; the real code is under `src/corpus_factory/`.

**`src/corpus_factory/`**

| Entry | What it holds |
|---|---|
| `README.md` | The six stage names in order. |
| `acquisition/` | `intake.py`, `hashing.py`, `discovery.py`, `batch.py`, `README.md` (chapter 4.1). |
| `inspection/` | `config.py`, `checks.py`, `deep_inspection.py`, `inspector.py`, `quarantine.py`, `report.py`, `result.py`, `__init__.py`, `README.md`, and an empty `.gitkeep`. |
| `provenance/` | `decision.py`, `gate.py`. |
| `ingestion/` | `ingest.py`, `loader.py`, `document.py`, `dispatcher.py`, `worker.py`, `README.md`. |
| `extraction/` | `extractor.py` and `readers/` (`txt_reader.py` has code; `pdf_reader.py`, `docx_reader.py`, `md_reader.py` are empty files; the extraction chapter says what uses them). |
| `preprocessing/` | `cleaning.py`, `normalization.py`, `filtering.py`, `deduplication.py`, `README.md`, and four empty folders of the same names that hold only a `.gitkeep`. |

**`scripts/`**

| Entry | What it runs |
|---|---|
| `acquisition.py`, `inspection.py`, `provenance.py`, `provenance_review.py`, `ingestion.py`, `extraction.py` | The first corpus-factory stages. |
| `cleaning.py`, `normalization.py`, `filtering.py`, `deduplication.py` | The four preprocessing stages. |
| `dataset_building.py`, `tokenizer_training.py`, `tokenize_dataset.py` | Dataset and tokenizer steps. |
| `train.py`, `evaluate.py`, `inference.py`, `model_stats.py`, `serve.py` | Model steps. |
| `README.md` | The commands in the order you run them. |

**`configs/`, `tests/`, `docs/`**

| Entry | What it holds |
|---|---|
| `configs/training.json` | Training settings (5 keys). |
| `configs/inspection.json` | Inspection policy (22 keys). |
| `tests/test_inspection.py` | `unittest` tests for the inspection stage (402 lines). It is the only test file. |
| `docs/pipeline.md`, `docs/steps.md`, `docs/reminders.md`, `docs/COURSE.md` | Notes (1.4). |

**`storage/`** (data; one line per directory, and which stage writes it)

| Directory | Written by | Holds |
|---|---|---|
| `storage/uploads/` | you | The files you supply. One sub-folder per source, or loose files. |
| `storage/incoming/batches/<batch_id>/` | acquisition | A copy of the uploaded files in `objects/`, plus `source.json` and `source.json.sha256`. |
| `storage/catalog/inspections/<inspection_id>/` | inspection | One report per inspection run of a batch. |
| `storage/quarantine/<batch_id>/<inspection_id>/` | inspection | What inspection sets aside for files that did not pass (see the inspection chapter). |
| `storage/catalog/provenance/<decision_id>/` | provenance | One record per rights decision. |
| `storage/raw/<batch_id>/` | ingestion | The trusted copy of an approved batch's accepted files: `objects/`, `manifest.json`, `manifest.json.sha256`. |
| `storage/extracted/<batch_id>/` | extraction | One plain-text file per document. |
| `storage/processed/cleaned`, `normalized`, `filtered`, `deduplicated` | the four preprocessing stages | The text after each preprocessing stage, again one folder per batch. |
| `storage/training/dataset/` | dataset building | `train.jsonl`, `validation.jsonl`, `test.jsonl` (text). |
| `storage/training/tokenized/` | tokenize dataset | The same three files as token ids. |

**`artifacts/`** (model outputs)

| Directory | Written by | Holds |
|---|---|---|
| `artifacts/tokenizer/` | tokenizer training | `tokenizer.json`. |
| `artifacts/checkpoints/` | training | `tiny_model.pt` (the current model) and numbered files such as `checkpoint_epoch_000021_step_000000063.pt`. |
| `artifacts/runs/<run_id>/` | training | `run.json`, a record of one training run. |
| `artifacts/logs/`, `artifacts/evaluations/` | nothing | Empty apart from a `.gitkeep`. No code writes here. |

### 1.2 The two halves

**The corpus factory (data).** Code in `src/corpus_factory/` plus `src/dataset/`. It starts with whatever files you upload and ends with three text files in `storage/training/dataset/`. Nothing in this half knows what a neural network is. Its job is to make sure the text is the text you meant to train on: copied without change, checked for safety, approved for use, extracted, cleaned, and split.

**The model side.** `src/tokenization/`, `src/model/`, `src/training/`, `src/evaluation/`, `src/inference/`, `src/serving/`. It starts from those three text files and produces a tokenizer, a trained set of weights, and an API that generates text.

The two top-level data directories follow the same split:

- `storage/` is **data**. It can be very large, it may contain private or licensed material, and every stage's output can be rebuilt from `storage/uploads/` by re-running the scripts.
- `artifacts/` is **what the model side produced from the data**: a vocabulary and weights. These are the things you would copy to another machine to run the model. You do not need `storage/` to run inference; you need `artifacts/tokenizer/tokenizer.json` and a checkpoint.

One overlap to be aware of: the tokenized dataset is model-side output, but it lives in `storage/training/tokenized/` because it is training data, not something you ship with the model.

### 1.3 How code is run

You always stand in the project directory and run a script as a module:

```
cd jsm_0.1
source .venv/bin/activate
python -m scripts.acquisition
```

`python -m scripts.acquisition` means "find the module `scripts.acquisition` and run it as the main program". The part that matters is what Python does to its import search path, `sys.path`, when started with `-m`: it puts the **current directory** first. Because the current directory is the project directory:

- `from paths import UPLOADS_DIR` finds `paths.py`, which sits in the project directory.
- `from src.corpus_factory.acquisition.intake import read_uploads` finds the folder `src/`, then `corpus_factory/`, then `acquisition/`, then the file `intake.py`.
- `scripts.acquisition` itself is found as the file `scripts/acquisition.py`.

If you ran `python scripts/acquisition.py` instead, Python would put `scripts/` first on the search path, not the project directory, and `from paths import ...` would fail. The same failure happens if you run from another directory. This was checked from a different directory:

```
ModuleNotFoundError: No module named 'paths'
```

No file in the project edits `sys.path`, so the rule is strict: project directory, `python -m`.

You will notice that most folders have no `__init__.py` file (only `src/corpus_factory/inspection/` has one, containing a single docstring). Python 3 treats a plain folder as a package for import purposes, so `src.model.model` works without them.

### 1.4 Root files

#### `requirements.txt`

```
torch
numpy
fastapi
uvicorn
```

No versions are pinned, so `pip install -r requirements.txt` installs whatever is newest. The environment used while writing this course has Python 3.12.3, `torch` 2.14.1, `numpy` 2.5.3, `fastapi` 0.142.2 and `uvicorn` 0.54.0.

| Package | What it is | What uses it |
|---|---|---|
| `torch` | PyTorch: tensors, neural-network layers, automatic gradients, optimizers. | Everything in `src/model/`, `src/training/`, `src/evaluation/`, `src/inference/`, `src/serving/model_manager.py`, and the model scripts. |
| `numpy` | Array library. | No file in the project imports it. PyTorch uses it if present and prints a warning if it is missing. |
| `fastapi` | Web framework: you write Python functions and it turns them into HTTP endpoints. It installs `pydantic` (request/response validation) and `starlette` with it. | `src/serving/server.py`, `src/serving/admin.py`. |
| `uvicorn` | The web server program that actually listens on a port and hands requests to the FastAPI app. | `scripts/serve.py`. |

Everything else the project imports (`json`, `hashlib`, `pathlib`, `re`, `secrets`, `datetime`, `dataclasses`, `zipfile`, `subprocess`, `unittest`, …) is part of Python's standard library and needs no installation.

The inspection stage can also use three optional outside tools if they happen to be installed: the Python package `magic` (imported inside a `try` in `src/corpus_factory/inspection/checks.py`), and the command-line programs `clamdscan`/`clamscan` and `pdfinfo`. None are in `requirements.txt`, and the code continues without them.

#### `config.py`

The file is empty: 0 bytes, 0 lines. Nothing imports it (there is no `import config` or `from config import` anywhere). Do not confuse it with the three files that do carry configuration code: `src/model/config.py`, `src/training/config.py` and `src/corpus_factory/inspection/config.py`.

#### `COURSE.md`

The file you are reading.

#### README files and `docs/`

| File | What it documents |
|---|---|
| `src/README.md` | A top-to-bottom arrow diagram of all stages, from "External / Hand-supplied Data" to "LIVE AI MODEL". No prose. |
| `src/corpus_factory/README.md` | The six corpus-factory stage names in order: Acquisition, Inspection, Provenance, Ingestion, Extraction, Preprocessing. |
| `src/corpus_factory/acquisition/README.md` | The acquisition stage: purpose, upload layout, `origin.json`, batch layout, manifest fields, duplicate protection. Compared against the code in 4.1. |
| `src/corpus_factory/inspection/README.md` | The inspection stage and how to run it. |
| `src/corpus_factory/ingestion/README.md` | A note (in Arabic) on the idea of distributed ingestion with a dispatcher and workers. |
| `src/corpus_factory/preprocessing/README.md` | Four lines (in Arabic) defining cleaning, normalization, filtering and deduplication. |
| `scripts/README.md` | The run commands in pipeline order, a one-line tokenizer test, and how to build and serve the web apps. |
| `docs/pipeline.md` | Two arrow diagrams: the acquisition-to-raw flow, and a numbered list of 15 stages. Only Acquisition and Inspection are ticked as done, which is out of date: all 15 have code now. |
| `docs/steps.md` | How to create the virtual environment and `pip install torch`, `fastapi`, `uvicorn`. It does not mention `numpy`. |
| `docs/reminders.md` | One reminder: the chain Tokens → Embeddings → Transformer → Logits → Softmax → Loss → Backpropagation → Gradients → Optimizer → Updated Weights. |
| `docs/COURSE.md` | An older beginner's course (327 lines). It describes a different layout: a neighbouring `jsm` folder and files such as `data_loader.py` and `subword_tokenizer.py`, with PowerShell commands. It does not describe the code in `jsm_0.1` as it is now. |

#### `../.gitignore` (at the git root, one level above the project)

The rules that concern `storage/` and `artifacts/`:

```
# Generated/runtime storage
jsm_0.1/storage/**
!jsm_0.1/storage/.gitkeep

# Keep test input files
!jsm_0.1/storage/uploads/
!jsm_0.1/storage/uploads/**

# Generated model artifacts
jsm_0.1/artifacts/**
!jsm_0.1/artifacts/.gitkeep
```

A `.gitignore` line is a pattern for paths git should not track. `**` matches anything at any depth. A line starting with `!` is an exception: "do track this after all". Later lines override earlier ones.

| Rule | Effect |
|---|---|
| `jsm_0.1/storage/**` | Ignore everything under `storage/`: batches, raw copies, extracted text, datasets. This is what keeps private data and large generated files out of git. |
| `!jsm_0.1/storage/.gitkeep` | Except a file `storage/.gitkeep`. That file does not exist. |
| `!jsm_0.1/storage/uploads/` and `!jsm_0.1/storage/uploads/**` | Except the `uploads` folder and everything in it. The sample upload files are tracked by git so the pipeline has test input after a fresh clone. Two lines are needed: git will not look inside an ignored folder, so the folder itself must be un-ignored first, then its contents. |
| `jsm_0.1/artifacts/**` | Ignore everything under `artifacts/`: the tokenizer, checkpoints (about 10 MB each) and run records. |
| `!jsm_0.1/artifacts/.gitkeep` | Except a file `artifacts/.gitkeep`. That file does not exist either. |

A `.gitkeep` is an empty file whose only purpose is to make git remember an otherwise empty folder (git tracks files, not folders). The `.gitkeep` files that do exist are one level deeper, for example `storage/raw/.gitkeep` and `artifacts/tokenizer/.gitkeep`. Those match the ignore rule, not the exception. They are in git anyway because they were added to git explicitly, and git keeps tracking a file once it is tracked. A new `.gitkeep` in a new sub-folder would be ignored.

The remaining rules ignore `__pycache__/`, `*.py[cod]` (compiled Python files), `.venv/`, `venv/`, and editor/OS files.

### 1.5 Python you will see everywhere

Later chapters assume these and refer back here.

**`pathlib.Path` and the `/` operator.** A `Path` is an object that represents a file location. Dividing a `Path` by a string joins them with the right separator.

```python
from pathlib import Path

folder = Path("storage") / "uploads"     # storage/uploads
file = folder / "notes.txt"              # storage/uploads/notes.txt
file.name                                # "notes.txt"
file.suffix                              # ".txt"
file.parent                              # storage/uploads
file.is_file()                           # True if it exists and is a file
```

**Type hints.** Notes after `:` and `->` that say what type a value should be. Python does not enforce them; they are for the reader and for editors.

```python
def count(words: list[str], limit: int | None = None) -> dict:
    ...
```

`list[str]` is a list of strings. `int | None` means "an integer or `None`". `-> dict` means the function returns a dictionary. `tuple[Path, ...]` means a tuple of any length whose items are all `Path`.

**f-strings.** A string with `f` in front evaluates whatever is inside `{}`.

```python
name = "notes.txt"
f"Saved: {name}"          # "Saved: notes.txt"
f"{7:08d}"                # "00000007"  (pad with zeros to 8 digits)
```

**`with open(...)`.** Opens a file and guarantees it is closed when the indented block ends, even if an error happens inside.

```python
with open("notes.txt", "r", encoding="utf-8") as file:
    text = file.read()
```

The second argument is the mode: `"r"` read text, `"w"` write text (replacing the file), `"rb"`/`"wb"` the same for raw bytes. Chapter 4.1 introduces `"x"`.

**`from x import y`.** Runs the file `x.py` (once) and makes the name `y` from it available here. `from src.model.config import ModelConfig` follows folders: `src/model/config.py`.

**`if __name__ == "__main__":` and `python -m scripts.x`.** Every file has a variable `__name__`. It equals `"__main__"` only in the file you launched. Code under this `if` therefore runs when you do `python -m scripts.x` and does not run when another file imports `scripts.x`.

```python
if __name__ == "__main__":
    print("run directly")
```

**`@dataclass`.** A shortcut for a class that only holds named values. Python writes the constructor for you.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(x=1, y=2)
p.x            # 1
```

`frozen=True` makes instances read-only: `p.x = 5` raises an error.

**Comprehensions and generator expressions.** A compact loop that builds a collection.

```python
[n * 2 for n in [1, 2, 3]]               # list: [2, 4, 6]
{w: len(w) for w in ["hi", "hello"]}     # dict: {"hi": 2, "hello": 5}
[n for n in [1, 2, 3] if n > 1]          # with a filter: [2, 3]
sum(n * 2 for n in [1, 2, 3])            # generator expression: 12
```

The last form has no brackets of its own. It produces the values one at a time and hands them straight to the function around it (`sum`, `sorted`, `tuple`, …) without building a list first.

**`try` / `except` / `finally`.** Run code that may fail; handle the failure; always run the clean-up.

```python
try:
    value = int("abc")
except ValueError:
    value = 0
finally:
    print("done")
```

**`raise ... from error`.** Raise a new, clearer error while keeping the original one attached as its cause, so the traceback shows both.

```python
try:
    int("abc")
except ValueError as error:
    raise ValueError("Bad number in config") from error
```

**Keyword arguments and trailing commas.** Arguments can be passed by name, one per line. The comma after the last one is allowed and is the style used throughout this project.

```python
result = train(
    epochs=3,
    learning_rate=0.0003,
)
```

## 2. `paths.py`

| | |
|---|---|
| **INPUT** | Nothing but its own location on disk. |
| **PROCESS** | Works out the project directory, then builds every other location from it with `/`. |
| **OUTPUT** | 25 module-level constants, each a `Path`. No file or folder is created. |
| **WHY IT EXISTS** | So a location such as "where batches live" is written in exactly one place, and every stage that writes it and every stage that reads it agree. |

#### `paths.py`

**Why this file exists.** A pipeline is a chain of "stage A writes a folder, stage B reads the same folder". If each stage typed its own folder names, one typo would silently break the chain: stage B would find nothing and report "no work". Here every location is a named constant that other files import.

**What enters / what leaves.** Nothing is passed in. The file reads one thing, the built-in variable `__file__`. It leaves 25 names that other files import, for example `from paths import BATCHES_DIR`. Importing `paths` does not touch the disk beyond resolving its own location: it creates no directories. Each stage creates its own output folder when it first writes.

**How it connects.** It is imported by 27 `from paths import ...` lines across `scripts/` and `src/`. It imports nothing from the project, so it can never be part of an import cycle.

**The code, section by section**

```python
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
```

`Path` is the class from the primer (1.5).

Read the second line from the inside out:

| Piece | Value (written relative to wherever the project sits) |
|---|---|
| `__file__` | The path of the file this code is in. Python sets it for every module. Here it is the path to `paths.py`. It may be relative or contain `..`, depending on how Python was started. |
| `Path(__file__)` | The same thing as a `Path` object. |
| `.resolve()` | Turns it into a full absolute path: starts from the filesystem root, removes any `..`, and follows symbolic links. |
| `.parent` | Drops the last component (`paths.py`), leaving the folder that contains it: the project directory `jsm_0.1`. |

**What Python does:** computes an absolute path to the folder holding `paths.py`, once, at the moment `paths` is first imported.

**What it means in the pipeline:** every other location is built from `PROJECT_DIR`, so every path in the project is absolute and does not depend on which directory you were in when you started Python. (You still must start from the project directory for the imports to work, as 1.3 explained. But once imports work, the data paths are fixed to the project's location, not to your current directory.)

All names here are in capitals. That is a Python convention for "constant: set once, never reassigned". Nothing enforces it.

```python
# Corpus storage pipeline
STORAGE_DIR = PROJECT_DIR / "storage"

UPLOADS_DIR = STORAGE_DIR / "uploads"

INCOMING_DIR = STORAGE_DIR / "incoming"
BATCHES_DIR = INCOMING_DIR / "batches"
```

Each line takes a `Path` already defined and appends one folder name with `/`. `BATCHES_DIR` is therefore `storage/incoming/batches` under the project.

```python
QUARANTINE_DIR = STORAGE_DIR / "quarantine"
RAW_STORAGE_DIR = STORAGE_DIR / "raw"
EXTRACTED_DIR = STORAGE_DIR / "extracted"
PROCESSED_DIR = STORAGE_DIR / "processed"
TRAINING_DATA_DIR = STORAGE_DIR / "training"
```

The rest of the data half. Note that there are no constants for the four preprocessing folders or for `dataset`/`tokenized`: the scripts build those themselves, for example `PROCESSED_DIR / "cleaned"` in `scripts/cleaning.py` and `TRAINING_DATA_DIR / "tokenized"` in `scripts/train.py`.

```python
# Model / training artifacts
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"

TOKENIZER_DIR = ARTIFACTS_DIR / "tokenizer"
TOKENIZER_PATH = TOKENIZER_DIR / "tokenizer.json"

CHECKPOINTS_DIR = ARTIFACTS_DIR / "checkpoints"
CHECKPOINT_PATH = CHECKPOINTS_DIR / "tiny_model.pt"

LOGS_DIR = ARTIFACTS_DIR / "logs"
EVALUATIONS_DIR = ARTIFACTS_DIR / "evaluations"
```

The naming rule in this file: `_DIR` is a folder, `_PATH` is one specific file. `TOKENIZER_PATH` is the single tokenizer file. `CHECKPOINT_PATH` is the single "current model" file, `tiny_model.pt`; a checkpoint is a saved copy of the model's weights (chapter 8).

```python
CATALOG_DIR = STORAGE_DIR / "catalog"
INSPECTIONS_CATALOG_DIR = CATALOG_DIR / "inspections"
PROVENANCE_CATALOG_DIR = CATALOG_DIR / "provenance"

RUNS_DIR = ARTIFACTS_DIR / "runs"
```

These four were added after the two commented groups and sit below them, so the file's grouping is slightly off: the three `CATALOG` constants are storage, and `RUNS_DIR` is an artifact.

```python
# Client apps (Next.js static exports, built with:
# cd apps && npm install && npm run build)
APPS_DIR = PROJECT_DIR / "apps"

WEBSITE_BUILD_DIR = (
    APPS_DIR / "public" / "website" / "web" / "out"
)
CHAT_BUILD_DIR = (
    APPS_DIR / "public" / "chat" / "web" / "out"
)
ADMIN_CONSOLE_BUILD_DIR = (
    APPS_DIR / "internal" / "admin_console" / "web" / "out"
)
```

The three `out` folders are where the frontend build puts finished static files. The serving backend hands those files to browsers (chapter 11). The parentheses only let the expression sit on its own line; they change nothing.

**Who writes and who reads each constant.** This table was built by searching every `.py` file for each name.

| Constant | Location | Written by | Read by |
|---|---|---|---|
| `PROJECT_DIR` | the project directory | nobody | The rest of this file; `src/training/config.py` and `src/corpus_factory/inspection/config.py` (to find the two files in `configs/`). |
| `STORAGE_DIR` | `storage/` | nobody directly | The rest of this file; `src/corpus_factory/inspection/report.py`, which builds `storage/catalog/inspections` from it on its own. |
| `UPLOADS_DIR` | `storage/uploads/` | you, by hand | `scripts/acquisition.py`; `src/serving/admin.py` (counts). |
| `INCOMING_DIR` | `storage/incoming/` | — | Only the next line of `paths.py`. No other file imports it. |
| `BATCHES_DIR` | `storage/incoming/batches/` | acquisition (`src/corpus_factory/acquisition/batch.py`) | `scripts/acquisition.py` (to detect repeats), `scripts/inspection.py`, `scripts/provenance.py`, `scripts/ingestion.py`, `src/serving/admin.py`. |
| `QUARANTINE_DIR` | `storage/quarantine/` | inspection (`inspection/quarantine.py`) | `inspection/report.py`, `src/serving/admin.py`. |
| `RAW_STORAGE_DIR` | `storage/raw/` | ingestion (`ingestion/ingest.py`) | `ingestion/loader.py`, `scripts/extraction.py`, `src/serving/admin.py`. |
| `EXTRACTED_DIR` | `storage/extracted/` | extraction (`scripts/extraction.py`) | `scripts/cleaning.py`, `src/serving/admin.py`. |
| `PROCESSED_DIR` | `storage/processed/` | `scripts/cleaning.py`, `normalization.py`, `filtering.py`, `deduplication.py` (each writes its own sub-folder) | Each of those reads the previous one's sub-folder; `scripts/dataset_building.py` reads `deduplicated`; `src/serving/admin.py`. |
| `TRAINING_DATA_DIR` | `storage/training/` | `scripts/dataset_building.py` (`dataset/`), `scripts/tokenize_dataset.py` (`tokenized/`) | `scripts/tokenizer_training.py` and `scripts/tokenize_dataset.py` (read `dataset/`); `scripts/train.py`, `scripts/evaluate.py`, `scripts/model_stats.py` (read `tokenized/`); `src/serving/admin.py`. |
| `ARTIFACTS_DIR` | `artifacts/` | — | Only later lines of `paths.py`. |
| `TOKENIZER_DIR` | `artifacts/tokenizer/` | — | Only the next line of `paths.py`. |
| `TOKENIZER_PATH` | `artifacts/tokenizer/tokenizer.json` | `scripts/tokenizer_training.py` | `scripts/tokenize_dataset.py`, `scripts/inference.py`, `scripts/model_stats.py`, `src/serving/server.py`. |
| `CHECKPOINTS_DIR` | `artifacts/checkpoints/` | Not through this name. Training writes into this folder because it is the parent of `CHECKPOINT_PATH`. | `src/serving/server.py` (to list the models it can serve). |
| `CHECKPOINT_PATH` | `artifacts/checkpoints/tiny_model.pt` | `scripts/train.py` (through `src/training/trainer.py` and `checkpoint.py`) | `scripts/train.py` (to resume), `scripts/evaluate.py`, `scripts/inference.py`, `scripts/model_stats.py`, `src/serving/server.py` (uses its file name as the default model). |
| `LOGS_DIR` | `artifacts/logs/` | nobody | **Unused.** No file imports it. |
| `EVALUATIONS_DIR` | `artifacts/evaluations/` | nobody | **Unused.** No file imports it. `scripts/evaluate.py` prints its result and writes no file. |
| `CATALOG_DIR` | `storage/catalog/` | — | Only the next two lines of `paths.py`. |
| `INSPECTIONS_CATALOG_DIR` | `storage/catalog/inspections/` | inspection, but not through this name: `inspection/report.py` uses its own `INSPECTIONS_DIR = STORAGE_DIR / 'catalog' / 'inspections'`. Same folder, defined twice. | `scripts/provenance.py`, `scripts/ingestion.py`, `src/serving/admin.py`. |
| `PROVENANCE_CATALOG_DIR` | `storage/catalog/provenance/` | provenance (`provenance/decision.py`) | `provenance/gate.py`, `src/serving/admin.py`. |
| `RUNS_DIR` | `artifacts/runs/` | `scripts/train.py` (through `src/training/run.py`) | `src/serving/admin.py`. |
| `APPS_DIR` | `apps/` | — | Only later lines of `paths.py`. |
| `WEBSITE_BUILD_DIR`, `CHAT_BUILD_DIR`, `ADMIN_CONSOLE_BUILD_DIR` | three `out/` folders under `apps/` | the frontend build | `src/serving/server.py`. |

Two constants are never used anywhere (`LOGS_DIR`, `EVALUATIONS_DIR`). Five exist only as stepping stones inside this file (`INCOMING_DIR`, `ARTIFACTS_DIR`, `TOKENIZER_DIR`, `CATALOG_DIR`, `APPS_DIR`).

## 3. `configs/`

| | |
|---|---|
| **INPUT** | Two JSON files you edit by hand. |
| **PROCESS** | A loader function reads each file into a Python `dict`. The inspection loader also validates every value. |
| **OUTPUT** | A `dict` passed to the training code, and a `dict` passed to the inspection code. |
| **WHY IT EXISTS** | So the numbers you are most likely to change between runs are not buried in code. |

JSON is a plain-text format for nested data. `{ }` is an object (it becomes a Python `dict`), `[ ]` is an array (a `list`), and `true`/`false` become `True`/`False`.

Not every setting lives here. The model's size (vocabulary, context length, layers) is in `src/model/config.py`, in code. `configs/` holds only training-loop settings and the inspection policy.

#### `configs/training.json`

**Why this file exists.** These are the five values you change when you want to train longer, train differently, or start over.

**What enters / what leaves.** `load_training_config()` in `src/training/config.py` opens the file and returns it as a `dict`. It checks only that the file exists and that the top level is a JSON object. It does not check the keys or their values.

**How it connects.** `scripts/train.py` calls the loader once at the start, reads three keys itself, and passes the whole `dict` on to `src/training/trainer.py`, which reads the other two. The whole `dict` is also copied unchanged into each run record (`src/training/run.py`) and each checkpoint (`src/training/checkpoint.py`), so you can later see which settings produced a model. Chapter 8 explains that code.

**The file**

```json
{
  "epochs": 21,
  "learning_rate": 0.0003,
  "resume": true,
  "checkpoint_every_epochs": 1,
  "keep_last_checkpoints": 3
}
```

| Key | Value now | Unit | Meaning | Read in | If the key is missing |
|---|---|---|---|---|---|
| `epochs` | `21` | passes over the training data | The epoch number to train **up to**. An epoch is one full pass over the training set. It is a target total, not "this many more": the loop runs from the last completed epoch plus one up to this number. If a resumed checkpoint has already completed 21 epochs, a run with `21` does no training. | `scripts/train.py` (`training_config["epochs"]`) | The script stops with `KeyError`. |
| `learning_rate` | `0.0003` | a plain number (no unit) | How big a step the optimizer takes each time it adjusts the weights. Chapter 8 explains it. | `scripts/train.py` (`training_config["learning_rate"]`) | `KeyError`. |
| `resume` | `true` | yes/no | If true, load `artifacts/checkpoints/tiny_model.pt` and continue from it. If false, start from fresh random weights. | `scripts/train.py` (`training_config.get("resume", True)`) | Treated as `true`. |
| `checkpoint_every_epochs` | `1` | epochs | Save a checkpoint after every this-many epochs. `0` or less turns the periodic save off. | `src/training/trainer.py` | `1`. |
| `keep_last_checkpoints` | `3` | files | How many numbered history checkpoints to keep; older ones are removed. | `src/training/trainer.py`, which passes it to `src/training/checkpoint.py` as `keep_last` | `3`. |

All five keys are read. The difference between `config["epochs"]` and `config.get("resume", True)` is ordinary Python: square brackets raise `KeyError` when the key is absent; `.get(key, default)` returns the default instead.

One thing you will notice on disk: `artifacts/checkpoints/` currently holds 21 numbered checkpoint files, not 3. Those files carry timestamps a few minutes older than the last edit to `configs/training.json` and `src/training/checkpoint.py`, so they were produced by a run made before the current settings and pruning code were saved. Chapter 8 covers the pruning code that `keep_last_checkpoints` feeds.

#### `configs/inspection.json`

**Why this file exists.** Inspection decides whether each acquired file is safe and well-formed enough to continue. The rules it applies (size limits, which file types are allowed) are a policy, and a policy should be readable and changeable without editing code.

**What enters / what leaves.** `load_inspection_config()` in `src/corpus_factory/inspection/config.py` reads the file and passes the result to `validate_inspection_config()` in the same file. Validation is strict: every key below must be present with the right type, and **any key not in the list is an error**. So, unlike `training.json`, you cannot add a note or a spare key to this file.

**How it connects.** `scripts/inspection.py` loads it (and accepts `--policy <file>` to use a different file). `src/corpus_factory/inspection/inspector.py` loads it by default when no policy is passed in. `tests/test_inspection.py` loads it too. The inspection chapter explains the checking code; the tables below say which file reads each key.

**The file**

```json
{
  "max_file_size_bytes": 2147483648,
  "max_batch_size_bytes": 107374182400,
  "max_files_per_batch": 100000,
  "max_line_characters": 1000000,
  "max_manifest_bytes": 67108864,
  "max_structured_bytes": 16777216,
  "max_xml_depth": 256,
  "max_archive_files": 10000,
  "max_archive_member_bytes": 104857600,
  "max_uncompressed_bytes": 5368709120,
  "max_compression_ratio": 200,
```

File names below are inside `src/corpus_factory/inspection/`. Sizes are in bytes; 1 MiB is 1,048,576 bytes and 1 GiB is 1,073,741,824 bytes.

| Key | Value now | Unit | Meaning | Read in |
|---|---|---|---|---|
| `max_file_size_bytes` | `2147483648` | bytes (2 GiB) | A single file larger than this is rejected. | `checks.py` |
| `max_batch_size_bytes` | `107374182400` | bytes (100 GiB) | A byte budget for one batch. Each file that is read uses some of it; a file larger than what remains is rejected. | `inspector.py` |
| `max_files_per_batch` | `100000` | files | Files beyond this position in a batch's manifest are rejected. | `inspector.py` |
| `max_line_characters` | `1000000` | characters | A text file whose longest line exceeds this is quarantined. Also used as a size limit on a single unparsed HTML fragment. | `checks.py`, `deep_inspection.py` |
| `max_manifest_bytes` | `67108864` | bytes (64 MiB) | The largest `source.json` inspection will read. | `checks.py` |
| `max_structured_bytes` | `16777216` | bytes (16 MiB) | The largest JSON or XML content it will parse to check structure; also a limit on the size of a ZIP file's internal directory. | `checks.py`, `deep_inspection.py` |
| `max_xml_depth` | `256` | nesting levels | XML nested deeper than this fails. | `deep_inspection.py` |
| `max_archive_files` | `10000` | entries | The most entries allowed inside a ZIP-based file (`.docx`, `.xlsx`, `.epub`, … are ZIP archives inside). | `deep_inspection.py` |
| `max_archive_member_bytes` | `104857600` | bytes (100 MiB) | The largest single entry inside such an archive, uncompressed. | `deep_inspection.py` |
| `max_uncompressed_bytes` | `5368709120` | bytes (5 GiB) | The largest total size of all entries, uncompressed. | `deep_inspection.py` |
| `max_compression_ratio` | `200` | ratio (uncompressed ÷ compressed) | An entry that expands more than 200 times is treated as unsafe. This guards against a tiny file built to expand into gigabytes. May be an integer or a decimal. | `deep_inspection.py` |

```json
  "allowed_extensions": [
    ".txt",
    ".text",
    ".md",
    ".markdown",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".ndjson",
    ".html",
    ".htm",
    ".xml",
    ".yaml",
    ".yml",
    ".log",
    ".pdf",
    ".doc",
    ".rtf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".odt",
    ".ods",
    ".epub"
  ],
  "blocked_extensions": [
    ".exe",
    ".dll",
    ".bat",
    ".cmd",
    ".com",
    ".msi",
    ".ps1",
    ".sh",
    ".scr",
    ".docm",
    ".xlsm",
    ".pptm",
    ".jar"
  ],
```

| Key | Value now | Meaning | Read in |
|---|---|---|---|
| `allowed_extensions` | 24 extensions | File-name endings inspection is willing to consider. A file with any other ending is handled according to `unknown_file_policy`. Being on this list means "may be inspected"; it does not mean a later stage can read it. Extraction (`src/corpus_factory/extraction/extractor.py`) currently accepts only `.txt` and `.md`. | `checks.py` |
| `blocked_extensions` | 13 extensions | Endings that are rejected outright: programs, scripts, and Office files that carry macros. Also applied to entries inside archives. | `checks.py`, `deep_inspection.py` |

The validator requires each entry to be a dot followed by lowercase letters or digits, no duplicates, and no extension on both lists.

```json
  "expected_mime_types": {
    ".txt": [
      "text/plain"
    ],
    ".text": [
      "text/plain"
    ],
    ".md": [
      "text/plain"
    ],
    ".markdown": [
      "text/plain"
    ],
    ".csv": [
      "text/plain"
    ],
    ".tsv": [
      "text/plain"
    ],
    ".json": [
      "text/plain",
      "application/json"
    ],
    ".jsonl": [
      "text/plain",
      "application/json",
      "application/x-ndjson"
    ],
    ".ndjson": [
      "text/plain",
      "application/json",
      "application/x-ndjson"
    ],
    ".html": [
      "text/html"
    ],
    ".htm": [
      "text/html"
    ],
    ".xml": [
      "application/xml",
      "text/xml"
    ],
    ".yaml": [
      "text/plain"
    ],
    ".yml": [
      "text/plain"
    ],
    ".log": [
      "text/plain"
    ],
    ".pdf": [
      "application/pdf"
    ],
    ".doc": [
      "application/x-ole-storage",
      "application/msword"
    ],
    ".rtf": [
      "application/rtf",
      "text/rtf"
    ],
    ".docx": [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ],
    ".xlsx": [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ],
    ".pptx": [
      "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ],
    ".odt": [
      "application/vnd.oasis.opendocument.text"
    ],
    ".ods": [
      "application/vnd.oasis.opendocument.spreadsheet"
    ],
    ".epub": [
      "application/epub+zip"
    ]
  },
  "blocked_mime_types": [
    "application/x-dosexec",
    "application/x-elf",
    "application/x-mach-binary",
    "text/x-shellscript",
    "application/javascript",
    "application/x-executable",
    "application/x-sharedlib",
    "application/vnd.microsoft.portable-executable"
  ],
```

A MIME type is a standard label for what a file's content is, such as `text/plain` or `application/pdf`. Inspection works it out from the file's bytes, not from its name. That is the point of these two keys: a file's name can lie, its content cannot.

| Key | Value now | Meaning | Read in |
|---|---|---|---|
| `expected_mime_types` | one list per allowed extension (24 entries) | For each extension, the content types that are consistent with it. If a file named `.pdf` turns out to contain plain text, the detected type is not in the list for `.pdf` and the file is quarantined. The validator requires this object to have exactly the same keys as `allowed_extensions`. | `checks.py` |
| `blocked_mime_types` | 8 types | Content types that are rejected whatever the file is called: Windows, Linux and macOS executables, shell scripts, JavaScript. | `checks.py` |

```json
  "unknown_file_policy": "quarantine",
  "require_malware_scan": false,
  "require_deep_container_inspection": false,
  "malware_chunk_size": 128,
  "max_malware_chunk_bytes": 2147483648,
  "malware_timeout_seconds": 120,
  "pdf_timeout_seconds": 30
}
```

| Key | Value now | Unit | Meaning | Read in |
|---|---|---|---|---|
| `unknown_file_policy` | `"quarantine"` | one of `"quarantine"`, `"reject"` | What to do with a file whose extension is not on the allowed list. | `checks.py` |
| `require_malware_scan` | `false` | yes/no | If true, a file that could not be confirmed clean by a virus scanner is quarantined. With `false`, a missing scanner does not hold files back; a file the scanner reports as infected is rejected either way. | `checks.py` |
| `require_deep_container_inspection` | `false` | yes/no | If true, a PDF fails when the external `pdfinfo` program is not installed to validate it. With `false`, the missing validator is only noted. | `deep_inspection.py` |
| `malware_chunk_size` | `128` | files | How many files are handed to the virus scanner per invocation. Despite the word "size", this is a count of files. | `checks.py` |
| `max_malware_chunk_bytes` | `2147483648` | bytes (2 GiB) | The largest total size of one such group. The validator requires it to be at least `max_file_size_bytes`, so the biggest allowed file always fits in a group. | `checks.py` |
| `malware_timeout_seconds` | `120` | seconds | How long one scanner invocation may run. | `checks.py` |
| `pdf_timeout_seconds` | `30` | seconds | How long `pdfinfo` may run on one PDF. | `deep_inspection.py` |

All 22 keys are read by the inspection code, and all 22 are checked by the validator. No key in either config file is unused.

#### What I should understand before moving on

- The project has two halves: `src/corpus_factory/` + `src/dataset/` produce text; the other `src/` packages produce a tokenizer, a model and an API. `storage/` holds data, `artifacts/` holds model outputs.
- Code under `src/` is a library. You run things through `scripts/`, always as `python -m scripts.<name>` from the project directory, because that is what puts the project directory on Python's import path.
- `paths.py` is the single place where locations are defined. `Path(__file__).resolve().parent` anchors them to the project's real location on disk.
- A stage's output folder is the next stage's input folder. `paths.py` is how they agree on its name.
- `configs/training.json` is loaded loosely (any object is accepted); `configs/inspection.json` is validated strictly (unknown keys are errors).
- `epochs` is a total to reach, not an amount to add.
- Git tracks the sample uploads and the code, and ignores every generated file under `storage/` and `artifacts/`.
- Some things exist but do nothing: `config.py`, `LOGS_DIR`, `EVALUATIONS_DIR`, and six leftover folders under `src/`.

#### Self-test

1. You open a terminal in `jsm_0.1/scripts/` and run `python acquisition.py`. What error do you get, on which line, and why?
2. Suppose you move the whole `jsm_0.1` folder to another disk. Which lines of `paths.py` need editing?
3. `scripts/cleaning.py` writes to `PROCESSED_DIR / "cleaned"` and `scripts/normalization.py` reads from `PROCESSED_DIR / "cleaned"`. What would happen if one of them had a typo in `"cleaned"`, and why does `paths.py` not protect against that particular mistake?
4. You trained to 21 epochs with `"resume": true`. You want 10 more epochs of training on the same model. What do you change in `training.json`?
5. You add `"note": "relaxed limits for testing"` to both config files. What happens the next time you run training, and the next time you run inspection?
6. A file called `report.pdf` actually contains plain text. Which two keys in `inspection.json` are involved in catching it, and what is the outcome?
7. You delete the whole `artifacts/` folder and run `git status`. Git shows a few deleted files. Which ones, and why only those?
8. You want to copy the trained model to another machine to generate text there. Which of `storage/` and `artifacts/` do you need, and which specific files?

<details><summary>Answers</summary>

1. `ModuleNotFoundError: No module named 'paths'`, on the first line, `from paths import UPLOADS_DIR, BATCHES_DIR`. Run this way, Python puts the script's own folder (`scripts/`) on the import path, and `paths.py` is one level up. `python -m scripts.acquisition` from the project directory puts the project directory on the path instead.
2. None. `PROJECT_DIR` is computed from `__file__`, the location of `paths.py` itself, and everything else is built from `PROJECT_DIR`.
3. The reader would look in a folder that does not exist or is empty and would find no work, while the writer's output sat unused in another folder. `paths.py` defines `PROCESSED_DIR` but not the four sub-folders; each script types the sub-folder name itself, so that part of the agreement is not centralised.
4. Set `"epochs": 31`. The value is the epoch number to stop at. Leaving it at 21 would train nothing; setting it to 10 would also train nothing, because the loop runs from epoch 22 up to the target.
5. Training runs normally: the loader only checks that the file is a JSON object, and the extra key is simply carried into the run record and checkpoints. Inspection stops with an error about unknown keys, because its validator rejects any key it does not know.
6. `allowed_extensions` lets `.pdf` through to content checks; `expected_mime_types` says a `.pdf` must have content type `application/pdf`. The detected type is `text/plain`, which is not in that list, so the file is quarantined. (`blocked_mime_types` is not involved: plain text is not a blocked type.)
7. The `.gitkeep` files in `artifacts/checkpoints/`, `artifacts/evaluations/`, `artifacts/logs/` and `artifacts/tokenizer/`. They are the only files under `artifacts/` that git tracks; everything else matches the ignore rule `jsm_0.1/artifacts/**`, so git never knew about it.
8. Only `artifacts/`: `artifacts/tokenizer/tokenizer.json` and a checkpoint such as `artifacts/checkpoints/tiny_model.pt` (plus the code). `storage/` is the data the model was built from and is not needed to run it.

</details>

## 4. The corpus factory

| | |
|---|---|
| **INPUT** | Files of any kind placed in `storage/uploads/`. |
| **PROCESS** | Six stages, each a separate script: acquisition, inspection, provenance, ingestion, extraction, preprocessing (cleaning, normalization, filtering, deduplication). |
| **OUTPUT** | Plain text documents in `storage/processed/deduplicated/`, ready for dataset building (chapter 5). |
| **WHY IT EXISTS** | A model learns whatever text it is given. The factory controls, and records, exactly what that text is and where it came from. |

A language model has no judgement about its training data. If a file is corrupt, the model learns the corruption. If a file is there twice, the model sees it twice and leans towards it. If a file is something you had no right to use, that is now inside the weights and cannot be taken out. And if you cannot say which files a model was trained on, you cannot repeat the training or explain its behaviour. Reading files straight from an uploads folder into a training loop gives you none of these protections.

So the factory moves data through stages, and each stage answers one question:

| # | Stage | Question it answers | Writes to |
|---|---|---|---|
| 1 | Acquisition | What exact bytes were received, from which source, and when? | `storage/incoming/batches/<batch_id>/` |
| 2 | Inspection | Is each file safe and well-formed enough to continue? | `storage/catalog/inspections/<inspection_id>/`, `storage/quarantine/` |
| 3 | Provenance | Is this batch allowed to be used for training? (A person decides.) | `storage/catalog/provenance/<decision_id>/` |
| 4 | Ingestion | Copy the accepted files of an approved batch into trusted storage. | `storage/raw/<batch_id>/` |
| 5 | Extraction | Turn each file into plain text. | `storage/extracted/<batch_id>/` |
| 6 | Preprocessing | Clean, normalize, filter, deduplicate the text. | `storage/processed/cleaned/`, `normalized/`, `filtered/`, `deduplicated/` (each with `<batch_id>/` inside) |

Three ideas run through all of them.

**Stages never edit their input.** Each stage reads one folder and writes a different one. If a later stage has a bug, you fix it and re-run it; the earlier output is still there, untouched.

**The batch id.** Acquisition groups the files from one source into a **batch** and gives it a name such as `wikipedia-ar-20261004T124557Z-4ffa41ee`: the source, the time, and a random suffix. That name becomes a folder under `storage/incoming/batches/`, and the same name is used as the folder under `storage/raw/`, `storage/extracted/` and each `storage/processed/<stage>/`. So for any piece of text late in the pipeline, the folder it sits in tells you which acquisition it came from, and that acquisition's `source.json` tells you the original file names, sizes and hashes.

**Gates.** Stages 2 and 3 do not transform anything. They decide what may go on. Inspection gives a decision for each file; provenance gives a decision for each batch. Ingestion (`scripts/ingestion.py`) copies only the files inspection accepted, and only from batches whose training rights were allowed. Everything else stays in `storage/incoming/batches/` and goes no further.

### 4.1 Acquisition

| | |
|---|---|
| **INPUT** | `storage/uploads/`: sub-folders (one per source, each optionally with an `origin.json`) and loose files. Also the existing `storage/incoming/batches/`, to see what was acquired before. |
| **PROCESS** | Group files by source. Skip a source whose exact files were already acquired. Otherwise create a new batch folder, copy each file into it while computing its SHA-256 hash and size, write a manifest describing the batch, and write the manifest's own hash beside it. |
| **OUTPUT** | `storage/incoming/batches/<batch_id>/` containing `objects/` (the copies), `source.json` (the manifest) and `source.json.sha256` (its checksum). |
| **WHY IT EXISTS** | To take a fixed, recorded copy of what was received before anything else looks at it. Every later stage can then prove it is working on the same bytes. |

The stage is driven by `scripts/acquisition.py` (chapter 12). It calls the four files below in this order: `read_uploads` (intake) to list the sources; `existing_fingerprints` (discovery) once, to learn what is already acquired; then for each source `sha256_file` (hashing) on every file to decide whether it is new, and `acquire_batch` (batch) if it is.

Acquisition does not open files to understand them. It does not check their type, extract text, or judge quality. It copies bytes and writes down facts about them.

#### `src/corpus_factory/acquisition/intake.py`

**Why this file exists.** Before copying anything, the stage needs a plain list: which sources are there, which files belong to each, and what each source says about itself. This file turns the `uploads` folder into that list.

**What enters / what leaves.** `read_uploads(root)` takes the uploads directory as a `Path`. It reads directory listings and any `origin.json` files. It returns a list of `IntakeSource` objects. It writes nothing and does not read the content of any data file.

**How it connects.** Called by `scripts/acquisition.py` with `UPLOADS_DIR`. Each `IntakeSource` it returns is later passed to `acquire_batch` in `batch.py`, which also imports the `IntakeSource` class for its type hints.

**The code, section by section**

```python
import json
from dataclasses import dataclass
from pathlib import Path


ORIGIN_FILE = "origin.json"
UNATTRIBUTED = "unattributed"
```

`json` is the standard-library module that converts between JSON text and Python values; it is needed to read `origin.json`. `dataclass` and `Path` are in the primer (1.5).

Two names are fixed here as constants so they are spelled once: the file name that describes a source, and the source name given to files that sit loose in `uploads/` with no folder.

```python
@dataclass(frozen=True)
class IntakeSource:
    name: str
    files: tuple[Path, ...]
    origin: dict
```

One source waiting to be acquired.

| Field | Holds |
|---|---|
| `name` | The folder name under `uploads/`, or `"unattributed"`. |
| `files` | The data files of that source, as a tuple of `Path`. A tuple is like a list that cannot be changed after it is made. |
| `origin` | The contents of the folder's `origin.json` as a `dict`, or an empty `dict` if there is none. |

`frozen=True` means you cannot assign to `source.name` after creating it. It does not make the `origin` dictionary itself unchangeable; it only stops the field from being pointed at a different object.

```python
def read_uploads(root: Path) -> list[IntakeSource]:
    if not root.is_dir():
        raise ValueError(f"Uploads directory not found: {root}")

    sources = []
```

If `storage/uploads/` does not exist, stop immediately with a clear message. `sources` is the list that will be returned.

```python
    # Each folder = one source
    for folder in sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ):
        origin_path = folder / ORIGIN_FILE
        origin = {}
```

`root.iterdir()` yields every entry directly inside `uploads/` (not deeper). The generator expression (primer, 1.5) keeps only entries that are folders and whose names do not start with a dot, which skips hidden folders. `sorted(...)` puts them in a fixed order.

**What Python does:** the operating system returns directory entries in no guaranteed order. `sorted` on `Path` objects orders them by path, so the loop always visits folders in the same sequence.

**What it means in the pipeline:** the same uploads always produce the same sources in the same order, on any machine. Repeatability is the whole point of this stage.

For each folder, `origin_path` is where its `origin.json` would be, and `origin` starts as an empty dictionary in case there is none.

```python
        if origin_path.is_file():
            try:
                origin = json.loads(
                    origin_path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid origin.json: {origin_path}"
                ) from error

            if not isinstance(origin, dict):
                raise ValueError(
                    f"{origin_path} must contain a JSON object"
                )
```

If the folder has an `origin.json`:

- `origin_path.read_text(encoding="utf-8")` reads the whole file as a string. `json.loads` ("load string") parses that string into Python values.
- If the text is not valid JSON, `json.loads` raises `json.JSONDecodeError`. The code catches it and raises a `ValueError` that names the file, with the original error attached (`raise ... from error`, primer 1.5).
- Valid JSON is not necessarily an object: `[1, 2]` and `"hello"` are valid JSON too. `isinstance(origin, dict)` checks that the top level is an object, because later code calls `origin.get(...)`, which only dictionaries have.

A bad `origin.json` therefore stops the whole stage before anything is copied. The stage does not guess.

The code does not check which keys are inside. The keys that later code looks for are `platform`, `source_type`, `source_url`, `license_identifier` and `attribution` (all in `batch.py`). Any others are ignored, and a missing one is replaced by a default.

```python
        files = tuple(
            sorted(
                path
                for path in folder.rglob("*")
                if path.is_file()
                and path.name != ORIGIN_FILE
                and not path.name.startswith(".")
            )
        )
```

`folder.rglob("*")` is the recursive version of `iterdir`: it yields everything inside the folder at **any depth**, so files in sub-folders of a source are included. Three conditions filter it:

- `path.is_file()`: keep files, drop directories.
- `path.name != ORIGIN_FILE`: `origin.json` describes the source; it is not data and is never copied into a batch.
- `not path.name.startswith(".")`: skip hidden files such as `.DS_Store`.

The dot check looks at the file's own name only. A normally named file inside a hidden sub-folder of a source would still be picked up.

The result is sorted and frozen into a tuple.

```python
        if files:
            sources.append(
                IntakeSource(
                    name=folder.name,
                    files=files,
                    origin=origin,
                )
            )
```

An empty tuple is false in Python, so a folder with no data files (empty, or holding only `origin.json`) produces no source and therefore no batch.

```python
    # Files directly inside uploads/
    loose_files = tuple(
        sorted(
            path
            for path in root.iterdir()
            if path.is_file()
            and path.name != ORIGIN_FILE
            and not path.name.startswith(".")
        )
    )
```

After the folders, the files sitting directly in `uploads/`. This uses `iterdir`, not `rglob`, so it only sees the top level. An `origin.json` placed directly in `uploads/` is skipped and never read.

```python
    if loose_files:
        sources.append(
            IntakeSource(
                name=UNATTRIBUTED,
                files=loose_files,
                origin={},
            )
        )

    return sources
```

All loose files together form one source named `"unattributed"` with an empty origin: nothing is known about where they came from. It is appended last, after all the folder sources.

Example. Suppose `uploads/` contains a folder `wiki/` with `origin.json` and `a.txt`, an empty folder `drafts/`, and a loose file `note.txt`. `read_uploads` returns two sources: `IntakeSource(name="wiki", files=(.../wiki/a.txt,), origin={...})` and `IntakeSource(name="unattributed", files=(.../note.txt,), origin={})`. `drafts/` is not there.

#### `src/corpus_factory/acquisition/hashing.py`

**Why this file exists.** Acquisition needs a way to say "these are exactly the same bytes" without comparing two files side by side. A hash gives every file a short fixed-size fingerprint that can be stored and compared later.

**What enters / what leaves.** `sha256_file(path, chunk_size)` takes a file path and returns a string of 64 hexadecimal characters. It reads the file and writes nothing.

**How it connects.** Called by `scripts/acquisition.py` for every file of every source, to build the fingerprint that decides whether a source was already acquired. `batch.py` imports it too but never calls it (it computes hashes with its own loop, shown below).

**SHA-256 in plain terms.** SHA-256 is a hash function: a fixed procedure that takes any amount of bytes and produces 256 bits (32 bytes). Written in hexadecimal, that is 64 characters. Three properties matter here:

- **Deterministic.** The same bytes always give the same result, on any machine.
- **Sensitive.** Changing a single bit of the input changes the result completely.
- **Practically collision-free.** Nobody knows how to find two different inputs with the same SHA-256. So "same hash" is treated as "same content".

Real output:

```
sha256(b"hello") = 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
sha256(b"hellp") = fdd7585e08c4e2afd71dcabdb4636c89d557a3f42db9e2040c8bbd1708aa4ce7
```

One letter changed, and the two results have nothing in common. A hash is not encryption: you cannot get the file back from it, and that is not its purpose. It identifies content.

It depends only on the bytes. The file's name, folder and date play no part.

**The code, section by section**

```python
import hashlib
from pathlib import Path
```

`hashlib` is the standard-library module with hash functions, including SHA-256. `Path` is used only in the type hint.

```python
def sha256_file(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    sha256 = hashlib.sha256()
```

`chunk_size` has a default of `1024 * 1024` = `1048576` bytes, which is 1 MiB. Writing it as a product makes the intent readable.

`hashlib.sha256()` creates an empty hash object. Think of it as a machine you feed bytes into; it keeps a small running state and can give you the result at any point.

```python
    with open(path, "rb") as file:
        while chunk := file.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest()
```

These four lines are the pattern this course calls **chunked reading**, and they appear again in `batch.py`.

**`"rb"`.** Open for reading in binary mode. The file is delivered as raw `bytes`, exactly as stored, with no decoding into text. A hash must be computed over the real bytes; text mode could fail on a PDF or alter line endings.

**`file.read(chunk_size)`.** Read at most `chunk_size` bytes from where the last read stopped. At the end of the file it returns the empty bytes object `b""`.

**The walrus operator `:=`.** `chunk := file.read(chunk_size)` does two things at once: it assigns the result to `chunk`, and the whole expression has that value so `while` can test it. Non-empty bytes are true; `b""` is false. The line is shorthand for:

```python
while True:
    chunk = file.read(chunk_size)
    if not chunk:
        break
    sha256.update(chunk)
```

A real run of the same pattern on 8 bytes with a chunk size of 3 gives the chunks `[b'abc', b'def', b'gh']`, then `b''`, which ends the loop.

**`sha256.update(chunk)`.** Feed these bytes into the hash. Feeding a file in pieces gives exactly the same result as feeding it all at once: updating with `b"hel"` then `b"lo"` gives the same digest as hashing `b"hello"`.

**`sha256.hexdigest()`.** Finish and return the 32-byte result as 64 hexadecimal characters.

**What Python does:** reads the file 1 MiB at a time, so memory use stays at about 1 MiB no matter how big the file is.

**What it means in the pipeline:** the uploads may contain files of many gigabytes (the inspection policy allows up to 2 GiB each). `file.read()` with no argument would load a whole file into memory. Chunked reading lets acquisition fingerprint files of any size on an ordinary machine.

#### `src/corpus_factory/acquisition/discovery.py`

**Why this file exists.** You will run acquisition many times, and the uploads folder usually still contains what it contained last time. Without a check, every run would copy everything again into a new batch. This file reads what earlier runs recorded so the script can recognise a source it has already taken.

**What enters / what leaves.** `existing_fingerprints(batches_dir)` takes the batches directory. It reads the `source.json` of every existing batch. It returns a `set` of fingerprints. It writes nothing.

**How it connects.** Called once by `scripts/acquisition.py` with `BATCHES_DIR`, before the loop over sources. The script then builds a fingerprint for each current source in the same shape and asks whether it is in the set. The `source.json` files it reads were written by `batch.py` on earlier runs.

**What a fingerprint is here.** A pair: the source's platform name, and the sorted tuple of the SHA-256 hashes of all its files. For example `("Wikipedia", ("2cf2…", "fdd7…"))`. Two acquisitions have the same fingerprint when they come from the same platform and contain exactly the same set of file contents. File names are not part of it.

**The code, section by section**

```python
import json
from pathlib import Path


def existing_fingerprints(
    batches_dir: Path,
) -> set[tuple[str, tuple[str, ...]]]:
    fingerprints = set()
```

The return type reads from the outside in: a `set` of `tuple`s, each holding a `str` (the platform) and a `tuple[str, ...]` (any number of hash strings).

A `set` is an unordered collection with no duplicates and a very fast "is this in here?" test. Members of a set must be hashable, meaning unchangeable values such as strings and tuples. That is why the hashes are stored in a tuple, not a list.

```python
    if not batches_dir.exists():
        return fingerprints
```

On the very first run there is no `storage/incoming/batches/` yet. Nothing has been acquired, so the answer is the empty set.

```python
    for batch_dir in batches_dir.iterdir():
        manifest_path = batch_dir / "source.json"

        if not manifest_path.is_file():
            continue
```

Look at every entry in the batches directory. If it has no `source.json`, skip it (`continue` jumps to the next loop iteration). That covers stray files and a batch folder that was created but never finished.

```python
        try:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            continue
```

Read and parse the manifest. `except (A, B)` catches either error type: `JSONDecodeError` if the content is not valid JSON, `OSError` if the file cannot be read. In both cases the batch is skipped silently.

Compare this with `intake.py`, which stops the program on a bad `origin.json`. The difference is deliberate in effect: a bad input file is your mistake to fix, but an unreadable old manifest only means "I cannot prove this was acquired before", and the safe consequence of that is acquiring again.

```python
        source_name = manifest.get("source", {}).get("platform")
```

The manifest has a `"source"` object with a `"platform"` field inside (you will see it written in `batch.py`). `manifest.get("source", {})` returns that object, or an empty dictionary if the key is missing, so the second `.get("platform")` always has a dictionary to work on and returns `None` when there is no platform. Chaining `.get` with a `{}` default is a common way to reach into nested data without an error.

The variable is called `source_name` but holds the platform, which is the folder name only when `origin.json` did not declare a `platform`.

```python
        hashes = tuple(
            sorted(
                artifact["sha256"]
                for artifact in manifest.get("artifacts", [])
                if "sha256" in artifact
            )
        )
```

`"artifacts"` in the manifest is a list with one entry per file. This collects the `sha256` value from each entry that has one, sorts them, and makes a tuple.

**What Python does:** sorting strings puts the hashes in alphabetical order, whatever order the files were in.

**What it means in the pipeline:** the fingerprint must not depend on file order or file names. If you rename `a.txt` to `b.txt`, the files sort differently, but the set of hashes is the same, so the sorted tuple is the same. Sorting turns "the same collection of contents" into "an equal tuple".

```python
        if source_name and hashes:
            fingerprints.add(
                (
                    source_name,
                    hashes,
                )
            )

    return fingerprints
```

Only a manifest that has both a platform and at least one hash contributes a fingerprint. The inner parentheses build the pair; `add` puts it in the set.

#### `src/corpus_factory/acquisition/batch.py`

**Why this file exists.** This is the file that actually acquires. It creates the batch folder, copies each file into it, records what it copied in a manifest, and seals the manifest with a checksum.

**What enters / what leaves.** The entry point is `acquire_batch(source)`, which takes one `IntakeSource` and returns the `Path` of the new batch folder. On the way it reads every file of the source and writes:

```
storage/incoming/batches/<batch_id>/
    objects/
        00000001-<original file name>
        00000002-<original file name>
        ...
    source.json
    source.json.sha256
```

**How it connects.** `scripts/acquisition.py` calls `acquire_batch` for each source that `discovery.py` did not recognise. The next stage, inspection, reads `source.json` and the files in `objects/`, and re-computes each hash to check nothing changed.

**The code, section by section**

```python
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import secrets
from src.corpus_factory.acquisition.hashing import sha256_file
from paths import BATCHES_DIR
from src.corpus_factory.acquisition.intake import IntakeSource
```

| Import | What it is | Why this file needs it |
|---|---|---|
| `datetime`, `timezone` | Standard-library date and time types. | Timestamps in the batch id and manifest. |
| `Path` | Primer 1.5. | Building locations. |
| `hashlib` | Hash functions. | SHA-256 while copying, and for the manifest checksum. |
| `json` | JSON reading/writing. | Writing `source.json`. |
| `re` | Regular expressions: patterns for matching text. | Cleaning the source name. |
| `secrets` | Random values of cryptographic quality. | The random suffix of the batch id. |
| `sha256_file` | The function from `hashing.py`. | **Not used.** It is imported but never called in this file. |
| `BATCHES_DIR` | `storage/incoming/batches` from `paths.py`. | Where batches are created. |
| `IntakeSource` | The dataclass from `intake.py`. | Type hints, and its fields are read. |

```python
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
```

Returns the current time as text. `datetime.now(timezone.utc)` is the current moment in UTC, the world's reference time with no local offset or daylight saving. `.isoformat()` writes it in the standard ISO 8601 layout, ending in `+00:00`. `.replace("+00:00", "Z")` swaps that ending for `Z`, the usual short way to write "UTC". The result is 27 characters and looks like `2026-01-15T09:30:00.123456Z`: date, `T`, time with microseconds, `Z`.

Using UTC means timestamps from different machines and seasons can be compared directly.

```python
def _safe_source_name(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_-]+", "-", name)

    return name.strip("-") or "unattributed"
```

A source name comes from a folder name, which can contain spaces, capitals or any character. The batch id becomes a folder name itself, so this function reduces the name to a safe form. The leading underscore in `_safe_source_name` is a convention meaning "internal helper, not meant to be called from other files".

- `name.strip().lower()`: remove spaces at both ends, make lowercase.
- `re.sub(pattern, "-", name)`: replace every match of the pattern with a hyphen. The pattern `[^a-z0-9_-]+` reads: `[...]` is "one character from this set"; a leading `^` inside the brackets inverts it to "any character **not** in this set"; the set is lowercase `a`–`z`, digits, underscore and hyphen; `+` means "one or more in a row". So each run of other characters becomes a single `-`. The `r` before the string makes it a raw string, where backslashes are left alone; it is a habit for patterns.
- `name.strip("-")`: remove hyphens at both ends.
- `... or "unattributed"`: `or` returns its left side if that is non-empty, otherwise its right side. If nothing survives, use `"unattributed"`.

Real results:

| Input | Output |
|---|---|
| `"Riyadh Municipality"` | `"riyadh-municipality"` |
| `"  Wikipedia AR!! "` | `"wikipedia-ar"` |
| `"a__b--c"` | `"a__b--c"` |
| `"مرحبا"` | `"unattributed"` |

The last row matters: only ASCII letters are kept, so a folder named entirely in Arabic gets a batch id beginning with `unattributed`, the same prefix as the loose-files source. This affects only the folder name of the batch. The manifest still records the real folder name (in `source.platform` and in each file's `origin_folder`).

```python
def create_batch(source_name: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = secrets.token_hex(4)

    safe_name = _safe_source_name(source_name)

    batch_id = f"{safe_name}-{stamp}-{suffix}"
```

Builds the batch id from three parts.

- `stamp`: the UTC time in a compact layout. `strftime` formats a time using codes: `%Y` four-digit year, `%m` month, `%d` day, `%H` hour, `%M` minute, `%S` second; the `T` and `Z` are literal. Example: `20261004T124557Z`. No colons, because colons are not allowed in file names on some systems. Resolution is one second.
- `suffix`: `secrets.token_hex(4)` returns 4 random bytes written as 8 hexadecimal characters, such as `4ffa41ee`.
- `safe_name`: the cleaned source name.

An f-string joins them: `wikipedia-ar-20261004T124557Z-4ffa41ee`.

**What Python does:** produces a name that sorts by source and then by time, and is different on every call.

**What it means in the pipeline:** this is the batch id from the chapter introduction. The time makes it readable and ordered. The random suffix is there because two batches for the same source could be created within the same second, and they must not share a name.

```python
    batch_dir = BATCHES_DIR / batch_id
    objects_dir = batch_dir / "objects"

    objects_dir.mkdir(parents=True, exist_ok=False)

    return batch_dir
```

`mkdir` creates the directory `objects`. `parents=True` also creates every missing folder above it, so this one call creates `storage/incoming/`, `batches/`, the batch folder and `objects/` as needed.

`exist_ok=False` means: if `objects/` already exists, raise `FileExistsError`. (It is also the default; writing it out states the intent.)

**What Python does:** refuses to proceed if the target folder is already there.

**What it means in the pipeline:** a batch is always a new, empty folder. Acquisition can never add files to, or mix files into, a batch that already exists.

```python
def acquire_file(
    source_file: Path,
    batch_dir: Path,
    sequence: int,
    source: IntakeSource,
) -> dict:
    destination = (
        batch_dir
        / "objects"
        / f"{sequence:08d}-{source_file.name}"
    )
```

Copies one file into the batch and returns a dictionary of facts about it.

| Parameter | Meaning |
|---|---|
| `source_file` | The file in `uploads/` to copy. |
| `batch_dir` | The batch folder from `create_batch`. |
| `sequence` | The file's position in the batch: 1, 2, 3, … |
| `source` | The `IntakeSource` it belongs to. |

The stored name is the sequence number padded to 8 digits, a hyphen, and the original file name: `{sequence:08d}` turns `1` into `00000001`. `source_file.name` is only the last part of the path, so the sub-folder a file came from is not kept. The sequence prefix is what keeps names unique: two files both called `notes.txt` from different sub-folders of one source become `00000001-notes.txt` and `00000002-notes.txt`.

```python
    sha256 = hashlib.sha256()
    size_bytes = 0

    with source_file.open("rb") as src, destination.open("xb") as dst:
        while chunk := src.read(1024 * 1024):
            dst.write(chunk)
            sha256.update(chunk)
            size_bytes += len(chunk)
```

This is the centre of the stage.

A fresh hash object and a byte counter are prepared. Then one `with` statement opens two files, separated by a comma; both are closed when the block ends. `source_file.open("rb")` is the same as `open(source_file, "rb")`.

**Exclusive-create mode.** The destination is opened with `"xb"`. `b` is binary. `x` means **create the file, and fail if it already exists**. Compare with `"w"`, which silently empties an existing file and writes over it. If the destination exists, `"x"` raises `FileExistsError` ("File exists") and nothing is written.

**The loop.** The same chunked read and walrus as in `hashing.py`. For each chunk of up to 1 MiB, three things happen to the **same bytes in memory**:

1. `dst.write(chunk)`: written to the copy.
2. `sha256.update(chunk)`: fed into the hash.
3. `size_bytes += len(chunk)`: counted.

**What Python does:** reads the source once and, in a single pass, produces the copy, its hash, and its size.

**What it means in the pipeline:** the hash that goes into the manifest is the hash of exactly the bytes that were written into the batch. If the code copied first and hashed the source file afterwards, the source could change in between and the manifest would describe something other than what is stored. Doing all three on the same chunk closes that gap. And `"xb"` makes the "never modify in place" rule real at the file level: this code cannot overwrite an object that is already in a batch.

An empty source file makes the loop run zero times: an empty copy is created, `size_bytes` stays `0`, and the hash is the SHA-256 of nothing, which is always `e3b0c442…7852b855`.

```python
    return {
        "artifact_id": f"artifact_{sequence:08d}",
        "original_filename": source_file.name,
        "sha256": sha256.hexdigest(),
        "size_bytes": size_bytes,
        "source_metadata": {
            "origin_folder": source.name,
        },
        "source_url": source.origin.get("source_url"),
        "stored_relative_path": (
            Path("objects") / destination.name
        ).as_posix(),
    }
```

The record for this file. From here on the pipeline calls a stored file an **artifact**.

| Key | Value |
|---|---|
| `artifact_id` | `artifact_00000001`, … An id that is unique within the batch. |
| `original_filename` | The name the file had in `uploads/` (without any sub-folder). |
| `sha256` | The 64-character hash of the copied bytes. |
| `size_bytes` | How many bytes were copied. |
| `source_metadata.origin_folder` | The source's folder name, or `unattributed`. |
| `source_url` | The `source_url` from `origin.json`, or `None` if not declared. The same value is repeated for every file of the source. |
| `stored_relative_path` | `objects/00000001-notes.txt`: where the copy is, **relative to the batch folder**. |

`.as_posix()` writes the path with forward slashes on every operating system. Storing a relative path with a fixed separator means the manifest stays correct if the batch folder, or the whole project, is moved or read on another system.

```python
def write_source_manifest(
    batch_dir: Path,
    source: IntakeSource,
    files: list[dict],
    collected_at: str,
) -> Path:

    total_bytes = sum(file["size_bytes"] for file in files)
```

A **manifest** is a file that lists and describes the contents of a package. Here it is `source.json`: the batch's own description of itself. Every later stage reads the manifest instead of guessing from folder contents.

`files` is the list of dictionaries returned by `acquire_file`. `collected_at` is a timestamp taken by the caller before copying began. `total_bytes` adds up the sizes with a generator expression (primer 1.5).

```python
    manifest = {
        "schema_version": "1.0.0",
        "record_type": "incoming_source_batch",

        "batch_id": batch_dir.name,

        "collected_at": collected_at,
        "created_at": utc_now(),

        "connector": {
            "contract_version": "0.1.0",
            "name": "local-uploads",
            "version": "1.0.0",
        },
```

The manifest is built as one Python dictionary.

| Key | Value | Meaning |
|---|---|---|
| `schema_version` | `"1.0.0"` | The version of this manifest layout. A reader can check it before trusting the field names. |
| `record_type` | `"incoming_source_batch"` | What kind of record this is. |
| `batch_id` | the batch folder's name | The id from `create_batch`. |
| `collected_at` | time before copying started | Two timestamps bracket the work: … |
| `created_at` | time now, as the manifest is built | … this one is taken after all files are copied. |
| `connector` | fixed values | A connector is the thing that fetched the data. There is only one, `local-uploads`: files placed by hand in a local folder. The three values are constants written here; nothing else in the acquisition code reads them. |

```python
        "source": {
            "platform": source.origin.get(
                "platform",
                source.name,
            ),
            "source_type": source.origin.get(
                "source_type",
                "undeclared_local_files",
            ),
            "source_url": source.origin.get("source_url"),
        },
```

Where the data came from, taken from `origin.json` with fallbacks.

| Key | From `origin.json` | If not declared |
|---|---|---|
| `platform` | `platform` | the folder name (`source.name`) |
| `source_type` | `source_type` | `"undeclared_local_files"` |
| `source_url` | `source_url` | `None`, written to JSON as `null` |

`platform` is the value `discovery.py` reads back as the first half of a fingerprint. `scripts/acquisition.py` computes it with the identical expression, `source.origin.get("platform", source.name)`, so the value compared before acquiring matches the value stored after.

```python
        "license": {
            "identifier": source.origin.get(
                "license_identifier",
                "unknown",
            ),
            "attribution": source.origin.get("attribution"),
            "status": "review_required",
            "training_use": "review_required",
        },
```

What is claimed about rights. `identifier` and `attribution` are copied from `origin.json` (defaults `"unknown"` and `None`). They are claims made by whoever wrote `origin.json`; acquisition does not verify them.

`status` and `training_use` are always `"review_required"`, whatever `origin.json` says. Acquisition has no way to grant permission to train on a batch. That decision belongs to the provenance stage and a human reviewer.

```python
        "immutability": {
            "append_only": True,
            "never_modify_in_place": True,
        },

        "artifacts": files,

        "summary": {
            "artifacts": len(files),
            "bytes": total_bytes,
        },

        "next_stage": "inspection",
    }
```

| Key | Meaning |
|---|---|
| `immutability` | A stated policy: new batches may be added, existing ones are not to be changed. These are two fixed `True` values written into the file. They are a declaration, not a mechanism. What actually protects a batch is the exclusive-create modes in this file and the checksum below; nothing sets the files read-only. |
| `artifacts` | The per-file records from `acquire_file`, in sequence order. |
| `summary` | The number of files and their total size, for a quick check without reading the list. |
| `next_stage` | `"inspection"`. A label saying what should process this batch next. |

```python
    manifest_path = batch_dir / "source.json"

    with open(manifest_path, "x", encoding="utf-8") as file:
        json.dump(
            manifest,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return manifest_path
```

Writes the dictionary to `source.json`.

- Mode `"x"` again: exclusive create, this time in text mode. A batch gets exactly one manifest; a second attempt to write one fails.
- `json.dump(obj, file)` converts the dictionary to JSON text and writes it to the open file. (`json.dumps` with an `s` returns a string instead.) Python `True` becomes `true`, `None` becomes `null`.
- `ensure_ascii=False` writes non-ASCII characters as themselves. With the default, `"مرحبا"` would be written as `"مرحبا"`; with `False` it is written as `"مرحبا"`. This keeps Arabic file names and platform names readable in the manifest. It is the reason for `encoding="utf-8"` on the `open`.
- `indent=2` puts each key on its own line with two-space indentation, so a person can read the file.

```python
def write_manifest_checksum(manifest_path: Path) -> Path:
    sha256 = hashlib.sha256()

    with open(manifest_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)
```

A **checksum** is a hash stored next to the thing it was computed from, so that anyone can later re-compute the hash and see whether the thing changed.

This reads the manifest that was just written, in binary, and hashes it with the same chunked loop as `hashing.py` (the loop is written out again here instead of calling `sha256_file`). It hashes the file as it is on disk, not the dictionary in memory, so the checksum covers the exact bytes a later reader will see.

```python
    checksum_path = manifest_path.with_suffix(
        manifest_path.suffix + ".sha256"
    )

    with open(checksum_path, "x", encoding="utf-8") as file:
        file.write(sha256.hexdigest())

    return checksum_path
```

`with_suffix` replaces a path's extension. The manifest's suffix is `.json`, so the new suffix is `.json.sha256` and the result is `source.json.sha256` in the same folder.

The file is created exclusively and contains only the 64 hexadecimal characters: no file name and no newline. It is exactly 64 bytes.

**What Python does:** stores the manifest's hash in a small sibling file.

**What it means in the pipeline:** this builds a chain of trust. The manifest holds the hash of every object, so the manifest vouches for the objects. The checksum file holds the hash of the manifest, so it vouches for the manifest. If anyone edits `source.json`, even to change one hash inside it, the manifest no longer matches `source.json.sha256`. Inspection performs both checks: it compares `source.json` against `source.json.sha256`, then re-hashes every object and compares it with the manifest (`src/corpus_factory/inspection/checks.py`). The limit of this protection: both files sit in the same folder, so it detects accidental damage and careless edits, not someone who deliberately rewrites both.

```python
def acquire_batch(source: IntakeSource) -> Path:
    collected_at = utc_now()

    batch_dir = create_batch(source.name)

    files_metadata = []
```

The function the script calls. It ties the others together for one source. It notes the start time, creates the empty batch folder, and prepares a list for the per-file records.

```python
    for sequence, source_file in enumerate(
        source.files,
        start=1,
    ):
        metadata = acquire_file(
            source_file=source_file,
            batch_dir=batch_dir,
            sequence=sequence,
            source=source,
        )

        files_metadata.append(metadata)
```

`enumerate(items, start=1)` yields pairs `(1, first)`, `(2, second)`, …, so the loop has both the position and the file. `source.files` was sorted in `intake.py`, so sequence numbers follow sorted path order. Each file is copied and its record collected.

```python
    manifest_path = write_source_manifest(
        batch_dir=batch_dir,
        source=source,
        files=files_metadata,
        collected_at=collected_at,
    )

    write_manifest_checksum(manifest_path)

    return batch_dir
```

After all files are copied, write the manifest, then its checksum, and return the batch folder.

**The order of writes, and what an unfinished batch looks like.** The order is: folder, objects, `source.json`, `source.json.sha256`. The manifest is written only after every copy has succeeded, so a manifest never lists a file that is not there. If the process stops part-way (disk full, a file that cannot be read, Ctrl-C), the batch folder is left behind with some objects and no `source.json`. Nothing here removes it. `discovery.py` ignores a folder without a manifest, so the next run does not treat the source as acquired and acquires it again into a new batch.

**Write-then-replace is not used here.** A later technique you will meet (from 4.2 on, and for checkpoints in chapter 8) is to write a file under a temporary name and then rename it over the real name, so readers only ever see a complete file. Acquisition does not need to replace anything: every file it writes is new, inside a folder that did not exist a moment before. It uses exclusive create instead, which gives the opposite guarantee: not "the old version is swapped for a complete new one" but "there is never an old version to swap".

**How the pieces behave together.** Because the fingerprint covers a whole source, a source is all-or-nothing:

| You do this in `uploads/` | Next run of acquisition |
|---|---|
| Nothing | Every source is skipped. |
| Rename a file, content unchanged | Skipped: the set of hashes is the same. |
| Edit one file in a folder of ten | A new batch with all ten files. The old batch stays as it was. |
| Add an eleventh file | A new batch with all eleven. |
| Change `platform` in `origin.json` | A new batch: the platform is half of the fingerprint. |
| Change `attribution` or `license_identifier` in `origin.json` | Skipped: those are not part of the fingerprint, so the new values are not recorded anywhere. |

Each file of a new source is read twice: once by `sha256_file` in the script to decide, and once by `acquire_file` to copy. The hash recorded in the manifest is the one from the copy.

**Where the README and the code differ.** `src/corpus_factory/acquisition/README.md` describes intent well, with these differences from what the code does:

- Its example batch lists `00000001-report.pdf` then `00000002-notes.txt`. Files are numbered in sorted order, so the real result would be `00000001-notes.txt`, `00000002-report.pdf`.
- "Each source folder becomes its own batch." A folder with no data files produces no batch, and a folder whose files were already acquired produces none either.
- "Incoming batches are treated as immutable." The code declares this in the manifest and never overwrites, but it does not make the stored files read-only or otherwise prevent a change from outside.
- It does not mention that files in sub-folders of a source are included (with only their file name kept), or that names starting with a dot are skipped.

#### What I should understand before moving on

- Acquisition records bytes and facts about them. It makes no judgement about content, safety or rights; `training_use` is always `review_required`.
- A SHA-256 hash is a 64-character identifier of content. Same bytes, same hash; any change, a different hash. Name and location are not part of it.
- Chunked reading with `while chunk := file.read(n):` processes a file of any size with a fixed, small amount of memory.
- In `acquire_file`, the copy, the hash and the size all come from the same chunks in one pass, so the manifest describes exactly what is stored.
- Mode `"x"`/`"xb"` and `mkdir(exist_ok=False)` make the code unable to overwrite: everything in a batch is created once.
- `source.json` is the batch's description of itself; `source.json.sha256` lets a later reader detect that the manifest was altered.
- A fingerprint is (platform, sorted hashes of all files). It is compared against earlier manifests to skip sources already acquired, and it treats a source as a unit.
- The batch id, `<name>-<UTC time>-<random>`, is the folder name that follows the data through `raw`, `extracted` and `processed`.

#### Self-test

1. You rename `uploads/wiki/a.txt` to `uploads/wiki/article.txt` without changing its content and run acquisition again. Is a new batch created? Explain using what `discovery.py` puts in a fingerprint.
2. A source folder holds 500 files and you fix a typo in one. How many files does the next acquisition copy, and what happens to the earlier batch?
3. Why does `acquire_file` compute the hash inside the copy loop instead of calling `sha256_file(source_file)` before or after copying?
4. What would be different, and worse, if `destination.open("xb")` were `destination.open("wb")`?
5. Someone opens `source.json` in an editor and changes one artifact's `size_bytes`. Nothing else is touched. How can a later stage tell? What if they had changed a byte in a file under `objects/` instead?
6. Acquisition is interrupted after copying 3 of 10 files. Describe what is on disk, and what the next run does about that source.
7. `hashes` is built with `tuple(sorted(...))`. What would go wrong with a plain list, and what would go wrong with a tuple that was not sorted?
8. An `origin.json` declares `"license_identifier": "CC-BY-4.0"`. What does the manifest say under `license`, and does that mean the batch may be used for training?

<details><summary>Answers</summary>

1. No. The fingerprint is the platform plus the sorted tuple of file hashes. A hash depends only on bytes, and the bytes did not change, so the fingerprint computed by the script equals one already in the set and the source is skipped.
2. All 500. One hash changed, so the tuple of hashes differs, the fingerprint is new, and the whole source is acquired into a new batch. The earlier batch is not modified or removed; both now exist.
3. So that the recorded hash is the hash of the bytes actually written. Hashing in a separate pass reads the source a second time, and the file could have changed between the two reads; the manifest would then describe content that is not what is stored. One pass over the same chunks removes that possibility (and reads the file once instead of twice).
4. `"wb"` would silently empty and overwrite a file that already existed at that path. `"xb"` raises `FileExistsError` instead. With `"wb"` a bug or a name collision could replace an object in a batch without any sign; with `"xb"` the "never modify in place" rule is enforced by the operating system.
5. Re-compute the SHA-256 of `source.json` and compare it with the content of `source.json.sha256`: they no longer match. For a changed object, re-compute that file's SHA-256 and compare it with the `sha256` recorded for it in the manifest (and the size with `size_bytes`): they no longer match. The checksum protects the manifest; the manifest protects the objects.
6. A batch folder with `objects/` holding three files, and no `source.json` and no `source.json.sha256`. On the next run `discovery.py` skips that folder because it has no manifest, so no fingerprint matches, and the source is acquired again in full into a new batch with a new id. The unfinished folder remains.
7. A list cannot be put inside a set (it is not hashable), so `fingerprints.add(...)` would raise `TypeError`. An unsorted tuple would make the fingerprint depend on file order: the same contents listed in a different order, for example after a rename changes the sort order of paths, would give a different tuple and the source would wrongly look new.
8. `"identifier": "CC-BY-4.0"`, `"attribution"` as declared (or `null`), and `"status": "review_required"`, `"training_use": "review_required"`. No. The identifier is an unverified claim copied from `origin.json`. Acquisition always writes `review_required`; permission is decided later by the provenance stage.

</details>

---

### 4.2 Inspection

| | |
|---|---|
| **INPUT** | One batch directory written by acquisition: `storage/incoming/batches/<batch_id>/` containing `objects/<8-digit sequence>-<original name>`, the manifest `source.json` and its checksum `source.json.sha256`. Plus the policy file `configs/inspection.json`. |
| **PROCESS** | First decide whether the manifest itself can be trusted. Then, for every artifact the manifest lists, run a fixed series of checks on the stored file (filesystem, limits, extension, integrity, MIME, text, JSON, deep container, malware) and keep the most severe verdict: `accepted_for_ingestion`, `quarantined` or `rejected`. |
| **OUTPUT** | A new directory `storage/catalog/inspections/inspection_<timestamp>_<uuid>/` holding `manifest.json` and `manifest.json.sha256`. If anything was not accepted, also `storage/quarantine/<batch_id>/inspection_<timestamp>_<uuid>/quarantine.json` with its checksum. The incoming files are never moved, changed or deleted. |
| **WHY IT EXISTS** | Uploaded files are untrusted. Before any later stage opens them to pull text out, the pipeline needs proof that each file is what its name claims, was not altered after acquisition, is within size limits, and does not carry things a text corpus has no use for (executables, macros, scripts, zip bombs, XML entity tricks). |

The stage is driven by `scripts/inspection.py` (`python -m scripts.inspection`; its code is in chapter 12). For each pending batch the script makes three calls, in this order: `inspect_batch` (in `inspector.py`), `write_inspection_report` (in `report.py`), `quarantine_batch` (in `quarantine.py`).

**What the incoming batch looks like.** Acquisition (4.1) leaves this on disk, and inspection relies on every part of it:

```
storage/incoming/batches/<source>-<YYYYMMDDTHHMMSSZ>-<8 hex chars>/
  objects/
    00000001-notes.txt
    00000002-report.pdf
  source.json
  source.json.sha256
```

`source.json` has `"schema_version": "1.0.0"`, `"record_type": "incoming_source_batch"`, a `batch_id` equal to the directory name, a `source` object, a `license` object, and an `artifacts` list. Each entry in that list looks like this (made-up values):

```json
{
  "artifact_id": "artifact_00000001",
  "original_filename": "notes.txt",
  "sha256": "<64 lowercase hex characters>",
  "size_bytes": 13,
  "source_metadata": {"origin_folder": "my-source"},
  "source_url": null,
  "stored_relative_path": "objects/00000001-notes.txt"
}
```

`source.json.sha256` contains the SHA-256 of the bytes of `source.json` as hex text, with no trailing newline.

**The three verdicts.** Every check produces one of three decisions, and the code treats them as an ordered scale:

| Decision (value stored in reports) | Meaning in this code | Typical cause |
|---|---|---|
| `accepted_for_ingestion` | Nothing objected. | A well-formed `.txt` file. |
| `quarantined` | Uncertain, corrupt or unverifiable. Held back, could be looked at again. | Empty file, wrong extension for the content, invalid UTF-8, broken ZIP, hash mismatch. |
| `rejected` | A definite policy violation. | Symlink, blocked extension, executable signature, archive path traversal, XML entity declaration, malware hit. |

A decision can only get worse as checks run. One `rejected` check makes the artifact `rejected` no matter how many other checks passed.

**What "quarantine" means here.** Nothing is moved into `storage/quarantine/`. A quarantine record is a small JSON file that *points at* the problem files where they already are. Later stages decide what to read by looking at the inspection report: `scripts/provenance.py` and `scripts/ingestion.py` both read `storage/catalog/inspections/*/manifest.json`, and ingestion skips any artifact whose `decision` is not `accepted_for_ingestion`.

**Two levels of failure.** A problem with `source.json` (missing, checksum mismatch, wrong shape) quarantines the *whole batch*: no artifact is inspected. A problem with one file affects *only that artifact*; its siblings can still be accepted.

#### `src/corpus_factory/inspection/__init__.py`

**Why this file exists** — It marks the folder as a Python package so that `from src.corpus_factory.inspection.checks import ...` works.

**What enters / what leaves** — Nothing. It contains one docstring and no code.

**How it connects** — Python runs it automatically the first time anything inside the package is imported.

**The code, section by section**

```python
"""Artifact safety inspection; incoming source bytes are never modified."""
```

A string on its own as the first statement of a module is a *docstring*: documentation that Python stores as the module's `__doc__`. It states the rule every other file in this package obeys: inspection only reads the incoming bytes.

#### `src/corpus_factory/inspection/result.py`

**Why this file exists** — It defines the vocabulary of the stage: the three decisions, the five malware-scan statuses, and the record types that carry evidence from the checks to the report. Every other file in the package imports from here.

**What enters / what leaves** — No files are read or written. The module exports two enums (`InspectionDecision`, `MalwareScanStatus`), one helper function (`more_restrictive_decision`) and four frozen dataclasses (`MalwareScanResult`, `CheckResult`, `ArtifactInspectionResult`, `InspectionResult`).

**How it connects** — `checks.py` and `deep_inspection.py` create `CheckResult` and `ArtifactInspectionResult` objects. `inspector.py` wraps them in one `InspectionResult` per batch. `report.py` and `quarantine.py` turn that object into JSON.

**The code, section by section**

```python
"""Immutable evidence and monotonic artifact decisions."""
from dataclasses import dataclass
from enum import Enum
```

- `dataclass` — the decorator from the primer in 1 that writes `__init__` and friends for a class that is mostly a list of fields.
- `Enum` — a standard-library base class for a fixed set of named constants. Instead of passing the loose string `"rejected"` around (which could be mistyped), the code passes `InspectionDecision.REJECTED`.

```python
class InspectionDecision(str, Enum):
    ACCEPTED = "accepted_for_ingestion"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"


def more_restrictive_decision(current, candidate):
    order = tuple(InspectionDecision)
    return max((current, candidate), key=order.index)
```

`class InspectionDecision(str, Enum)` inherits from two classes. Because of `Enum`, the class has exactly three members. Because of `str`, each member *is also a string* equal to its value, so `InspectionDecision.QUARANTINED == "quarantined"` is true, and `json.dumps` writes it as plain `"quarantined"` (checked: `json.dumps({'d': InspectionDecision.QUARANTINED})` gives `{"d": "quarantined"}`). That is why the reports contain readable strings and the code never converts by hand.

The order of the three lines matters. They are written from least to most severe, and `more_restrictive_decision` depends on that:

- **What Python does:** `tuple(InspectionDecision)` lists the members in definition order: `(ACCEPTED, QUARANTINED, REJECTED)`. `order.index` is a function that returns a member's position in that tuple (0, 1 or 2). `max((current, candidate), key=order.index)` returns whichever of the two has the larger position.
- **What it means in the pipeline:** combining two verdicts always yields the worse one. `more_restrictive_decision(REJECTED, ACCEPTED)` returns `REJECTED`. This is the "monotonic" in the docstring: a later passing check can never undo an earlier failure.

```python
class MalwareScanStatus(str, Enum):
    NOT_RUN = "not_run"
    UNAVAILABLE = "unavailable"
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"


@dataclass(frozen=True)
class MalwareScanResult:
    status: MalwareScanStatus = MalwareScanStatus.NOT_RUN
    engine: str | None = None
    signature: str | None = None
    error: str | None = None
```

`MalwareScanStatus` is the same kind of string enum, with five possible outcomes of a virus scan. The distinction between them is the point: "the scanner was not installed" (`UNAVAILABLE`), "we never tried" (`NOT_RUN`) and "the scanner crashed" (`ERROR`) are all recorded as themselves and never rounded up to `CLEAN`.

`MalwareScanResult` is one scanner verdict for one file. `@dataclass(frozen=True)` makes instances immutable: after creation, assigning to a field raises an error. `engine` is the path of the scanner program that produced the verdict, `signature` is the name of the malware it matched (only when infected), `error` is a message (only when something went wrong). `str | None = None` means "a string or nothing, default nothing".

```python
@dataclass(frozen=True)
class CheckResult:
    name: str
    decision: InspectionDecision = InspectionDecision.ACCEPTED
    errors: tuple[str, ...] = ()
```

A `CheckResult` is the outcome of one named check on one artifact (or on the batch manifest). Written with only a name, as in `CheckResult('filesystem')`, it means "this check ran and passed": the decision defaults to `ACCEPTED` and `errors` to the empty tuple `()`. `tuple[str, ...]` is the type hint for "a tuple of any number of strings". Tuples are used instead of lists throughout this file because tuples cannot be modified, which fits a frozen record.

```python
@dataclass(frozen=True)
class ArtifactInspectionResult:
    artifact_id: str
    filename: str
    stored_relative_path: str
    decision: InspectionDecision = InspectionDecision.ACCEPTED
    size_bytes: int | None = None
    sha256: str | None = None
    detected_mime_type: str | None = None
    mime_detection_method: str | None = None
    encoding: str | None = None
    character_count: int | None = None
    line_count: int | None = None
    max_line_characters: int | None = None
    is_regular_file: bool = False
    is_symlink: bool = False
    malware_scan_status: MalwareScanStatus = MalwareScanStatus.NOT_RUN
    malware_engine: str | None = None
    malware_signature: str | None = None
    malware_error: str | None = None
    flags: tuple[str, ...] = ()
    checks: tuple[CheckResult, ...] = ()

    @property
    def errors(self):
        return tuple(error for check in self.checks for error in check.errors)
```

`ArtifactInspectionResult` is everything inspection learned about one file. Only the first three fields are required; they come straight from the manifest entry. Everything else starts at "unknown" (`None`, `False`, `NOT_RUN`, `()`) and is filled in as checks run.

| Field | Filled by | Meaning |
|---|---|---|
| `artifact_id`, `filename`, `stored_relative_path` | manifest | Identity. `filename` is the *original* name. |
| `decision` | every check | Worst decision so far. |
| `size_bytes` | filesystem | Size the operating system reports for the stored file. |
| `sha256` | integrity | Hash that inspection computed itself (not the one the manifest claims). |
| `detected_mime_type`, `mime_detection_method` | MIME | What the content looks like, and how that was determined. |
| `encoding`, `character_count`, `line_count`, `max_line_characters` | text | Only for text-type extensions. |
| `is_regular_file`, `is_symlink` | filesystem | What kind of filesystem object the path is. |
| `malware_*` | malware | Copied from a `MalwareScanResult`. |
| `flags` | deep inspection | Non-fatal notes, currently only `pdf_validator_unavailable`. |
| `checks` | every check | The full list of `CheckResult`s, in the order they ran. |

`@property` turns a method into something you read like a field: `artifact.errors`, no parentheses. The body is a generator expression with two `for` clauses (see the primer in 1); read it left to right as nested loops: for each check, for each error in that check, yield the error. The result is one flat tuple of every error message of every check. Because it is computed from `checks` each time, it can never disagree with them. It is not a dataclass field, which matters later in `report.py`.

```python
@dataclass(frozen=True)
class InspectionResult:
    batch_id: str
    source_manifest_sha256: str | None
    policy: dict
    artifacts: tuple[ArtifactInspectionResult, ...] = ()
    checks: tuple[CheckResult, ...] = ()

    @property
    def errors(self):
        return tuple(error for check in self.checks for error in check.errors)

    @property
    def batch_valid(self):
        return not self.errors
```

`InspectionResult` is the result for a whole batch. `source_manifest_sha256` is the hash of `source.json` (or `None` when the manifest could not be read). `policy` is a copy of the configuration that was in force, so the report can show which rules produced the verdicts. `checks` here are *batch-level* checks; in the current code there is exactly one, named `manifest`.

`batch_valid` is `True` when no batch-level check reported an error. `not self.errors` works because an empty tuple counts as false in Python.

```python
    @property
    def duplicate_groups(self):
        groups = {}
        for artifact in self.artifacts:
            if artifact.sha256:
                groups.setdefault(artifact.sha256, []).append(artifact.artifact_id)
        return tuple({"sha256": sha, "count": len(ids), "artifact_ids": ids}
                     for sha, ids in sorted(groups.items()) if len(ids) > 1)
```

`duplicate_groups` finds files in the same batch with identical bytes.

- **What Python does:** `groups` is a dict from hash to a list of artifact ids. `groups.setdefault(key, [])` returns the list stored under `key`, first creating an empty one if the key is new; `.append(...)` then adds to it. The final expression keeps only hashes shared by more than one artifact, sorted by hash so the output order is stable, and builds one small dict per group.
- **What it means in the pipeline:** two files with the same SHA-256 are byte-for-byte copies (see 4.1). Inspection only *reports* them. Nothing is removed here; removing repeated text is the job of the deduplication stage. Artifacts that were never hashed (`sha256` is `None`: rejected early, or empty) are left out.

For two artifacts that share a hash the property returns a shape like `({'sha256': 'ab…', 'count': 2, 'artifact_ids': ['artifact_00000001', 'artifact_00000002']},)`.

```python
    @property
    def summary(self):
        return {
            "total_artifacts": len(self.artifacts),
            "total_bytes": sum(a.size_bytes or 0 for a in self.artifacts),
            **{d.name.lower(): sum(a.decision == d for a in self.artifacts)
               for d in InspectionDecision},
            "duplicate_groups": len(self.duplicate_groups),
            **{f"malware_{s.value}": sum(a.malware_scan_status == s for a in self.artifacts)
               for s in MalwareScanStatus},
        }
```

`summary` builds the counts shown on screen and stored in the report.

- `a.size_bytes or 0` treats an unknown size (`None`) as 0 so `sum` does not fail.
- `**{...}` unpacks a dict into the surrounding dict literal. The first one is a dict comprehension over the three decisions: `d.name.lower()` turns the member name `ACCEPTED` into the key `"accepted"`, and `sum(a.decision == d for a in self.artifacts)` counts matches (each comparison is `True` or `False`, and Python adds those as 1 and 0).
- The second does the same for the five malware statuses, with keys built by an f-string from the *value*: `malware_not_run`, `malware_unavailable`, `malware_clean`, `malware_infected`, `malware_error`.

Real output for a made-up batch of two 5-byte files with the same hash, one accepted and one quarantined:

```
{'total_artifacts': 2, 'total_bytes': 10, 'accepted': 1, 'quarantined': 1, 'rejected': 0, 'duplicate_groups': 1, 'malware_not_run': 2, 'malware_unavailable': 0, 'malware_clean': 0, 'malware_infected': 0, 'malware_error': 0}
```

`total_bytes` adds the size of every artifact whose size is known, including rejected ones.

#### `src/corpus_factory/inspection/config.py`

**Why this file exists** — The limits and lists that drive the checks live in `configs/inspection.json` (its keys are explained in chapter 3). This file reads that JSON and refuses to continue if any value is missing, of the wrong type, contradictory or unknown. A typo in the policy stops the stage before a single file is inspected.

**What enters / what leaves** — `load_inspection_config(path)` reads one JSON file and returns a plain `dict`. `validate_inspection_config(config)` takes a dict and returns the same dict unchanged, or raises `ValueError` with a message naming the bad key. Nothing is written.

**How it connects** — `scripts/inspection.py` calls `load_inspection_config` once and passes the dict (called `policy` everywhere else) to `inspect_batch`. `inspector.py` calls `validate_inspection_config` again on whatever it is given. From then on the checks read values with `policy['some_key']`.

**The code, section by section**

```python
"""Load and validate the external inspection policy before doing any work."""
import json
import math
import re
from pathlib import Path

from paths import PROJECT_DIR

INSPECTION_CONFIG_PATH = PROJECT_DIR / "configs" / "inspection.json"
```

- `json` — parses the policy file.
- `math` — only for `math.isfinite`, used on the compression ratio.
- `re` — regular expressions, used to check the shape of extensions and MIME types.
- `Path` — only used as the type hint of the `path` parameter.
- `PROJECT_DIR` — the project root from `paths.py`; `INSPECTION_CONFIG_PATH` is built from it with the `/` operator, so the default policy is always `configs/inspection.json` inside the project, whatever the current directory is.

```python
def validate_inspection_config(config: dict) -> dict:
    if not isinstance(config, dict):
        raise ValueError("Inspection config must be a JSON object")
    integers = (
        "max_file_size_bytes", "max_batch_size_bytes", "max_files_per_batch",
        "max_line_characters", "max_archive_files", "max_archive_member_bytes",
        "max_uncompressed_bytes", "max_manifest_bytes", "max_structured_bytes",
        "max_xml_depth", "malware_chunk_size", "malware_timeout_seconds",
        "pdf_timeout_seconds", "max_malware_chunk_bytes",
    )
    for key in integers:
        if type(config.get(key)) is not int or config[key] <= 0:
            raise ValueError(f"Inspection config: {key} must be a positive integer")
```

The first guard rejects a file whose top level is not a JSON object (for example a list).

`integers` names the fourteen keys that must be positive whole numbers. The loop checks each one:

- `config.get(key)` returns `None` when the key is missing, so a missing key fails the same test as a wrong type.
- `type(x) is not int` is stricter than `isinstance(x, int)`. In Python `True` is technically an integer (`isinstance(True, int)` is true), and JSON `true` becomes Python `True`. Comparing the exact type means `"max_xml_depth": true` is refused, and so is `10.0`.
- `<= 0` refuses zero and negatives. `or` evaluates its right side only when the left side is false, so `config[key] <= 0` is never reached for a missing key.

```python
    ratio = config.get("max_compression_ratio")
    if type(ratio) not in (int, float) or not math.isfinite(ratio) or ratio <= 0:
        raise ValueError("Inspection config: max_compression_ratio must be finite and positive")
    for key in ("require_malware_scan", "require_deep_container_inspection"):
        if type(config.get(key)) is not bool:
            raise ValueError(f"Inspection config: {key} must be a boolean")
```

`max_compression_ratio` may be a whole number or a decimal (`200` or `200.5`), must be a finite number (not infinity or NaN) and greater than zero. The two `require_...` switches must be real booleans; the string `"false"` or the number `0` is refused.

```python
    for key in ("allowed_extensions", "blocked_extensions", "blocked_mime_types"):
        items = config.get(key)
        pattern = r"\.[a-z0-9]+" if key.endswith("extensions") else r"[a-z0-9.+-]+/[a-z0-9.+-]+"
        if (not isinstance(items, list) or not items
                or any(not isinstance(v, str) or not re.fullmatch(pattern, v) for v in items)
                or len(set(items)) != len(items)):
            raise ValueError(f"Inspection config: invalid {key}")
    if set(config["allowed_extensions"]) & set(config["blocked_extensions"]):
        raise ValueError("Inspection config: allowed and blocked extensions overlap")
```

The three list-valued keys share one loop. A regular expression describes what one item must look like:

| Pattern | For | Reads as |
|---|---|---|
| `\.[a-z0-9]+` | keys ending in `extensions` | a dot, then one or more lowercase letters or digits: `.txt`, `.docx` |
| `[a-z0-9.+-]+/[a-z0-9.+-]+` | `blocked_mime_types` | type, slash, subtype, lowercase: `text/plain`, `application/epub+zip` |

`re.fullmatch` succeeds only if the *entire* string matches, so `.TXT`, `txt` and `.tar.gz` are all refused. The `r"..."` prefix (a raw string) tells Python not to treat backslashes specially, so `\.` reaches the regex engine intact.

The `if` then fails the list when it is not a list, is empty, contains a non-string or a badly shaped string, or contains a repeat (`len(set(items)) != len(items)` — turning a list into a set drops duplicates, so the lengths differ if there were any).

Requiring lowercase here is what makes the later checks correct: the checks lowercase the file's extension before looking it up, so the lists must be lowercase too.

The last two lines refuse a policy in which the same extension is both allowed and blocked. `&` between two sets is their intersection; a non-empty set is truthy.

```python
    expected = config.get("expected_mime_types")
    if not isinstance(expected, dict) or set(expected) != set(config["allowed_extensions"]):
        raise ValueError("Inspection config: expected_mime_types must cover exactly allowed_extensions")
    for ext, mimes in expected.items():
        if (not isinstance(mimes, list) or not mimes
                or any(not isinstance(m, str) or not re.fullmatch(r"[a-z0-9.+-]+/[a-z0-9.+-]+", m) for m in mimes)):
            raise ValueError(f"Inspection config: invalid expected MIME types for {ext}")
        if set(mimes) & set(config["blocked_mime_types"]):
            raise ValueError(f"Inspection config: expected and blocked MIME types overlap for {ext}")
```

`expected_mime_types` maps each extension to the content types that are acceptable for it. Three rules:

1. Its keys must be *exactly* the allowed extensions, no more and no fewer (`set(expected) != set(...)`). You cannot allow an extension without saying what its content should look like.
2. Each value must be a non-empty list of well-shaped MIME strings.
3. No extension may expect a MIME type that is also blocked.

```python
    if config.get("unknown_file_policy") not in ("quarantine", "reject"):
        raise ValueError("Inspection config: unknown_file_policy must be quarantine or reject")
    if config['max_malware_chunk_bytes'] < config['max_file_size_bytes']:
        raise ValueError('Inspection config: max_malware_chunk_bytes must accommodate max_file_size_bytes')
    known = set(integers) | {'max_compression_ratio', 'require_malware_scan',
                           'require_deep_container_inspection', 'allowed_extensions',
                           'blocked_extensions', 'blocked_mime_types', 'expected_mime_types',
                           'unknown_file_policy'}
    if config.keys() - known:
        raise ValueError(f'Inspection config: unknown keys: {sorted(config.keys() - known)}')
    return config
```

- `unknown_file_policy` must be one of two words. It decides what happens to a file whose extension is not in `allowed_extensions`.
- `max_malware_chunk_bytes` must be at least `max_file_size_bytes`. The malware check groups files into chunks under a byte budget; this rule guarantees the largest permitted file fits in a chunk by itself.
- `known` is the set of every key this function understands. `config.keys() - known` is set subtraction: the keys present in the file but not understood. If there are any, the config is refused. So a key cannot be silently ignored: a misspelt required key (`max_file_size_byte`) already fails earlier as a missing key, and any extra key that is not in this set fails here.

The function returns the dict it was given. It does not copy or fill in defaults; **every** key must be in the JSON.

```python
def load_inspection_config(path: Path = INSPECTION_CONFIG_PATH) -> dict:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"Cannot load inspection config {path}: {error}") from error
    return validate_inspection_config(config)
```

`path.read_text(encoding="utf-8")` reads the whole file as text and `json.loads` parses it. Three kinds of failure are caught: `OSError` (file missing or unreadable), `UnicodeError` (not valid UTF-8) and `ValueError` (not valid JSON; `json.JSONDecodeError` is a kind of `ValueError`). All become one `ValueError` that names the file; `from error` keeps the original as the cause (primer in 1).

**How the code uses each key.** Every key in `configs/inspection.json` is validated here, and every one is read somewhere in the stage:

| Key | Read in | Effect |
|---|---|---|
| `max_file_size_bytes`, `max_files_per_batch`, `max_batch_size_bytes` | `inspect_artifact`, `inspect_batch` | Artifact `rejected` before it is read. |
| `max_manifest_bytes` | `read_manifest` | Batch quarantined. |
| `allowed_extensions`, `blocked_extensions`, `unknown_file_policy` | `inspect_artifact`; `blocked_extensions` also inside archives | Extension verdicts. |
| `expected_mime_types`, `blocked_mime_types` | `inspect_artifact` | MIME verdicts. |
| `max_line_characters` | `inspect_artifact` (text), `_inspect_html` | `quarantined`. |
| `max_structured_bytes` | `_inspect_json`, `inspect_xml`, `bounded_zip` | Bounds parsers. |
| `max_xml_depth` | `inspect_xml` | `rejected`. |
| `max_archive_files`, `max_archive_member_bytes`, `max_uncompressed_bytes`, `max_compression_ratio` | `bounded_zip`, `_inspect_zip` | `rejected`. |
| `require_deep_container_inspection`, `pdf_timeout_seconds` | `_inspect_pdf` only | See the PDF section. |
| `require_malware_scan`, `malware_chunk_size`, `max_malware_chunk_bytes`, `malware_timeout_seconds` | malware functions | See the malware section. |

#### `src/corpus_factory/inspection/checks.py`

**Why this file exists** — It holds the checks themselves, except the format-specific parsers (those are in `deep_inspection.py`). It opens files in a way that cannot be redirected by symbolic links, validates the batch manifest, hashes each artifact, works out what the content really is, measures text, validates JSON, and runs the virus scanner.

**What enters / what leaves**

| Function | Takes | Returns / raises |
|---|---|---|
| `open_regular(path)` | a path | context manager yielding a binary read stream; raises `OSError` or `UnsafeContent` |
| `safe_artifact_path(batch_dir, relative)` | batch directory, `stored_relative_path` | the full path; raises `UnsafeContent` |
| `stream_hash(stream, max_bytes, destination)` | open stream | SHA-256 hex string; optionally copies the bytes |
| `read_manifest(batch_dir, policy)` | batch directory | `(manifest dict, sha256 of source.json)`; raises on any problem |
| `detect_encoding(prefix)` | first bytes of a file | codec name |
| `_detect_mime(stream, policy)` | open stream | `(mime type or None, method)` |
| `inspect_text(stream, encoding, policy)` | open stream | `(characters, lines, longest line)` |
| `_inspect_json(...)` | open stream | nothing; raises `ValueError` if invalid |
| `inspect_artifact(batch_dir, artifact, policy, remaining_bytes, within_count)` | one manifest entry | one `ArtifactInspectionResult`; never raises for a bad file |
| `scan_malware_batch(batch_dir, artifacts, policy)` | results so far | dict `artifact_id -> MalwareScanResult` |
| `apply_malware_result(artifact, malware, policy)` | one result, one verdict | a new `ArtifactInspectionResult` |

Files read: `source.json`, `source.json.sha256`, and each `objects/...` file. Files written: only temporary copies in the system temporary directory, deleted automatically. Nothing under `storage/` is written by this file.

**How it connects** — `inspector.py` calls `read_manifest`, then `inspect_artifact` once per artifact, then `scan_malware_batch` and `apply_malware_result`. `inspect_artifact` calls `inspect_deep_container` from `deep_inspection.py` for the formats that need it.

**The code, section by section**

```python
"""Filesystem, content, integrity, and chunked malware checks."""
import codecs
import errno
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile
import zlib
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path, PurePosixPath
```

| Import | Why this file needs it |
|---|---|
| `codecs` | Byte-order-mark constants and *incremental decoders* (turn bytes into text piece by piece). |
| `errno` | Named operating-system error numbers (`ELOOP`, `ENOTDIR`) used to classify a failure. |
| `hashlib` | SHA-256 (see 4.1). |
| `io` | `io.TextIOWrapper`, which presents a byte stream as a text stream. |
| `json` | Parses the manifest and validates JSON artifacts. |
| `os` | Low-level file calls: `os.open`, `os.fstat`, `os.close`, `os.fdopen`. |
| `re` | Regular expressions (hash format, line splitting). |
| `shutil` | `shutil.which`, which looks a program up on the `PATH`. |
| `stat` | Helpers that interpret a file's mode bits: regular file, symlink, directory. |
| `subprocess` | Runs the external virus scanner. |
| `tempfile` | Temporary files and directories that delete themselves. |
| `zipfile`, `zlib` | Only their exception types, caught at the bottom of `inspect_artifact`. |
| `contextmanager` | Turns a generator function into something usable in a `with` statement. |
| `replace` | `dataclasses.replace(obj, field=value)` returns a *copy* of a frozen dataclass with some fields changed. This is how results are "updated" although they are immutable. |
| `Path`, `PurePosixPath` | `Path` touches the real filesystem. `PurePosixPath` only parses a string with `/` rules and never touches the disk. |

```python
from src.corpus_factory.inspection.deep_inspection import (
    CHUNK, DEEP_EXTENSIONS, ZIP_FORMATS, UnsafeContent, bounded_zip,
    inspect_deep_container,
)
from src.corpus_factory.inspection.result import (
    ArtifactInspectionResult, CheckResult, InspectionDecision as D,
    MalwareScanResult, MalwareScanStatus as M, more_restrictive_decision,
)

TEXT_EXTENSIONS = {'.txt', '.text', '.md', '.markdown', '.csv', '.tsv', '.json',
                   '.jsonl', '.ndjson', '.html', '.htm', '.xml', '.yaml', '.yml', '.log'}
```

The names from `deep_inspection.py` are explained in that file's section; for now: `CHUNK` is `65536` (bytes read at a time), `UnsafeContent` is the exception that means "definite violation, reject", and `bounded_zip` opens a ZIP file safely. `InspectionDecision as D` and `MalwareScanStatus as M` are short aliases, so `D.REJECTED` and `M.CLEAN` appear below.

`TEXT_EXTENSIONS` is the set of extensions that get the text check. It is fixed in code, not in the JSON policy. `.html`, `.htm` and `.xml` appear both here and in `DEEP_EXTENSIONS`, so those files get the text check and then a structural check.

**Background: why opening a file needs care.** A *symbolic link* (symlink) is a tiny filesystem entry that says "I am really that other path". If `objects/00000001-notes.txt` were replaced by a symlink to some private file elsewhere on the machine, a naive `open()` would follow it and the pipeline would read, and later train on, a file nobody uploaded. The same trick works one level up: replace the `objects` directory with a link. The next two functions exist to make "open this path" mean "open exactly this object, and only if it is an ordinary file". The first is the Windows version, the second is the general entry point with the macOS/Linux version inside it.

```python
@contextmanager
def _windows_regular(path):
    """Open reparse points themselves; retain parents without delete sharing."""
    import ctypes
    import msvcrt
    from ctypes import wintypes

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                       wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    create.restype = wintypes.HANDLE
    close = kernel.CloseHandle
    close.argtypes = [wintypes.HANDLE]
    close.restype = wintypes.BOOL
    information = kernel.GetFileInformationByHandle
    information.argtypes = [wintypes.HANDLE, wintypes.LPVOID]
    information.restype = wintypes.BOOL
```

This function only runs on Windows; on macOS and Linux it is defined but never called. The imports are inside the function because `msvcrt` exists only on Windows, and importing it at the top of the file would crash everywhere else.

`@contextmanager` is explained with `open_regular` below.

`ctypes` lets Python call functions in a compiled system library directly. `ctypes.WinDLL('kernel32', use_last_error=True)` loads the core Windows library and asks ctypes to remember the system error code after each call. The lines after it describe three functions so that ctypes passes arguments of the right size:

| Name | Windows function | Purpose |
|---|---|---|
| `create` | `CreateFileW` | open a file or directory and get a *handle* (Windows' word for an open-file token) |
| `close` | `CloseHandle` | release a handle |
| `information` | `GetFileInformationByHandle` | read metadata of an already open handle |

`argtypes` is the list of parameter types, `restype` the return type. `parents` will hold the handles of the parent directories and `leaf` the handle of the file itself.

```python
    parents = []
    leaf = None
    try:
        for component in (*reversed(path.parents), path):
            is_leaf = component == path
            # OPEN_EXISTING, BACKUP_SEMANTICS | OPEN_REPARSE_POINT.
            handle = create(str(component), 0x80000000 if is_leaf else 0,
                            1 if is_leaf else 3, None, 3, 0x02200000, None)
            if handle == ctypes.c_void_p(-1).value:
                raise ctypes.WinError(ctypes.get_last_error())
            if is_leaf:
                leaf = handle
            else:
                parents.append(handle)
            # BY_HANDLE_FILE_INFORMATION is thirteen DWORDs; attributes first.
            metadata = (wintypes.DWORD * 13)()
            if not information(handle, ctypes.byref(metadata)):
                raise ctypes.WinError(ctypes.get_last_error())
            if metadata[0] & 0x400:
                raise UnsafeContent('symlink/reparse point in artifact path')
            if not is_leaf and not metadata[0] & 0x10:
                raise UnsafeContent('non-directory parent in artifact path')
```

`path.parents` is every ancestor of the path, nearest first; `reversed(...)` makes it root first; `(*..., path)` appends the file itself. So the loop walks from the drive root down to the file, opening each component.

The numbers passed to `create` are Windows constants:

| Value | Constant | Meaning |
|---|---|---|
| `0x80000000` (leaf) / `0` (parents) | `GENERIC_READ` / none | read the file's data; for directories only metadata is needed |
| `1` (leaf) / `3` (parents) | share modes | others may read the file; others may read and write inside the directories. Delete-sharing is not granted, so a directory cannot be removed or renamed while its handle is held. |
| `3` | `OPEN_EXISTING` | never create anything |
| `0x02200000` | `FILE_FLAG_BACKUP_SEMANTICS` + `FILE_FLAG_OPEN_REPARSE_POINT` | the first allows opening directories; the second says "if this is a link, open the link itself, do not follow it" |

A *reparse point* is the Windows mechanism behind symlinks and junctions. `ctypes.c_void_p(-1).value` is how the failure value `INVALID_HANDLE_VALUE` looks from Python; in that case the function raises an `OSError` built from the Windows error code.

`(wintypes.DWORD * 13)()` creates an array of thirteen 32-bit integers, the size of the structure Windows fills in. Only the first, the attribute bits, is used: `0x400` is "this is a reparse point" and `0x10` is "this is a directory". A link anywhere in the path, or a parent that is not a directory, raises `UnsafeContent`.

```python
        descriptor = msvcrt.open_osfhandle(leaf, os.O_RDONLY | os.O_BINARY)
        leaf = None  # Ownership transferred to the CRT descriptor.
        with os.fdopen(descriptor, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise UnsafeContent('not a regular file')
            yield stream
    finally:
        if leaf is not None:
            close(leaf)
        for handle in reversed(parents):
            close(handle)
```

`msvcrt.open_osfhandle` converts the Windows handle into an ordinary file descriptor (a small integer) and `os.fdopen` wraps that in a normal Python file object. Setting `leaf = None` records that the descriptor now owns the handle, so the `finally` block must not close it a second time. `os.fstat(...)` asks about the *open* file, and `stat.S_ISREG` checks it is a regular file. `yield stream` hands the file to the `with` block of the caller. The `finally` block runs whatever happens and releases every handle, children before parents.

```python
@contextmanager
def open_regular(path):
    """Reject links at every component; pin parent directories on POSIX."""
    path = Path(path).absolute()
    if os.name == 'nt':
        with _windows_regular(path) as stream:
            yield stream
        return
```

`open_regular` is what the rest of the file uses: `with open_regular(path) as stream:`.

**What Python does:** `@contextmanager` converts a function containing one `yield` into a context manager. The code before `yield` runs when the `with` block is entered, the yielded value becomes the `as` variable, and the code after `yield` (here, the `finally` blocks) runs when the block is left, even through an exception. Generators and `yield` are taught in chapter 5.

`Path(path).absolute()` makes the path start at the filesystem root *without* resolving links. (`resolve()` would follow links and hide exactly what this function wants to detect.) `os.name == 'nt'` is true on Windows; there the work is delegated and the function returns.

```python
    descriptor = None
    parent = None
    try:
        if os.open in os.supports_dir_fd and hasattr(os, 'O_NOFOLLOW'):
            parent = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
            for part in path.parts[1:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
                os.close(parent)
                parent = child
            descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        else:
            raise OSError('safe no-follow file opening unavailable on this platform')
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError('not a regular file')
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            yield stream
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if parent is not None:
            os.close(parent)
```

The macOS/Linux version. A *file descriptor* is the integer the operating system gives you for an open file or directory.

- `os.open in os.supports_dir_fd and hasattr(os, 'O_NOFOLLOW')` asks whether this platform supports the two features needed. If not, the function refuses to open anything rather than fall back to an unsafe open.
- `os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)` opens the root directory `/`. Flags are combined with `|`: read-only, and "fail unless this is a directory".
- The loop goes through every directory name between the root and the file (`path.parts[1:-1]` skips the root at the start and the file name at the end). `os.open(part, ..., dir_fd=parent)` opens the name `part` *relative to the already open directory* `parent`. `O_NOFOLLOW` makes the call fail if `part` is a symlink. Then the old parent is closed and the child becomes the new parent.
- Finally the file itself is opened the same way. `O_NONBLOCK` prevents the call from hanging forever if the name turns out to be a named pipe.

**What it means in the pipeline:** the path is walked one hop at a time, each hop anchored to a directory that is already held open and each hop refusing links. Nobody can swap a directory for a link between the check and the open, because there is no gap: checking and opening are the same system call.

`os.fstat(descriptor)` then confirms the opened thing is a regular file (not a directory, device or pipe). `os.fdopen(descriptor, 'rb')` wraps the descriptor in a Python file object opened for reading bytes; `descriptor = None` again marks the transfer of ownership so the `finally` block only closes what is still its own.

When a symlink is met, the operating system reports error `ELOOP` (or `ENOTDIR` for a parent). `inspect_artifact` uses those two error numbers to choose `rejected` over `quarantined`.

```python
def safe_artifact_path(batch_dir, relative):
    parts = PurePosixPath(relative).parts
    if (len(parts) != 2 or parts[0] != 'objects' or parts[1] in {'.', '..'}
            or '\\' in relative or ':' in relative or any(ord(c) < 32 for c in relative)
            or relative != '/'.join(parts)):
        raise UnsafeContent('unsafe stored_relative_path; expected objects/<filename>')
    return batch_dir / relative
```

`safe_artifact_path` validates the `stored_relative_path` string from the manifest *as a string*, before the filesystem is touched. `PurePosixPath("objects/00000001-notes.txt").parts` is `('objects', '00000001-notes.txt')`. The path is refused unless all of these hold:

| Condition | Blocks |
|---|---|
| exactly two parts, the first being `objects` | `../../etc/passwd`, `objects/a/b`, absolute paths |
| second part is not `.` or `..` | climbing out of `objects` |
| no backslash, no colon | Windows separators and drive letters such as `C:` |
| no character with code below 32 | control characters, including NUL and newline |
| `relative == '/'.join(parts)` | disguised spellings such as `objects//x` or `objects/x/`, which parse to the same parts but are not the canonical string |

This is protection against *path traversal*: a manifest entry crafted to make the pipeline read a file outside the batch. Failure raises `UnsafeContent`, which ends in `rejected`. On success the function returns `batch_dir / relative`.

```python
def stream_hash(stream, max_bytes, destination=None):
    stream.seek(0)
    digest = hashlib.sha256()
    size = 0
    while chunk := stream.read(CHUNK):
        size += len(chunk)
        if size > max_bytes:
            raise OSError('artifact grew during inspection')
        digest.update(chunk)
        if destination is not None:
            destination.write(chunk)
    return digest.hexdigest()
```

`stream_hash` computes the SHA-256 of a stream in 64 KiB chunks (chunked hashing and `:=` are explained in 4.1) with two additions:

- `max_bytes`: if more bytes arrive than expected, the file grew after its size was measured, and the function raises.
- `destination`: if given, every chunk is also written there. This is how `inspect_artifact` makes its private copy: **the bytes that are hashed and the bytes that are copied are the same bytes, read once.**

```python
def read_manifest(batch_dir, policy):
    with open_regular(batch_dir / 'source.json') as stream:
        if os.fstat(stream.fileno()).st_size > policy['max_manifest_bytes']:
            raise ValueError('source.json exceeds manifest size limit')
        data = stream.read(policy['max_manifest_bytes'] + 1)
        if len(data) > policy['max_manifest_bytes']:
            raise ValueError('source.json exceeds manifest size limit')
    actual_hash = hashlib.sha256(data).hexdigest()
    with open_regular(batch_dir / 'source.json.sha256') as stream:
        expected_hash = stream.read(1024).decode('ascii').strip()
    if expected_hash != actual_hash:
        raise ValueError('source.json.sha256 mismatch')
```

`read_manifest` is the batch trust gate. It either returns a manifest it has verified, or raises, and any exception here quarantines the entire batch.

- `source.json` is opened with `open_regular`, so a symlinked manifest is refused.
- The size is checked twice: once from the file's metadata (`st_size`), and again after reading. `stream.read(limit + 1)` reads at most one byte more than allowed, so the program never loads an enormous file into memory, yet can still tell "exactly at the limit" from "over the limit".
- `hashlib.sha256(data).hexdigest()` hashes the raw bytes just read.
- `source.json.sha256` is read (at most 1024 bytes), decoded as ASCII, and stripped of surrounding whitespace. If it differs from the computed hash, the manifest was altered or damaged after acquisition wrote it.

**What it means in the pipeline:** everything inspection knows about the batch comes from `source.json`. The checksum comparison is done on the bytes *before* they are parsed, so the JSON parser only ever sees content that matches what acquisition recorded.

Note what the checksum does and does not prove: it detects accidental damage and a careless edit. Someone able to rewrite both files consistently would pass it.

```python
    manifest = json.loads(data)
    if not isinstance(manifest, dict):
        raise ValueError('source.json must contain a JSON object')
    if manifest.get('batch_id') != batch_dir.name:
        raise ValueError('source.json batch_id does not match directory name')
    if manifest.get('schema_version') != '1.0.0' or manifest.get('record_type') != 'incoming_source_batch':
        raise ValueError('unsupported source manifest schema or record_type')
    if not isinstance(manifest.get('source'), dict) or not isinstance(manifest.get('license'), dict):
        raise ValueError('source and license must be objects')
    artifacts = manifest.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError('artifacts must be a nonempty list')
```

`json.loads(data)` accepts bytes directly. Then the shape is checked field by field: a JSON object at the top, `batch_id` equal to the directory name (a manifest copied into the wrong directory is refused), the exact schema version and record type that acquisition writes, `source` and `license` present as objects, and `artifacts` a non-empty list. `manifest.get('x')` returns `None` for a missing key, and `isinstance(None, dict)` is false, so missing and wrong-typed are caught by the same line.

```python
    ids, paths = set(), set()
    for item in artifacts:
        if not isinstance(item, dict):
            raise ValueError('each artifact must be an object')
        for key in ('artifact_id', 'original_filename', 'stored_relative_path', 'sha256'):
            if not isinstance(item.get(key), str) or not item[key]:
                raise ValueError(f'artifact {key} must be a nonempty string')
        if not re.fullmatch(r'[a-f0-9]{64}', item['sha256']):
            raise ValueError('artifact sha256 must contain 64 lowercase hex characters')
        if type(item.get('size_bytes')) is not int or item['size_bytes'] < 0:
            raise ValueError('artifact size_bytes must be a nonnegative integer')
        if item['artifact_id'] in ids or item['stored_relative_path'] in paths:
            raise ValueError('duplicate artifact ID or stored path in manifest')
        ids.add(item['artifact_id'])
        paths.add(item['stored_relative_path'])
    return manifest, actual_hash
```

Each artifact entry must be an object with four non-empty strings, a `sha256` of exactly 64 lowercase hexadecimal characters (`[a-f0-9]{64}` with `re.fullmatch`), and a `size_bytes` that is a true integer, zero or more. `ids` and `paths` are sets that remember what has been seen: a repeated `artifact_id` or `stored_relative_path` raises. Without that, two entries could point at the same file, or two files could share an identity in the report.

`ids, paths = set(), set()` assigns two variables in one line.

The function returns the parsed manifest and the hash of `source.json`; the hash goes into the report as `source_manifest_sha256`.

```python
def detect_encoding(prefix):
    if prefix.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
        raise UnicodeError('UTF-32 is not supported')
    if prefix.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    if prefix.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return 'utf-16'
    return 'utf-8'
```

**Background: byte order marks.** A text file is bytes; an *encoding* is the rule for turning bytes into characters (the full treatment is in chapter 6). Some files begin with a short marker called a BOM that announces the encoding:

| First bytes (hex) | Encoding | Python codec returned |
|---|---|---|
| `EF BB BF` | UTF-8 with BOM | `utf-8-sig` (decodes UTF-8 and drops the marker) |
| `FF FE` or `FE FF` | UTF-16, little or big endian | `utf-16` (reads the marker to learn the byte order, then drops it) |
| `FF FE 00 00` or `00 00 FE FF` | UTF-32 | none: raises `UnicodeError` |
| anything else | assumed UTF-8 | `utf-8` |

`prefix.startswith((a, b))` with a tuple means "starts with any of these". The UTF-32 test must come first: the UTF-32 little-endian marker `FF FE 00 00` *begins with* the UTF-16 marker `FF FE`, so testing UTF-16 first would misidentify it.

A file with no BOM is assumed to be UTF-8. That is an assumption, not a detection; if it is wrong, the strict decoding in `inspect_text` fails and the file is quarantined.

```python
def _detect_mime(stream, policy):
    stream.seek(0)
    prefix = stream.read(8192)
    if prefix.startswith(b'MZ'):
        return 'application/x-dosexec', 'builtin-signature'
    if prefix.startswith(b'\x7fELF'):
        return 'application/x-elf', 'builtin-signature'
    if prefix[:4] in (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe'):
        return 'application/x-mach-binary', 'builtin-signature'
    if prefix.startswith(b'#!'):
        return 'text/x-shellscript', 'builtin-signature'
    if prefix.startswith(b'%PDF-'):
        return 'application/pdf', 'builtin-signature'
    if prefix.lower().startswith(b'{\\rtf'):
        return 'application/rtf', 'builtin-signature'
    if prefix.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        return 'application/x-ole-storage', 'builtin-signature'
```

**Background: magic numbers.** A file's name is just a label anyone can change. Its *content* usually starts with a fixed byte sequence that identifies the format, called a signature or magic number. A *MIME type* is a standard name for a kind of content, such as `text/plain` or `application/pdf`. `_detect_mime` reads the first 8192 bytes and derives a MIME type from the content alone; the filename is not even passed in.

| Starts with | Format | Returned MIME |
|---|---|---|
| `MZ` | Windows/DOS executable | `application/x-dosexec` |
| `\x7fELF` | Linux executable | `application/x-elf` |
| `FE ED FA CE`, `CE FA ED FE`, `FE ED FA CF`, `CF FA ED FE`, `CA FE BA BE` | macOS executable (32-bit, 64-bit, both byte orders, multi-architecture) | `application/x-mach-binary` |
| `#!` | script with an interpreter line, e.g. `#!/bin/sh` | `text/x-shellscript` |
| `%PDF-` | PDF | `application/pdf` |
| `{\rtf` (any letter case) | Rich Text Format | `application/rtf` |
| `D0 CF 11 E0 A1 B1 1A E1` | OLE compound file, the container of legacy `.doc` | `application/x-ole-storage` |

`b'...'` is a bytes literal; `\x7f` is one byte written in hexadecimal. `prefix[:4] in (...)` compares the first four bytes against a tuple of candidates. The function returns a pair: the MIME type and the method, here `'builtin-signature'`. The first four rows are all in `blocked_mime_types`, so those files end up `rejected`. Note the `#!` rule looks only at two bytes: a Markdown or text file whose very first characters are `#!` is classified as a shell script and rejected.

```python
    if prefix.startswith(b'PK'):
        with bounded_zip(stream, policy) as archive:
            names = archive.namelist()
            for required, mime in ZIP_FORMATS.values():
                if required in names:
                    if required == 'content.xml':
                        if 'mimetype' in names and archive.getinfo('mimetype').file_size < 256:
                            return archive.read('mimetype').decode('ascii'), 'builtin-container'
                        return 'application/zip', 'builtin-container'
                    return mime, 'builtin-container'
        return 'application/zip', 'builtin-container'
```

`PK` are the first two bytes of every ZIP file, and `.docx`, `.xlsx`, `.pptx`, `.odt`, `.ods` and `.epub` are all ZIP files with a particular set of members inside. `bounded_zip` (next file) opens the archive under limits; `archive.namelist()` lists the member names without decompressing anything.

`ZIP_FORMATS.values()` yields `(required member, mime)` pairs. The loop asks, in table order, "does this archive contain `word/document.xml`? `xl/workbook.xml`? ...". The first hit decides the type. `content.xml` is special because both `.odt` and `.ods` use it: OpenDocument files carry a tiny member called `mimetype` whose content *is* the MIME string, so the code reads it (only if it is under 256 bytes) and returns what it says. A ZIP that matches nothing is `application/zip`, which is not an expected type for any extension, so a plain ZIP renamed to `.docx` is quarantined by the MIME check.

```python
    try:
        text = codecs.getincrementaldecoder(detect_encoding(prefix))().decode(prefix, final=False)
        if any(ord(c) < 32 and c not in '\t\r\n\f' for c in text):
            raise UnicodeError('binary control bytes')
        stripped = text.lstrip().lower()
        if stripped.startswith(('<!doctype html', '<html', '<head', '<body')):
            return 'text/html', 'builtin-text'
        if stripped.startswith('<'):
            return 'application/xml', 'builtin-text'
        return 'text/plain', 'builtin-text'
    except UnicodeError:
        # Optional libmagic only supplements unknown binary signatures.
        try:
            import magic
            return magic.from_buffer(prefix, mime=True).lower(), 'libmagic'
        except (ImportError, AttributeError, OSError, RuntimeError):
            return None, 'unavailable'
```

No signature matched, so the content is tested as text.

- `codecs.getincrementaldecoder(name)()` creates a decoder object for the detected encoding. `decode(prefix, final=False)` decodes the 8192 bytes but tolerates the last character being cut in half at the boundary (an Arabic letter is two bytes in UTF-8, and the cut can fall between them).
- `any(ord(c) < 32 and c not in '\t\r\n\f' for c in text)` looks for *control characters*: codes below 32 other than tab, carriage return, newline and form feed. Real text does not contain them; binary data almost always does (the zero byte in particular).
- If the text, after dropping leading whitespace and lowercasing, starts like an HTML page, the type is `text/html`. Anything else that starts with `<` is called `application/xml`. Everything else is `text/plain`.

Real results from calling the function on tiny made-up inputs:

| Bytes | Result |
|---|---|
| `b'hello'` | `('text/plain', 'builtin-text')` |
| `b'{"a": 1}'` | `('text/plain', 'builtin-text')` |
| `b'<html>'` | `('text/html', 'builtin-text')` |
| `b'<div>hi</div>'` | `('application/xml', 'builtin-text')` |
| `b'<?xml version="1.0"?><html>'` | `('application/xml', 'builtin-text')` |
| `b'h\x00i\x00'` (UTF-16 without BOM) | `(None, 'unavailable')` |

Two consequences follow from this heuristic and are worth knowing. An `.html` file that does not start with `<!doctype html`, `<html`, `<head` or `<body` (for example an HTML fragment, a page that starts with a comment, or XHTML that starts with `<?xml`) is detected as `application/xml`, which is not in the expected list for `.html`, so it is quarantined. And a `.md` or `.txt` file whose first non-blank character is `<` is also detected as XML and quarantined for the same reason.

The `except UnicodeError` branch handles content that is neither a known signature nor decodable text. It tries the optional third-party library `python-magic` (`import magic`), which wraps the same database as the Unix `file` command. If the library is missing or fails, the result is `(None, 'unavailable')`. That library is not listed in `requirements.txt` and is not installed in the project's `.venv`, so in this project the fallback always yields `None`, and an artifact with MIME `None` fails the MIME comparison and is quarantined.

```python
def detect_mime_type(path, policy):
    with open_regular(path) as stream:
        return _detect_mime(stream, policy)[0]
```

A public convenience wrapper: open a path safely and return only the MIME type (`[0]` takes the first element of the pair). Nothing in `src/`, `scripts/` or `tests/` calls it; `inspect_artifact` calls `_detect_mime` directly on its private copy.

```python
def inspect_text(stream, encoding, policy):
    stream.seek(0)
    decoder = codecs.getincrementaldecoder(encoding)(errors='strict')
    characters = lines = longest = current = 0
    previous_cr = False
    while True:
        chunk = stream.read(CHUNK)
        text = decoder.decode(chunk, final=not chunk)
        characters += len(text)
        if any(ord(c) < 32 and c not in '\t\r\n\f' for c in text):
            raise ValueError('binary control characters in text')
        if previous_cr and text.startswith('\n'):
            text = text[1:]
        if text:
            previous_cr = text.endswith('\r')
            parts = re.split(r'\r\n|\r|\n', text)
            current += len(parts[0])
            longest = max(longest, current)
            if len(parts) > 1:
                lines += len(parts) - 1
                longest = max(longest, *(len(part) for part in parts[1:]))
                current = len(parts[-1])
        if not chunk:
            break
    return characters, lines + bool(current), longest
```

`inspect_text` decodes the whole file and measures it. It returns three numbers: character count, line count, and the length of the longest line.

The decoder is created with `errors='strict'`: the first byte sequence that is not valid in the encoding raises `UnicodeDecodeError`. `characters = lines = longest = current = 0` sets four counters to zero. `current` is the length of the line being read *so far*; it has to survive from one chunk to the next because a line can straddle two chunks.

Per chunk:

1. `decoder.decode(chunk, final=not chunk)`: when `stream.read` returns empty bytes the file is finished, `not chunk` is `True`, and the decoder is told to flush; if a character was left half-finished at the end of the file, this is where it raises.
2. `characters += len(text)`: counts characters, not bytes. Line-break characters are included; a BOM is not, because the codec already removed it.
3. The control-character test, the same as in `_detect_mime` but now over the whole file. A hit raises `ValueError`.
4. `previous_cr`: Windows line endings are two characters, `\r\n`. If one chunk ended with `\r` and the next begins with `\n`, they are one line break, not two, so the leading `\n` is dropped before counting.
5. `re.split(r'\r\n|\r|\n', text)` cuts the text at every line break of any of the three styles. The pattern lists `\r\n` first so that pair is consumed as one break. If the text was `"ab\ncd\nef"`, `parts` is `['ab', 'cd', 'ef']`.
   - `parts[0]` continues the line already in progress: `current += len(parts[0])`.
   - If there is more than one part, there were `len(parts) - 1` line breaks. The longest of the remaining parts is compared with `longest`, and the last part becomes the new line in progress.
6. `if not chunk: break` ends the loop after the final flush.

`lines + bool(current)` adds one for a last line that has no line break after it (`bool` of a non-zero number is `True`, which counts as 1). So `"a\nb\n"` is two lines, not three.

Real output: for the bytes of `"hello\nمرحبا\r\ni love coffee"` the function returns `(26, 3, 13)` — 26 characters (5 + 1 + 5 + 2 + 13), 3 lines, longest line 13. For `b"a\nb\n"` it returns `(4, 2, 1)`.

The `policy` parameter is accepted but not used inside this function. The comparison with `max_line_characters` is done by the caller.

**What it means in the pipeline:** this is the proof that a file claiming to be text really decodes as text, plus cheap statistics for the report. A single line of many megabytes is a sign of minified or machine-generated content and can make later line-based stages use far too much memory, which is why the longest line is measured.

```python
def _inspect_json(stream, suffix, encoding, size, policy):
    stream.seek(0)
    wrapper = io.TextIOWrapper(stream, encoding=encoding, errors='strict')
    def invalid_constant(value):
        raise ValueError(f'nonstandard JSON constant: {value}')
    try:
        if suffix == '.json':
            if size > policy['max_structured_bytes']:
                raise ValueError('JSON exceeds bounded structural validation limit')
            json.loads(wrapper.read(policy['max_structured_bytes'] + 1), parse_constant=invalid_constant)
        else:
            for line in wrapper:
                if line.strip():
                    json.loads(line, parse_constant=invalid_constant)
    finally:
        wrapper.detach()
```

`_inspect_json` checks that `.json`, `.jsonl` and `.ndjson` files really parse. It keeps nothing; a file passes if no exception is raised.

- `io.TextIOWrapper(stream, encoding=..., errors='strict')` wraps the byte stream so that reading from `wrapper` gives decoded text.
- `invalid_constant` is a function defined inside the function. Python's JSON parser accepts three words that are not legal JSON: `NaN`, `Infinity` and `-Infinity`. Passing `parse_constant=invalid_constant` makes the parser call this function when it meets one, and the function raises. So files are held to strict JSON.
- `.json`: the file must be no bigger than `max_structured_bytes`, because the whole document has to be in memory to parse it. `wrapper.read(n)` reads at most `n` characters; `json.loads` parses them.
- `.jsonl` / `.ndjson` (one JSON value per line): `for line in wrapper` reads one line at a time, and each line that is not blank is parsed on its own. Memory use is bounded by the longest line, which the caller has already checked.
- `finally: wrapper.detach()` separates the wrapper from the underlying stream. Without it, the wrapper would *close* the underlying temporary file when it is discarded, and the checks that run afterwards would find their file closed.

A `.json` file larger than `max_structured_bytes` is not rejected for being large; it raises `ValueError` and is quarantined, because the stage could not validate it within its memory bound.

```python
def add_check(result, check, **evidence):
    return replace(result, decision=more_restrictive_decision(result.decision, check.decision),
                   checks=result.checks + (check,), **evidence)
```

`add_check` is the one place where a verdict is combined. It returns a *copy* of `result` with three changes: the decision becomes the worse of the old decision and the new check's decision; the check is appended to `checks` (`+ (check,)` concatenates a one-element tuple — the comma makes it a tuple); and any extra keyword arguments (`**evidence`) overwrite fields of the same name, for example `is_symlink=True`. Since every check goes through this function, the "decisions only get worse" rule is enforced in one line.

```python
def inspect_artifact(batch_dir, artifact, policy, remaining_bytes, within_count=True):
    result = ArtifactInspectionResult(artifact['artifact_id'], artifact['original_filename'], artifact['stored_relative_path'])
    try:
        path = safe_artifact_path(batch_dir, artifact['stored_relative_path'])
        for component in (*reversed(path.absolute().parents), path):
            metadata = component.lstat()
            if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, 'st_file_attributes', 0) & 0x400:
                return add_check(result, CheckResult('filesystem', D.REJECTED, ('symlink/reparse point in artifact path',)), is_symlink=True)
        info = path.lstat()
        result = replace(result, size_bytes=info.st_size, is_symlink=stat.S_ISLNK(info.st_mode),
                         is_regular_file=stat.S_ISREG(info.st_mode))
        if result.is_symlink or not result.is_regular_file:
            return add_check(result, CheckResult('filesystem', D.REJECTED, ('symlink or non-regular file',)))
        if not within_count or info.st_size > policy['max_file_size_bytes'] or info.st_size > remaining_bytes:
            return add_check(result, CheckResult('limits', D.REJECTED, ('file or remaining batch resource limit exceeded',)))
```

`inspect_artifact` runs all per-file checks for one manifest entry. `artifact` is the manifest dict for that file, `remaining_bytes` is how much of the batch's byte budget is left, and `within_count` is `False` when this artifact's position in the manifest is beyond `max_files_per_batch`.

The whole body is inside `try:`. A check that finds a problem either returns early with `return add_check(...)` or raises; the three `except` clauses at the bottom turn any exception into a verdict. That is why this function never crashes on a bad file.

In order:

1. **Path string.** `safe_artifact_path` validates the manifest's `stored_relative_path` (explained above).
2. **Links anywhere in the path.** The loop walks every component from the filesystem root down to the file. `lstat()` is like `stat()` but describes a link itself instead of what it points to. `stat.S_ISLNK(mode)` is true for a symlink; `getattr(metadata, 'st_file_attributes', 0) & 0x400` is the Windows reparse-point test (`getattr` with a default returns 0 on systems where the attribute does not exist). Any link → check `filesystem`, `rejected`. Note that this walk starts at the root of the disk, so it also covers the directories *above* the project: if the project folder were ever placed under a symlinked directory, every artifact would be rejected here.
3. **Kind of object.** `path.lstat()` again, for the file itself. Its size and kind are recorded with `replace`. A directory, pipe or device is not a regular file → `filesystem`, `rejected`. (The `is_symlink` half of this test cannot be true at this point, because step 2 already returned for a symlink.)
4. **Limits.** Too many files in the batch, bigger than `max_file_size_bytes`, or bigger than what is left of the batch budget → check `limits`, `rejected`. This happens before the file is opened, so an oversized file is never read.

```python
        suffix = Path(result.filename).suffix.lower()
        stored_suffix = path.suffix.lower()
        if suffix in policy['blocked_extensions'] or stored_suffix in policy['blocked_extensions']:
            return add_check(result, CheckResult('extension', D.REJECTED, ('blocked extension',)))
        if suffix != stored_suffix:
            result = add_check(result, CheckResult('extension', D.QUARANTINED, ('stored/original extension mismatch',)))
        if suffix not in policy['allowed_extensions']:
            decision = D.REJECTED if policy['unknown_file_policy'] == 'reject' else D.QUARANTINED
            result = add_check(result, CheckResult('extension', decision, ('unsupported extension',)))
        elif suffix not in TEXT_EXTENSIONS | DEEP_EXTENSIONS:
            result = add_check(result, CheckResult('extension', D.QUARANTINED, ('inspection handler unavailable',)))
```

5. **Extension.** Two suffixes are taken, both lowercased: `suffix` from the original filename and `stored_suffix` from the stored path. (`Path("notes.TXT").suffix.lower()` is `".txt"`; a name without a dot gives `""`.)

| Situation | Check | Decision | Continues? |
|---|---|---|---|
| either suffix is in `blocked_extensions` | `extension` | `rejected` | no, returns |
| the two suffixes differ | `extension` | `quarantined` | yes |
| `suffix` not in `allowed_extensions` | `extension` | `quarantined`, or `rejected` if `unknown_file_policy` is `"reject"` | yes |
| allowed, but neither a text nor a deep extension | `extension` | `quarantined` ("inspection handler unavailable") | yes |

The last row is a safety net for a policy that allows an extension the code has no checker for. With the current `configs/inspection.json` it cannot trigger: all 24 allowed extensions are in `TEXT_EXTENSIONS` or `DEEP_EXTENSIONS`. `A | B` on two sets is their union.

A quarantined artifact keeps going through the remaining checks so that the report contains its hash, MIME type and so on. Only `rejected` returns early.

```python
        with open_regular(path) as source, tempfile.TemporaryFile() as stream:
            before = os.fstat(source.fileno())
            if (before.st_size, before.st_dev, before.st_ino) != (info.st_size, info.st_dev, info.st_ino):
                raise OSError('artifact changed while opening')
            result = add_check(result, CheckResult('filesystem'))
            if not info.st_size:
                return add_check(result, CheckResult('limits', D.QUARANTINED, ('empty file',)))
            # All content checks share the exact private snapshot that was hashed.
            result = replace(result, sha256=stream_hash(source, info.st_size, stream))
            integrity = ()
            if result.sha256 != artifact['sha256']:
                integrity += ('artifact sha256 mismatch',)
            if info.st_size != artifact['size_bytes']:
                integrity += ('artifact size mismatch',)
            result = add_check(result, CheckResult('integrity', D.QUARANTINED if integrity else D.ACCEPTED, integrity))
```

`with open_regular(path) as source, tempfile.TemporaryFile() as stream:` opens two things: the real artifact, safely, as `source`; and an anonymous temporary file as `stream`, which the operating system deletes when it is closed.

6. **Same file as measured.** `os.fstat(source.fileno())` describes the file that was actually opened. Its size, device number and inode number (`st_dev` + `st_ino` together identify one file on one disk) must equal those from the earlier `lstat`. If they differ, the file was swapped between the two calls → `OSError`. If they match, a passing `filesystem` check is recorded.
7. **Empty.** A zero-byte file → check `limits`, `quarantined`, return. It is never hashed, so its `sha256` stays `None`.
8. **Hash and private snapshot.** `stream_hash(source, info.st_size, stream)` reads the artifact once, hashing it and copying it into the temporary file at the same time.

   - **What Python does:** after this line, `stream` holds an exact copy of the bytes and `result.sha256` is the hash of exactly those bytes.
   - **What it means in the pipeline:** every later check (MIME, text, JSON, deep) reads `stream`, not `source`. If someone modified the incoming file while inspection was running, the checks would still all be judging the same bytes that the recorded hash describes. The verdict and the hash cannot refer to different content.
9. **Integrity.** The computed hash is compared with the manifest's `sha256`, and the size with the manifest's `size_bytes`. `integrity += ('...',)` appends a message to a tuple. Any mismatch → check `integrity`, `quarantined`; otherwise the check is recorded as passed. A mismatch means the stored file is not the file acquisition copied.

```python
            mime, method = _detect_mime(stream, policy)
            result = replace(result, detected_mime_type=mime, mime_detection_method=method)
            if mime in policy['blocked_mime_types']:
                return add_check(result, CheckResult('mime', D.REJECTED, ('blocked executable MIME type',)))
            mismatch = mime not in policy['expected_mime_types'].get(suffix, ())
            result = add_check(result, CheckResult('mime', D.QUARANTINED if mismatch else D.ACCEPTED,
                               ('content MIME unavailable or inconsistent with extension',) if mismatch else ()))
```

10. **MIME.** `_detect_mime(stream, policy)` runs on the snapshot. Then:

    - detected type is in `blocked_mime_types` → check `mime`, `rejected`, return. This catches an executable renamed to `story.txt`.
    - otherwise `policy['expected_mime_types'].get(suffix, ())` is the list of acceptable types for this extension (an empty tuple if the extension is unknown). If the detected type is not in it → `quarantined` with "content MIME unavailable or inconsistent with extension". This catches a PDF renamed to `.txt`, and also the case where detection returned `None`.

    An artifact with an unsupported extension always fails this comparison as well, because its extension has no expected list.

```python
            if suffix in TEXT_EXTENSIONS:
                stream.seek(0)
                encoding = detect_encoding(stream.read(4))
                result = replace(result, encoding=encoding)
                chars, lines, longest = inspect_text(stream, encoding, policy)
                result = replace(result, character_count=chars, line_count=lines, max_line_characters=longest)
                extreme = longest > policy['max_line_characters']
                result = add_check(result, CheckResult('text', D.QUARANTINED if extreme else D.ACCEPTED,
                                   ('maximum line length exceeded',) if extreme else ()))
                if suffix in {'.json', '.jsonl', '.ndjson'} and not extreme:
                    _inspect_json(stream, suffix, encoding, info.st_size, policy)
                    result = add_check(result, CheckResult('json_structure'))
```

11. **Text.** Only for `TEXT_EXTENSIONS`. The snapshot is rewound with `seek(0)`, its first four bytes choose the encoding, and `inspect_text` produces the three statistics, which are stored on the result. If the longest line exceeds `max_line_characters` → check `text`, `quarantined`; otherwise passed.

    If the bytes are not valid in the chosen encoding, or contain control characters, `inspect_text` raises, and the artifact is quarantined by the last `except` clause below; in that case no `text` check is recorded and the statistics stay `None`.
12. **JSON structure.** For the three JSON extensions, and only when the line-length check passed, `_inspect_json` parses the content. If it returns without raising, a passing `json_structure` check is recorded.

```python
            if suffix in DEEP_EXTENSIONS:
                check, flags = inspect_deep_container(stream, suffix, policy, result.encoding)
                result = add_check(result, check, flags=result.flags + flags)
            after = os.fstat(source.fileno())
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise OSError('artifact changed during inspection')
        return result
    except UnsafeContent as error:
        return add_check(result, CheckResult('content', D.REJECTED, (str(error),)))
    except OSError as error:
        decision = D.REJECTED if error.errno in (errno.ELOOP, errno.ENOTDIR) else D.QUARANTINED
        return add_check(result, CheckResult('filesystem', decision, (str(error),)))
    except (ValueError, UnicodeError, RecursionError, RuntimeError, zipfile.BadZipFile, zlib.error) as error:
        return add_check(result, CheckResult('content_or_filesystem', D.QUARANTINED, (str(error),)))
```

13. **Deep inspection.** For `DEEP_EXTENSIONS`, `inspect_deep_container` (next file) returns a `CheckResult` named `deep_inspection` and a tuple of flags, which are appended to the result. The detected text encoding is passed along for HTML.
14. **Unchanged during inspection.** `os.fstat` on the still-open source is compared with the one taken at the start: size, modification time and change time (the two times in nanoseconds). A difference → `OSError('artifact changed during inspection')`.

If nothing returned early or raised, the accumulated `result` is returned.

The three `except` clauses map exception types to verdicts:

| Exception | Check name recorded | Decision |
|---|---|---|
| `UnsafeContent` | `content` | `rejected` |
| `OSError` with error number `ELOOP` or `ENOTDIR` (a link was met while opening) | `filesystem` | `rejected` |
| any other `OSError` (missing file, permission denied, changed while opening, grew, changed during inspection) | `filesystem` | `quarantined` |
| `ValueError`, `UnicodeError`, `RecursionError`, `RuntimeError`, `zipfile.BadZipFile`, `zlib.error` | `content_or_filesystem` | `quarantined` |

Order matters: `UnsafeContent` is a subclass of `ValueError`, and Python uses the first matching clause, so it must be listed before the general `ValueError` clause. `RecursionError` is there because a JSON document nested thousands of levels deep makes the parser exceed Python's recursion limit. In every case `add_check(result, ...)` is applied to the result *as far as it had been filled in*, so evidence collected before the failure (size, hash, MIME) is kept.

```python
def _scan_snapshots(paths, policy):
    engines = [engine for name in ('clamdscan', 'clamscan') if (engine := shutil.which(name))]
    if not engines:
        return {path: MalwareScanResult(M.UNAVAILABLE, error='clamdscan and clamscan unavailable') for path in paths}
```

The malware check does not implement virus detection. It calls ClamAV, an open-source antivirus, if it is installed. ClamAV ships two command-line programs: `clamdscan`, which asks an already running background service to scan (fast), and `clamscan`, which loads the whole signature database itself each time (slow, but needs no service).

`_scan_snapshots(paths, policy)` takes a list of file paths and returns a dict from each path to a `MalwareScanResult`.

The first line is a list comprehension with a walrus: for each name, `shutil.which(name)` returns the full path of the program or `None`; `(engine := ...)` stores it and the `if` keeps only those found. If neither exists, every path gets the status `UNAVAILABLE`.

```python
    results = {}
    for engine in engines:
        pending = [path for path in paths if path not in results or results[path].status == M.ERROR]
        if not pending:
            break
        try:
            proc = subprocess.run([engine, '--no-summary', '--', *map(str, pending)], capture_output=True,
                                  text=True, errors='replace', timeout=policy['malware_timeout_seconds'], check=False)
            output = (proc.stdout + '\n' + proc.stderr).splitlines()
            for path in pending:
                verdicts = [line[len(str(path)) + 2:] for line in output if line.startswith(str(path) + ': ')]
                infected = [v[:-6] for v in verdicts if v.endswith(' FOUND')]
                if infected:
                    results[path] = MalwareScanResult(M.INFECTED, engine, infected[0])
                elif proc.returncode in (0, 1) and verdicts == ['OK']:
                    results[path] = MalwareScanResult(M.CLEAN, engine)
                else:
                    error = '; '.join(verdicts) or (proc.stderr.strip()[:500] or 'no per-file verdict')
                    results[path] = MalwareScanResult(M.ERROR, engine, error=f'exit {proc.returncode}: {error}')
        except (OSError, subprocess.TimeoutExpired) as error:
            for path in pending:
                results[path] = MalwareScanResult(M.ERROR, engine, error=str(error))
    return results
```

The loop tries the engines in order. `pending` is the list of paths that have no result yet or whose result is `ERROR`; the second engine is therefore only asked about files the first one could not judge.

`subprocess.run([engine, '--no-summary', '--', *paths], ...)` starts the scanner as a separate program and waits for it:

- The command is a *list*, not one string, and no shell is involved, so nothing in a path can be interpreted as a command.
- `--` is the conventional "end of options" marker: whatever follows is a file name even if it starts with `-`.
- `*map(str, pending)` unpacks all paths as separate arguments: one process scans the whole group.
- `capture_output=True, text=True, errors='replace'` collects what the scanner prints, as text, replacing undecodable bytes instead of failing.
- `timeout=...` kills the scanner after `malware_timeout_seconds` and raises `subprocess.TimeoutExpired`.
- `check=False`: a non-zero exit code is not an exception; the code inspects it itself.

ClamAV prints one line per file, `"<path>: OK"` or `"<path>: <SignatureName> FOUND"`. For each path, `verdicts` collects the text after `"<path>: "` from every line that starts with that path. `v[:-6]` removes the six characters of `" FOUND"`, leaving the signature name.

| Scanner output for this path | Result |
|---|---|
| at least one `... FOUND` line | `INFECTED`, with the first signature name |
| exactly one line, `OK`, and exit code 0 or 1 | `CLEAN` |
| anything else: no line, an error line, exit code 2 | `ERROR`, with the exit code and message |
| the process could not start or timed out | `ERROR` for every pending path |

Exit code 1 from ClamAV means "a virus was found somewhere in this run"; it is accepted for a file with an `OK` line because another file in the same group may be the infected one. The rule that matters is the third row: a file is only called clean when the scanner said so explicitly for that file.

```python
def scan_malware_batch(batch_dir, artifacts, policy):
    """Stage bounded, hash-verified snapshots so scanners cannot follow source links."""
    results = {}
    candidates = [a for a in artifacts if a.sha256 and a.decision != D.REJECTED]
    def chunks():
        chunk, size = [], 0
        for artifact in candidates:
            if chunk and (len(chunk) >= policy['malware_chunk_size']
                          or size + artifact.size_bytes > policy['max_malware_chunk_bytes']):
                yield chunk
                chunk, size = [], 0
            chunk.append(artifact)
            size += artifact.size_bytes
        if chunk:
            yield chunk
```

`scan_malware_batch` runs after every artifact has been through `inspect_artifact`. `candidates` are the artifacts that were hashed and are not already `rejected`; there is no reason to scan a file that is rejected anyway, and an unhashed file was never read. Those skipped artifacts keep the status `not_run`.

`chunks()` is a small generator function defined inside the function (generators: chapter 5). It hands out the candidates in groups. A group is closed, and a new one started, when it already holds `malware_chunk_size` files or when adding the next file would push its total size over `max_malware_chunk_bytes`. The `if chunk and (...)` guard means a group is never closed while empty, so a single large file still gets a group of its own.

```python
    for chunk in chunks():
        with tempfile.TemporaryDirectory(prefix='jsm-malware-') as directory:
            targets = {}
            for index, artifact in enumerate(chunk):
                snapshot = Path(directory).resolve() / f'{index:06d}{Path(artifact.filename).suffix.lower()}'
                try:
                    path = safe_artifact_path(batch_dir, artifact.stored_relative_path)
                    with open_regular(path) as source, snapshot.open('xb') as output:
                        digest = hashlib.sha256()
                        size = 0
                        while data := source.read(CHUNK):
                            size += len(data)
                            if size > artifact.size_bytes:
                                raise OSError('artifact changed before malware scan')
                            output.write(data)
                            digest.update(data)
                    if digest.hexdigest() != artifact.sha256:
                        raise OSError('artifact changed before malware scan')
                    targets[snapshot] = artifact.artifact_id
                except (OSError, ValueError) as error:
                    results[artifact.artifact_id] = MalwareScanResult(M.ERROR, error=str(error))
            for path, verdict in _scan_snapshots(list(targets), policy).items():
                results[targets[path]] = verdict
    return results
```

For each group a private temporary directory is created (`tempfile.TemporaryDirectory`, removed with everything in it when the `with` block ends). Each artifact is copied into it under a generated name: `f'{index:06d}...'` formats the position as six digits, followed by the lowercased original extension, giving names like `000000.txt`, `000001.pdf`. The scanner therefore never sees the uploader's file name or the incoming path, and cannot be led through a link.

The copy is made with the same care as before: validated path, `open_regular`, exclusive create (`'xb'`, see 4.1), hashing while copying. If the copy turns out longer than the recorded size, or its hash differs from the hash inspection recorded earlier, the file changed between the two steps and that artifact gets a malware status of `ERROR`. Otherwise `targets` remembers which snapshot belongs to which `artifact_id`.

`Path(directory).resolve()` converts the temporary directory to its real path with links resolved. Matching scanner output to files is done by comparing path text, so the code uses one fixed spelling of each path.

`_scan_snapshots(list(targets), policy)` scans the snapshots (a dict used as a list gives its keys), and the last two lines translate snapshot paths back to artifact ids. The function returns `{artifact_id: MalwareScanResult}`.

```python
def apply_malware_result(artifact, malware, policy):
    decision = D.ACCEPTED
    if malware.status == M.INFECTED:
        decision = D.REJECTED
    elif malware.status != M.CLEAN and policy['require_malware_scan']:
        decision = D.QUARANTINED
    errors = (malware.error or malware.signature or malware.status.value,) if decision != D.ACCEPTED else ()
    return add_check(artifact, CheckResult('malware', decision, errors),
                     malware_scan_status=malware.status, malware_engine=malware.engine,
                     malware_signature=malware.signature, malware_error=malware.error)
```

`apply_malware_result` converts a scanner verdict into a check:

| Scanner status | `require_malware_scan` | Decision of the `malware` check |
|---|---|---|
| `infected` | either | `rejected` |
| `clean` | either | `accepted_for_ingestion` |
| `unavailable`, `error`, `not_run` | `true` | `quarantined` |
| `unavailable`, `error`, `not_run` | `false` | `accepted_for_ingestion` |

`errors` is a one-element tuple holding the first non-empty of: the error text, the signature name, or the status word (`a or b or c` returns the first truthy value). The four `malware_*` fields are always copied onto the artifact, so even when the policy lets an unscanned file through, the report shows that it was *not* scanned.

`configs/inspection.json` currently sets `require_malware_scan` to `false`. With that setting an infected file is still rejected, but a file is not held back merely because no scan could be completed.

#### `src/corpus_factory/inspection/deep_inspection.py`

**Why this file exists** — Some formats can be dangerous or broken in ways that only show when you look at their internal structure: a `.docx` is a ZIP archive of XML files, a PDF can carry scripts, an HTML page can carry JavaScript. This file contains one bounded validator per format. "Bounded" is the key word: each one reads in fixed-size chunks and stops at a configured limit, so a hostile file cannot make it use unlimited memory, disk or time. Nothing is extracted to disk and no text is produced; text extraction is a later stage (4.5).

**What enters / what leaves** — The public entry point is `inspect_deep_container(stream, suffix, policy, encoding)`. `stream` is the private snapshot opened by `inspect_artifact`, `suffix` is the lowercased extension. It returns a pair: a `CheckResult` named `deep_inspection`, and a tuple of flag strings. It never raises for bad content. `bounded_zip`, `inspect_xml`, `CHUNK`, `ZIP_FORMATS`, `DEEP_EXTENSIONS` and `UnsafeContent` are also imported by `checks.py`. For PDFs only, a temporary copy is written to the system temporary directory and the external program `pdfinfo` is run on it.

**How it connects** — Called by `inspect_artifact` in `checks.py` as its second-to-last step. `bounded_zip` is also called earlier by `_detect_mime`.

**The code, section by section**

```python
"""Bounded static validation. No extraction, conversion, or network requests."""
import codecs
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import zipfile
import zlib
from html.parser import HTMLParser
from pathlib import PurePosixPath
from xml.parsers import expat

from src.corpus_factory.inspection.result import CheckResult, InspectionDecision as D
```

| Import | Why |
|---|---|
| `codecs` | incremental decoder for HTML |
| `re` | patterns for PDF names, RTF control words, URLs |
| `shutil` | `which` to find `pdfinfo`; `copyfileobj` to copy a stream |
| `stat` | interpret Unix mode bits stored inside ZIP entries |
| `struct` | unpack fixed binary layouts into numbers |
| `subprocess`, `tempfile` | run `pdfinfo` on a temporary copy |
| `zipfile` | the standard-library ZIP reader |
| `zlib` | only the exception type `zlib.error` (decompression failure) |
| `HTMLParser` | a tolerant, event-based HTML reader from the standard library |
| `PurePosixPath` | split archive member names on `/` without touching the disk |
| `expat` | a low-level, streaming XML parser |

```python
CHUNK = 64 * 1024
ZIP_FORMATS = {
    '.docx': ('word/document.xml', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
    '.xlsx': ('xl/workbook.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    '.pptx': ('ppt/presentation.xml', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'),
    '.odt': ('content.xml', 'application/vnd.oasis.opendocument.text'),
    '.ods': ('content.xml', 'application/vnd.oasis.opendocument.spreadsheet'),
    '.epub': ('META-INF/container.xml', 'application/epub+zip'),
}
DEEP_EXTENSIONS = set(ZIP_FORMATS) | {'.pdf', '.doc', '.rtf', '.xml', '.html', '.htm'}


class UnsafeContent(ValueError):
    """Definite policy violation, rather than uncertain/corrupt content."""
```

- `CHUNK = 64 * 1024` — 65,536 bytes, the read size used throughout the stage.
- `ZIP_FORMATS` maps each ZIP-based extension to a pair: the member that *must* exist inside a genuine file of that type, and the MIME type. A real `.docx` always contains `word/document.xml`; an EPUB always contains `META-INF/container.xml`.
- `DEEP_EXTENSIONS` — `set(ZIP_FORMATS)` is the set of that dict's keys; `|` unions it with the non-ZIP formats handled in this file.
- `UnsafeContent` is an exception class with no body of its own beyond a docstring. It inherits from `ValueError`. Its only purpose is to be *distinguishable*: throughout the stage, raising `UnsafeContent` means "this is a definite violation → `rejected`", while raising a plain `ValueError` means "this is broken or could not be verified → `quarantined`".

**Background: how a ZIP file is laid out, and what a zip bomb is.** A ZIP file stores each member (file) as a small header followed by its compressed data. At the *end* of the file sits the **central directory**: one entry per member with its name, compressed size, uncompressed size and position. After that comes a 22-byte **end-of-central-directory record** (optionally followed by a comment of up to 65,535 bytes) that says how many entries the directory has, how many bytes it occupies and where it starts. Readers start from that end record.

Compression is what makes archives dangerous. A few kilobytes of compressed data can expand to gigabytes when the original was, say, a long run of zeros (a *zip bomb*), and an archive can declare millions of entries so that merely listing it exhausts memory. The defence is to read the declared numbers first, compare them with limits, and only then let a parser work.

```python
def bounded_zip(stream, policy):
    """Bound the central directory before ZipFile allocates member objects."""
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(max(0, size - 65557))
    tail = stream.read(65557)
    index = tail.rfind(b'PK\x05\x06')
    if index < 0 or len(tail) - index < 22:
        raise ValueError('ZIP end record missing')
    _, disk, start_disk, count_disk, count, directory_bytes, offset, comment = struct.unpack_from('<4s4H2LH', tail, index)
    if disk or start_disk or count != count_disk or count == 65535 or offset == 0xffffffff:
        raise ValueError('multi-volume/ZIP64 container validation unavailable')
    if count > policy['max_archive_files'] or directory_bytes > policy['max_structured_bytes']:
        raise UnsafeContent('archive directory exceeds resource limits')
    if index + 22 + comment != len(tail) or offset + directory_bytes > size:
        raise ValueError('invalid ZIP end record')
    stream.seek(0)
    archive = zipfile.ZipFile(stream)
    if len(archive.infolist()) != count:
        archive.close()
        raise ValueError('inconsistent archive entry count')
    return archive
```

`bounded_zip` reads the end record by hand before handing the stream to `zipfile.ZipFile`.

- `stream.seek(0, 2)` moves to the end of the file (`2` means "relative to the end"); `stream.tell()` then gives the file size.
- `65557` is 22 + 65,535: the furthest from the end that the record can start. The code reads at most that many trailing bytes.
- `tail.rfind(b'PK\x05\x06')` searches backwards for the record's four-byte signature. Not found, or fewer than 22 bytes after it → `ValueError`.
- `struct.unpack_from('<4s4H2LH', tail, index)` decodes 22 bytes at that position.

  - **What Python does:** the format string describes a binary layout. `<` = little-endian (least significant byte first), `4s` = 4 raw bytes, `4H` = four unsigned 16-bit integers, `2L` = two unsigned 32-bit integers, `H` = one more 16-bit integer. That is 4 + 8 + 8 + 2 = 22 bytes, returned as eight Python values. `_` receives the signature and is ignored.
  - **What it means in the pipeline:** the program now knows `count` (number of entries), `directory_bytes` (size of the directory) and `offset` (where it starts), having read at most 64 KiB and allocated nothing.

Then four tests, in order:

| Test | Raises | Result for the artifact |
|---|---|---|
| archive spans several disks, the two entry counts disagree, or a field holds the special value (`65535`, `0xffffffff`) that means "real value is in the ZIP64 extension" | `ValueError` | quarantined: this code cannot validate such archives |
| `count > max_archive_files` or `directory_bytes > max_structured_bytes` | `UnsafeContent` | rejected |
| the record plus its comment does not end exactly at the end of the file, or the directory would extend past the file | `ValueError` | quarantined |
| after opening, `zipfile` finds a different number of entries than the record declared | `ValueError` | quarantined |

Only after the first three does `zipfile.ZipFile(stream)` run. It reads the central directory, not the member data. The function returns the open archive.

**Background: XML entity attacks.** XML lets a document define shortcuts called *entities* in a `<!DOCTYPE ...>` section. Two classic attacks use them. In the "billion laughs" attack, one entity is defined as ten copies of another, which is ten copies of another, and so on: a file of a few hundred bytes expands to gigabytes when parsed. In an *external entity* (XXE) attack, an entity is defined as the content of a local file or URL, and the parser fetches it. A corpus document never needs either feature, so the simplest safe rule is: no DOCTYPE and no entity declarations at all.

```python
def inspect_xml(stream, policy, relationships=False):
    """Expat handlers reject declarations before entity expansion; no tree retained."""
    parser = expat.ParserCreate(namespace_separator='}')
    depth = 0
    root = None

    def forbidden(*args):
        raise UnsafeContent('XML DTD/entity declarations are forbidden')

    def start(name, attrs):
        nonlocal depth, root
        depth += 1
        if root is None:
            root = name.rsplit('}', 1)[-1]
        if depth > policy['max_xml_depth']:
            raise UnsafeContent('XML nesting limit exceeded')
        if relationships and name.rsplit('}', 1)[-1] == 'Relationship':
            target = attrs.get('Target', '').strip()
            if (attrs.get('TargetMode', '').lower() == 'external'
                    or re.match(r'^(?:[a-zA-Z][\w+.-]*:|//|\\)', target)):
                raise UnsafeContent('external Office relationship')

    def end(name):
        nonlocal depth
        depth -= 1
```

`inspect_xml` validates an XML stream and returns the name of its root (outermost) element.

`expat` is an *event* parser: you give it callback functions and it calls them as it meets things in the input. It does not build a tree of the document in memory, so memory use stays flat regardless of file size. `ParserCreate(namespace_separator='}')` turns on namespace processing; element names then arrive as `<namespace-uri>}<local-name>`, and `name.rsplit('}', 1)[-1]` (split once from the right, take the last piece) recovers the plain local name such as `document`.

Three functions are defined inside `inspect_xml` so they can share its variables:

- `forbidden(*args)` accepts any arguments and always raises `UnsafeContent`.
- `start(name, attrs)` is called for each opening tag. `nonlocal depth, root` says these names refer to the variables of the enclosing function, so assigning to them here changes the outer ones. It increments the nesting depth, remembers the first element name as the root, and raises if the depth exceeds `max_xml_depth` (extremely deep nesting is another way to exhaust a parser).
- `end(name)` is called for each closing tag and decrements the depth.

The `relationships` part applies to Office files. Inside a `.docx` there are `.rels` files listing what each part links to. A relationship can point *outside* the document, for example to a template on a remote server that Word would download when the file is opened. With `relationships=True`, each `Relationship` element is checked: `TargetMode="External"` raises, and so does a `Target` matching this regular expression:

`^(?:[a-zA-Z][\w+.-]*:|//|\\)` — at the start of the string, one of: a URL scheme (a letter, then letters/digits/`+`/`.`/`-`, then a colon, as in `http:` or `file:`), or `//` (a network path), or a backslash (a Windows network path). `(?:...)` groups without capturing. Checked on examples: `media/image1.png` and `../word/x.xml` do not match; `http://x.y/a`, `//host/a`, `mailto:a@b` and `C:x` do.

```python
    parser.StartDoctypeDeclHandler = forbidden
    parser.EntityDeclHandler = forbidden
    parser.ExternalEntityRefHandler = forbidden
    parser.StartElementHandler = start
    parser.EndElementHandler = end
    total = 0
    while chunk := stream.read(CHUNK):
        total += len(chunk)
        if total > policy['max_structured_bytes']:
            raise ValueError('XML exceeds bounded structural validation limit')
        parser.Parse(chunk, False)
    parser.Parse(b'', True)
    return root
```

The callbacks are attached by assigning to attributes of the parser. `forbidden` is attached to three events: the start of a DOCTYPE declaration, an entity declaration, and a reference to an external entity. Since the DOCTYPE handler fires as soon as the declaration begins, the document is rejected *before* any entity inside it could be expanded.

The loop feeds the parser 64 KiB at a time. `parser.Parse(chunk, False)` means "more data follows"; `parser.Parse(b'', True)` means "that was the end", at which point expat reports unclosed tags. If the total passes `max_structured_bytes`, a plain `ValueError` is raised (quarantine: too big to validate, not proven harmful). XML that is not well-formed makes expat raise `expat.ExpatError`, which the caller also maps to quarantine.

The parser is given raw bytes, so it works out the document's encoding itself from the BOM or the XML declaration.

Real results from `inspect_deep_container` with suffix `.xml`:

| Input | Decision | Error |
|---|---|---|
| `<a><b>hello</b></a>` | accepted | |
| `<a><b>hello</a>` | quarantined | `mismatched tag: line 1, column 13` |
| `<!DOCTYPE a [<!ENTITY x "y">]><a>&x;</a>` | rejected | `XML DTD/entity declarations are forbidden` |

Because any DOCTYPE is refused, ordinary XML or XHTML files that merely declare a document type are rejected too.

```python
def _inspect_zip(stream, suffix, policy):
    with bounded_zip(stream, policy) as archive:
        entries = archive.infolist()
        names = set()
        total = 0
        for entry in entries:
            name = entry.filename
            parts = PurePosixPath(name).parts
            if ('\\' in name or name.startswith('/') or '..' in parts
                    or ':' in name or '\x00' in entry.orig_filename):
                raise UnsafeContent('unsafe archive member path')
            if name.casefold() in names:
                raise ValueError('duplicate archive member name')
            names.add(name.casefold())
            mode = entry.external_attr >> 16
            kind = stat.S_IFMT(mode)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise UnsafeContent('archive symlink or special file')
            if entry.flag_bits & 1:
                raise UnsafeContent('encrypted archive member')
            total += entry.file_size
            if (entry.file_size > policy['max_archive_member_bytes']
                    or total > policy['max_uncompressed_bytes']
                    or entry.file_size / max(1, entry.compress_size) > policy['max_compression_ratio']):
                raise UnsafeContent('archive expansion limit exceeded')
            lower = name.lower()
            if (PurePosixPath(lower).suffix in policy['blocked_extensions']
                    or 'vbaproject.bin' in lower or 'embeddings' in lower.split('/')):
                raise UnsafeContent('archive contains executable, macro, or embedded content')
```

`_inspect_zip` validates one of the six ZIP-based document formats. `with bounded_zip(...) as archive:` closes the archive at the end. The first loop looks only at the directory entries (`archive.infolist()` returns one `ZipInfo` object per member); nothing is decompressed yet.

| Test on each entry | Protects against | Raises |
|---|---|---|
| name contains a backslash or colon, starts with `/`, has a `..` part, or the raw name contains a zero byte | **path traversal** ("zip slip"): a member named `../../x` that a careless extractor would write outside its target folder | `UnsafeContent` |
| same name already seen, ignoring case (`casefold()` is a stronger `lower()`) | two members that would overwrite each other on a case-insensitive disk, or that make different tools read different content | `ValueError` |
| `entry.external_attr >> 16` is the Unix file mode stored in the entry (`>> 16` shifts the number right by 16 bits to keep the upper half). `stat.S_IFMT` extracts the file-type bits. Allowed: `0` (not recorded), regular file, directory | symlinks and device files inside the archive | `UnsafeContent` |
| `entry.flag_bits & 1` — bit 0 of the flags means the member is encrypted | content nobody can inspect | `UnsafeContent` |
| declared size of this member over `max_archive_member_bytes`; running `total` of declared sizes over `max_uncompressed_bytes`; `file_size / compress_size` over `max_compression_ratio` | **zip bombs** | `UnsafeContent` |
| member's extension is in `blocked_extensions`, or the name contains `vbaproject.bin`, or one of its folders is called `embeddings` | executables, Office macros (`vbaProject.bin` is where they are stored), and other files embedded inside a document | `UnsafeContent` |

`max(1, entry.compress_size)` avoids dividing by zero for an empty member.

```python
        required, mime = ZIP_FORMATS[suffix]
        if required not in archive.namelist():
            raise ValueError(f'required container member missing: {required}')
        if suffix in {'.docx', '.xlsx', '.pptx'}:
            if '[Content_Types].xml' not in archive.namelist() or '_rels/.rels' not in archive.namelist():
                raise ValueError('Office package metadata missing')
        else:
            if archive.getinfo('mimetype').file_size > 255 or archive.read('mimetype') != mime.encode('ascii'):
                raise ValueError('container mimetype mismatch')
```

Now the structure of the specific format. `required, mime = ZIP_FORMATS[suffix]` unpacks the pair for this extension.

- The required member must exist, otherwise the file is not what its extension says.
- Microsoft Office formats must also contain `[Content_Types].xml` and `_rels/.rels`, two bookkeeping files every genuine Office package has.
- The others (`.odt`, `.ods`, `.epub`) must contain a member named `mimetype` whose content is exactly the expected MIME string. `mime.encode('ascii')` converts the string to bytes for the comparison. The size is checked first (at most 255 bytes) so that `archive.read` cannot be tricked into decompressing something huge. If there is no such member, `archive.getinfo` raises `KeyError`, which `inspect_deep_container` treats as quarantine.

All failures here are `ValueError`: the file is malformed, not proven malicious.

```python
        # Read all members to EOF to validate CRC and decompression, including non-XML.
        for entry in entries:
            if entry.is_dir():
                continue
            with archive.open(entry) as member:
                if entry.filename.lower().endswith(('.xml', '.rels')):
                    root = inspect_xml(member, policy, relationships=entry.filename.endswith('.rels'))
                    expected_root = {'.docx': 'document', '.xlsx': 'workbook', '.pptx': 'presentation',
                                     '.odt': 'document-content', '.ods': 'document-content', '.epub': 'container'}
                    if entry.filename == required and root != expected_root[suffix]:
                        raise ValueError('unexpected document XML root')
                else:
                    seen = 0
                    while chunk := member.read(CHUNK):
                        seen += len(chunk)
                        if seen > policy['max_archive_member_bytes']:
                            raise UnsafeContent('expanded member exceeds limit')
```

The second loop actually reads every member to its end. The declared sizes checked above come from the archive's own directory and could be lies; reading is the only proof.

- **What Python does:** `archive.open(entry)` returns a stream that decompresses on the fly. Reading it to the end makes `zipfile` verify the member's CRC-32 checksum and raises `zipfile.BadZipFile` or `zlib.error` if the data is damaged.
- **What it means in the pipeline:** a document that passes here will not fail with a decompression error when the extraction stage opens it.

Members ending in `.xml` or `.rels` go through `inspect_xml`, with the relationship check switched on for `.rels` files. `str.endswith` accepts a tuple of alternatives. For the required member only, the root element must be the expected one from the `expected_root` table (`document` for `.docx`, `workbook` for `.xlsx`, and so on). All other members (images, fonts) are read in chunks and counted; `seen` going over `max_archive_member_bytes` raises, which guards against a member that expands to more than its header declared.

```python
class _HTMLInspection(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'iframe', 'object', 'embed', 'applet', 'base'}:
            raise UnsafeContent(f'active HTML element: {tag}')
        for name, value in attrs:
            compact = re.sub(r'\s+', '', value or '').lower()
            if name.startswith('on') or name == 'srcdoc' or compact.startswith(('javascript:', 'vbscript:', 'data:')):
                raise UnsafeContent('active HTML attribute')
        if tag == 'meta' and any(k == 'http-equiv' and (v or '').lower() == 'refresh' for k, v in attrs):
            raise UnsafeContent('HTML redirect')
```

`HTMLParser` is another event parser, built for HTML, which is far less strict than XML. You use it by writing a subclass and overriding methods. `_HTMLInspection` overrides `handle_starttag`, which the parser calls for every opening tag with the tag name (already lowercased) and a list of `(attribute name, value)` pairs.

The aim is to refuse *active* HTML: anything that runs code, loads another document, or redirects.

| Rule | Example that is rejected |
|---|---|
| tag is `script`, `iframe`, `object`, `embed`, `applet` or `base` | `<script>...</script>` |
| attribute name starts with `on` (event handlers) | `<p onclick="x()">` |
| attribute is `srcdoc` (an inline document for an iframe) | `<iframe srcdoc="...">` |
| attribute value, with all whitespace removed and lowercased, starts with `javascript:`, `vbscript:` or `data:` | `<a href="java script:...">`, `<img src="data:...">` |
| `<meta http-equiv="refresh">` | automatic redirect |

`re.sub(r'\s+', '', value or '')` deletes every run of whitespace; `value or ''` copes with attributes that have no value (`None`). Whitespace is removed because browsers ignore tabs and newlines inside a URL scheme, a known way of hiding `javascript:`. In the last rule `any(... for k, v in attrs)` is a generator expression that unpacks each pair.

Ordinary links (`<a href="https://...">`) and stylesheets are not affected, and nothing is ever fetched.

```python
def _inspect_html(stream, encoding, policy):
    parser = _HTMLInspection(convert_charrefs=True)
    decoder = codecs.getincrementaldecoder(encoding or 'utf-8-sig')()
    while chunk := stream.read(CHUNK):
        parser.feed(decoder.decode(chunk))
        if len(parser.rawdata) > policy['max_line_characters']:
            raise ValueError('HTML token exceeds structural limit')
    parser.feed(decoder.decode(b'', final=True))
    parser.close()
```

`_inspect_html` drives that parser. `convert_charrefs=True` makes the parser translate character references such as `&amp;` itself. The decoder uses the encoding found by the text check, or `utf-8-sig` if none was passed. Each chunk of bytes is decoded and fed in.

`parser.rawdata` is the parser's internal buffer of input it has not finished processing. Normally it stays small. If it grows beyond `max_line_characters`, some single token (for example a tag that never closes) is enormous → `ValueError`, quarantine. The last two lines flush the decoder and tell the parser the input has ended.

Real results: `<p>hello</p>` is accepted; `<p onclick="x()">hi</p>` is rejected with `active HTML attribute`.

```python
def _inspect_pdf(stream, policy):
    if stream.read(5) != b'%PDF-':
        raise ValueError('PDF signature missing')
    stream.seek(0)
    tail = b''
    active = re.compile(rb'/(?:JavaScript|JS|Launch|EmbeddedFile|OpenAction|AA)(?=[\s()<>\[\]{}/%])')
    while chunk := stream.read(CHUNK):
        data = tail + chunk
        decoded = re.sub(rb'#([0-9a-fA-F]{2})', lambda m: bytes([int(m[1], 16)]), data)
        if active.search(decoded):
            raise UnsafeContent('PDF active-content marker')
        tail = data[-1024:]
    decoded_tail = re.sub(rb'#([0-9a-fA-F]{2})', lambda m: bytes([int(m[1], 16)]), tail)
    if active.search(decoded_tail + b' '):
        raise UnsafeContent('PDF active-content marker')
    if b'%%EOF' not in tail or b'startxref' not in tail:
        raise ValueError('PDF trailer missing')
```

**Background: what is inside a PDF.** A PDF is a series of numbered objects. Dictionaries inside them use *names*, which start with a slash: `/Type`, `/Pages`. A handful of names make a PDF do things rather than show things:

| Name | Meaning |
|---|---|
| `/JavaScript`, `/JS` | embedded script |
| `/Launch` | start an external program |
| `/EmbeddedFile` | a file attached inside the PDF |
| `/OpenAction` | something to do automatically when the document is opened |
| `/AA` | "additional actions" triggered by events |

`_inspect_pdf` does a static scan of the raw bytes for those names.

- The first five bytes must be `%PDF-`.
- `active` is a compiled regular expression over *bytes* (`rb'...'`). `/(?:JavaScript|JS|...)` matches a slash followed by one of the names. `(?=[\s()<>\[\]{}/%])` is a *lookahead*: the next byte must be whitespace or a PDF delimiter, but it is not consumed. This is what stops `/JS` from matching inside a longer harmless name.
- PDF allows any character in a name to be written as `#` plus two hex digits, so `/J#61vaScript` is the same name as `/JavaScript`. The `re.sub` line undoes that: for each `#xx` it calls the small `lambda` function, which turns the two hex digits (`m[1]`) into the single byte they stand for. The search runs on this decoded copy.
- `tail` keeps the last 1024 bytes of what has been seen and is glued in front of the next chunk (`data = tail + chunk`), so a name cut in half by a chunk boundary is still found.
- After the loop, the tail is searched once more with a space appended, so a name that is the very last thing in the file (with no delimiter after it) is caught.
- A well-formed PDF ends with `startxref`, a number, and `%%EOF`. Both markers must appear in the final 1024 bytes; otherwise the file is truncated or not a real PDF → `ValueError`.

A marker hit is `UnsafeContent` → `rejected`. Two limits of this approach, both visible in the code: it looks at bytes as stored, so a name inside a *compressed* object is not seen; and it rejects on the name alone, so a PDF whose `/OpenAction` only says "open at page 1" is rejected like one that runs a script.

```python
    validator = shutil.which('pdfinfo')
    if validator is None:
        if policy['require_deep_container_inspection']:
            raise ValueError('pdfinfo unavailable; PDF structure not validated')
        return ('pdf_validator_unavailable',)
    # Validators receive a private snapshot, never a mutable incoming pathname.
    with tempfile.TemporaryDirectory(prefix='jsm-pdf-') as directory:
        from pathlib import Path
        snapshot = Path(directory) / 'document.pdf'
        stream.seek(0)
        with snapshot.open('wb') as output:
            shutil.copyfileobj(stream, output, CHUNK)
        result = subprocess.run([validator, str(snapshot)], capture_output=True,
                                timeout=policy['pdf_timeout_seconds'], check=False)
        if result.returncode:
            raise ValueError('pdfinfo rejected PDF: ' + result.stderr[:500].decode('utf-8', 'replace'))
        if re.search(rb'^Encrypted:\s+yes', result.stdout, re.MULTILINE):
            raise UnsafeContent('encrypted PDF')
    return ()
```

The second half asks an external tool whether the PDF is structurally sound. `pdfinfo` is a small program from the Poppler PDF toolkit that parses a PDF and prints its properties. `shutil.which('pdfinfo')` finds it on the `PATH` or returns `None`.

If it is not installed, `require_deep_container_inspection` decides:

| `require_deep_container_inspection` | Outcome |
|---|---|
| `true` | `ValueError` → the PDF is quarantined |
| `false` | the function returns the flag `('pdf_validator_unavailable',)`; the static checks above still applied, and the PDF can be accepted with that flag in its record |

This is the only place the stage reads that key. `configs/inspection.json` currently sets it to `false`.

If the tool is present, the snapshot is copied into a fresh private temporary directory as `document.pdf` (`shutil.copyfileobj` copies stream to stream in chunks) and `pdfinfo` is run on that copy with a time limit of `pdf_timeout_seconds`. The comment states the reason: the external program is given a private copy under a neutral name, never the path of the incoming file. `from pathlib import Path` appears here, inside the function, because the top of the file imports only `PurePosixPath`.

- A non-zero exit code → `ValueError` carrying the first 500 bytes of the tool's error output, decoded with `'replace'` so undecodable bytes cannot cause a second failure → quarantine.
- `re.search(rb'^Encrypted:\s+yes', result.stdout, re.MULTILINE)`: `pdfinfo` prints a line `Encrypted:      yes` for password-protected files. `re.MULTILINE` makes `^` match at the start of every line. → `UnsafeContent`, `rejected`.
- A timeout raises `subprocess.TimeoutExpired`, which the caller maps to quarantine.

Success returns the empty tuple `()`: no flags.

```python
def _inspect_rtf(stream):
    if not stream.read(5).lower().startswith(b'{\\rtf'):
        raise ValueError('RTF signature missing')
    stream.seek(0)
    depth = 0
    escaped = False
    tail = b''
    while chunk := stream.read(CHUNK):
        data = tail + chunk
        if re.search(rb'\\(?:object|objdata|field|bin)\b', data, re.IGNORECASE):
            raise UnsafeContent('RTF embedded/active/binary content')
        tail = data[-64:]
        for byte in chunk:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 123:
                depth += 1
            elif byte == 125:
                depth -= 1
                if depth < 0:
                    raise ValueError('unbalanced RTF braces')
    if depth or escaped:
        raise ValueError('unbalanced RTF structure')
```

**Background: RTF.** Rich Text Format is plain bytes made of three things: *groups* wrapped in braces `{ ... }` that may nest, *control words* that start with a backslash (`\b` for bold, `\par` for paragraph), and text. A backslash before a brace (`\{`) means a literal brace, not a group.

`_inspect_rtf` does two things in one pass over the file.

**Screening for control words.** The regular expression `\\(?:object|objdata|field|bin)\b`, case-insensitive, looks for a backslash followed by one of four words: `\object` and `\objdata` introduce embedded objects, `\field` introduces computed fields (hyperlinks, page numbers, and historically a route for exploits), `\bin` introduces raw binary data. The trailing `\b` is a *word boundary*: the next character must not be a letter, digit or underscore. A match → `UnsafeContent`, `rejected`. A 64-byte `tail` is carried between chunks for words split across a boundary.

Because of that word boundary, the pattern matches `\bin` followed by a space but not `\bin` followed directly by a digit. Checked: `{\rtf1 {\field x}}` is rejected, while `{\rtf1 \bin4 abcd}` is accepted.

**Brace balance.** Iterating over a `bytes` object yields integers, so `for byte in chunk` gives numbers: 92 is `\`, 123 is `{`, 125 is `}`. The small state machine: after a backslash, the next byte is skipped (`escaped`); `{` raises the depth; `}` lowers it; going below zero means a closing brace without an opener. At the end, a non-zero depth or a dangling backslash means the file is truncated or malformed → `ValueError`, quarantine.

```python
def inspect_deep_container(stream, suffix, policy, encoding=None):
    flags = ()
    try:
        stream.seek(0)
        if suffix in ZIP_FORMATS:
            _inspect_zip(stream, suffix, policy)
        elif suffix == '.pdf':
            flags = _inspect_pdf(stream, policy)
        elif suffix == '.xml':
            inspect_xml(stream, policy)
        elif suffix in {'.html', '.htm'}:
            _inspect_html(stream, encoding, policy)
        elif suffix == '.rtf':
            _inspect_rtf(stream)
        elif suffix == '.doc':
            raise ValueError('legacy DOC: safe cross-platform validator unavailable')
        return CheckResult('deep_inspection'), flags
    except UnsafeContent as error:
        return CheckResult('deep_inspection', D.REJECTED, (str(error),)), flags
    except (OSError, ValueError, KeyError, RuntimeError, EOFError, NotImplementedError,
            zipfile.BadZipFile, zlib.error, expat.ExpatError, subprocess.TimeoutExpired) as error:
        return CheckResult('deep_inspection', D.QUARANTINED, (str(error),)), flags
```

`inspect_deep_container` is the dispatcher. It rewinds the snapshot and calls the validator for the extension. Its two `except` clauses apply the convention of this file:

| What happened | Returned check |
|---|---|
| validator returned normally | `CheckResult('deep_inspection')` — passed |
| `UnsafeContent` | `deep_inspection`, `rejected`, with the message |
| any exception in the long list: I/O errors, `ValueError`, `KeyError` (missing archive member), `RuntimeError`, `EOFError` (truncated data), `NotImplementedError` (a compression method `zipfile` does not support), `BadZipFile`, `zlib.error`, `ExpatError`, `TimeoutExpired` | `deep_inspection`, `quarantined`, with the message |

`flags` is only ever non-empty for PDFs.

The `.doc` branch is unconditional: legacy Word files are a complex binary format, the code has no validator for them, and so it raises `ValueError` every time. `.doc` is in `allowed_extensions`, so the practical result is that every `.doc` file is quarantined with `legacy DOC: safe cross-platform validator unavailable`.

#### `src/corpus_factory/inspection/inspector.py`

**Why this file exists** — It is the orchestrator: one function that takes a batch directory and returns the complete `InspectionResult`, calling the checks in the right order.

**What enters / what leaves** — `inspect_batch(batch_dir, policy=None)` takes the batch directory and optionally a policy dict. It returns an `InspectionResult`. It writes nothing to `storage/`.

**How it connects** — Called by `scripts/inspection.py` once per batch. Its return value is passed to `write_inspection_report` and `quarantine_batch`.

**The code, section by section**

```python
"""Batch trust gate and artifact-level orchestration."""
from copy import deepcopy
from pathlib import Path

from src.corpus_factory.inspection.checks import (
    apply_malware_result, inspect_artifact, read_manifest, scan_malware_batch,
)
from src.corpus_factory.inspection.config import load_inspection_config, validate_inspection_config
from src.corpus_factory.inspection.result import CheckResult, InspectionDecision as D, InspectionResult
```

`deepcopy` makes a fully independent copy of a nested structure (a dict containing lists containing strings...). The other imports are the functions explained in the previous sections.

```python
def inspect_batch(batch_dir: Path, policy: dict | None = None) -> InspectionResult:
    policy = deepcopy(load_inspection_config() if policy is None else validate_inspection_config(policy))
    batch_dir = Path(batch_dir).absolute()
    try:
        manifest, digest = read_manifest(batch_dir, policy)
    except (OSError, ValueError, UnicodeError, RecursionError) as error:
        return InspectionResult(batch_dir.name, None, policy,
                                checks=(CheckResult('manifest', D.QUARANTINED, (str(error),)),))
```

`policy = deepcopy(A if policy is None else B)` is a conditional expression. With no policy given, the default file is loaded; with one given, it is validated again. Either way the function works on its own deep copy: the policy stored in the result is a snapshot that later changes to the caller's dict cannot alter.

`Path(batch_dir).absolute()` makes the path absolute without following links.

**The batch trust gate.** `read_manifest` is called inside `try`. If it raises (file missing or a symlink, too large, checksum mismatch, not valid JSON, wrong shape, JSON nested too deeply) the function returns immediately with a result that has:

- `source_manifest_sha256` = `None`,
- no artifacts at all,
- one batch-level check, `manifest`, `quarantined`, carrying the error message.

That makes `batch_valid` false. No object file in the batch is opened: a batch whose manifest cannot be trusted is not inspected file by file, because there is no reliable list of what the files are supposed to be.

```python
    artifacts = []
    remaining = policy['max_batch_size_bytes']
    for index, artifact in enumerate(manifest['artifacts']):
        result = inspect_artifact(batch_dir, artifact, policy, remaining,
                                  within_count=index < policy['max_files_per_batch'])
        artifacts.append(result)
        # Only bytes actually read consume the inspection budget. An oversized
        # rejected object cannot deprive later small artifacts of their budget.
        if result.sha256:
            remaining -= result.size_bytes
    malware = scan_malware_batch(batch_dir, artifacts, policy)
    artifacts = tuple(apply_malware_result(a, malware[a.artifact_id], policy)
                      if a.artifact_id in malware else a for a in artifacts)
    return InspectionResult(batch_dir.name, digest, policy, artifacts,
                            (CheckResult('manifest'),))
```

With a trusted manifest, each artifact is inspected in manifest order. `enumerate` yields `(index, artifact)` starting at 0, so `index < policy['max_files_per_batch']` is true for the first N artifacts and false afterwards; the ones beyond the limit are rejected individually by the `limits` check.

`remaining` is the batch byte budget. It starts at `max_batch_size_bytes` and is reduced only when `result.sha256` is set, which means the file was actually read. As the comment says, a file rejected for being too large was never read and therefore does not use up budget that later, smaller files need.

After all artifacts, `scan_malware_batch` returns verdicts keyed by artifact id. The generator expression inside `tuple(...)` is a conditional applied per artifact: if a verdict exists, replace the artifact with the version that has the malware check applied; otherwise keep it as it is (its malware status stays `not_run`).

The final `InspectionResult` carries the batch name, the manifest hash, the policy snapshot, the artifacts, and one passing batch-level check `manifest`.

The complete order of checks for one batch, with the name each records:

| # | Check name | Fails as |
|---|---|---|
| 0 | `manifest` (batch) | whole batch quarantined |
| 1 | `content` (unsafe stored path) | rejected |
| 2 | `filesystem` (links, kind of object, swapped file) | rejected / quarantined |
| 3 | `limits` (count, size, budget; empty file) | rejected; empty → quarantined |
| 4 | `extension` | rejected / quarantined |
| 5 | `integrity` (hash and size against manifest) | quarantined |
| 6 | `mime` | rejected / quarantined |
| 7 | `text` | quarantined |
| 8 | `json_structure` | quarantined (recorded as `content_or_filesystem`) |
| 9 | `deep_inspection` | rejected / quarantined |
| 10 | `malware` | rejected / quarantined |

#### `src/corpus_factory/inspection/report.py`

This file is presented before `quarantine.py` because `quarantine.py` uses its `publish_record` function.

**Why this file exists** — It turns an `InspectionResult` into a permanent, checksummed JSON record, and it answers the question "which batches have already been inspected under the current rules?".

**What enters / what leaves**

| Function | Takes | Writes / returns |
|---|---|---|
| `utc_now()` | nothing | current UTC time as text, e.g. `2026-01-01T12:00:00.000000Z` |
| `publish_record(root, record_id, filename, record)` | a dict | creates `root/record_id/filename` and `filename.sha256`; returns the path of the JSON file |
| `write_inspection_report(batch_dir, result, catalog_dir)` | an `InspectionResult` | creates `storage/catalog/inspections/inspection_<...>/manifest.json` + checksum; returns its path |
| `completed_batches(policy, catalog_dir, quarantine_dir)` | the current policy | reads existing reports; returns a set of batch directory paths (strings) |

**How it connects** — `scripts/inspection.py` calls `completed_batches` to choose pending batches, then `write_inspection_report` after each `inspect_batch`. The provenance and ingestion scripts later read the `manifest.json` files written here.

**The code, section by section**

```python
"""Append-only, atomic publication of checksummed inspection records."""
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from paths import STORAGE_DIR, QUARANTINE_DIR
from src.corpus_factory.inspection.result import InspectionResult

INSPECTOR_VERSION = '2.0.0'
INSPECTIONS_DIR = STORAGE_DIR / 'catalog' / 'inspections'
```

- `hashlib`, `json`, `os`, `shutil`, `tempfile` — hashing, JSON, `fsync`/`rename`, removing a directory tree, creating a temporary directory.
- `asdict` — converts a dataclass instance into a plain dict, recursively (dataclasses nested inside become dicts too).
- `datetime`, `timezone` — current time in UTC.
- `uuid4` — generates a random 128-bit identifier; two calls never produce the same value in practice.
- `INSPECTOR_VERSION` — a version string stamped into every report.
- `INSPECTIONS_DIR` — `storage/catalog/inspections`. `paths.py` defines the same location under the name `INSPECTIONS_CATALOG_DIR`, which other stages use; this file builds its own copy of the path.

```python
def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
```

`datetime.now(timezone.utc).isoformat()` gives text ending in `+00:00`; the `replace` swaps that for the shorter, equivalent `Z`.

```python
def publish_record(root: Path, record_id: str, filename: str, record: dict) -> Path:
    """Publish both files together; historical nonempty directories cannot be replaced."""
    root.mkdir(parents=True, exist_ok=True)
    destination = root / record_id
    if destination.exists():
        raise FileExistsError(destination)
    temporary = Path(tempfile.mkdtemp(prefix='.pending-', dir=root))
    try:
        data = (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        for name, payload in ((filename, data), (filename + '.sha256', (hashlib.sha256(data).hexdigest() + '\n').encode('ascii'))):
            with (temporary / name).open('xb') as output:
                output.write(payload)
                output.flush()
                os.fsync(output.fileno())
        os.rename(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination / filename
```

`publish_record` writes a JSON file and its checksum so that they appear together, completely, or not at all.

**The problem it solves.** If a program writes a file directly at its final location and is interrupted halfway, a half-written file is left behind that looks like a real record. The standard cure is: write everything somewhere temporary, force it onto the disk, then move it into place with a single rename. A rename within one filesystem is *atomic*: other programs see either the old state or the new state, never something in between.

Step by step:

1. `root.mkdir(parents=True, exist_ok=True)` makes sure the parent folder exists.
2. `destination = root / record_id`. If it already exists, `FileExistsError` is raised: records are append-only, an existing one is never overwritten.
3. `tempfile.mkdtemp(prefix='.pending-', dir=root)` creates a uniquely named directory such as `.pending-ab12cd` *inside `root`*. Being in the same folder guarantees it is on the same filesystem as the destination, which a rename requires.
4. `json.dumps(record, ensure_ascii=False, indent=2)` serialises the dict as indented JSON, keeping non-ASCII characters such as Arabic letters as themselves instead of `\uXXXX` escapes. A newline is added and the text is encoded to UTF-8 bytes. The hash is computed from exactly those bytes.
5. The `for` loop iterates over two `(name, payload)` pairs: the JSON file, and the checksum file whose content is the hex digest plus a newline. Each is opened with `'xb'` (exclusive create, binary; see 4.1) and written.
6. `output.flush()` pushes Python's buffer to the operating system; `os.fsync(output.fileno())` tells the operating system to push its own buffer to the physical disk.
7. `os.rename(temporary, destination)` moves the whole directory to its final name in one step.
8. `finally:` runs whether or not an error occurred. If the temporary directory still exists, the rename did not happen, so it is deleted (`shutil.rmtree` removes a directory and its contents).

- **What Python does:** two files are created in a hidden staging directory, synced, and the directory is renamed.
- **What it means in the pipeline:** a directory named `inspection_...` in the catalog is always complete. If the process is killed mid-way, at worst a `.pending-...` directory is left, and no reader looks at those because they do not match `inspection_*`.

```python
def write_inspection_report(batch_dir: Path, result: InspectionResult,
                            catalog_dir: Path = INSPECTIONS_DIR) -> Path:
    inspection_id = 'inspection_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '_' + uuid4().hex
    artifacts = [{**asdict(a), 'errors': list(a.errors)} for a in result.artifacts]
    record = {
        'schema_version': '2.0.0', 'record_type': 'inspection_report',
        'inspection_id': inspection_id, 'inspector_version': INSPECTOR_VERSION,
        'created_at': utc_now(), 'batch_id': result.batch_id,
        'incoming_batch': str(Path(batch_dir).absolute()),
        'source_manifest_sha256': result.source_manifest_sha256,
        'batch_status': 'valid' if result.batch_valid else 'quarantined',
        'policy': result.policy, 'summary': result.summary,
        'checks': [asdict(c) for c in result.checks], 'errors': list(result.errors),
        'artifacts': artifacts, 'duplicate_groups': result.duplicate_groups,
        'next_stage': 'ingestion' if result.batch_valid and result.summary['accepted'] else 'quarantine',
        'eligible_artifact_ids': [a.artifact_id for a in result.artifacts if a.decision.value == 'accepted_for_ingestion'],
    }
    return publish_record(catalog_dir, inspection_id, 'manifest.json', record)
```

`write_inspection_report` builds the record.

- `inspection_id` is `inspection_` + a UTC timestamp with microseconds (`%f`) + `_` + 32 random hex characters. The timestamp makes ids sort by time; the random part makes collisions practically impossible. Every run gets a new id, so re-inspecting a batch adds a record and never replaces one.
- `artifacts`: for each artifact, `asdict(a)` produces a dict of all its *fields*. `errors` is a property, not a field, so `asdict` does not include it; `{**asdict(a), 'errors': list(a.errors)}` copies the dict and adds it explicitly.
- Enum members inside the record are written by `json.dumps` as their string values, and tuples as JSON lists.

The record has this shape (all values made up, most artifact fields left out):

```json
{
  "schema_version": "2.0.0",
  "record_type": "inspection_report",
  "inspection_id": "inspection_20260101T120000000000Z_<32 hex>",
  "inspector_version": "2.0.0",
  "created_at": "2026-01-01T12:00:00.000000Z",
  "batch_id": "my-source-20260101T115900Z-ab12cd34",
  "incoming_batch": "<absolute path of the batch directory>",
  "source_manifest_sha256": "<64 hex>",
  "batch_status": "valid",
  "policy": { "...": "the full policy in force" },
  "summary": { "total_artifacts": 2, "total_bytes": 26, "accepted": 1, "quarantined": 1, "rejected": 0 },
  "checks": [ { "name": "manifest", "decision": "accepted_for_ingestion", "errors": [] } ],
  "errors": [],
  "artifacts": [
    {
      "artifact_id": "artifact_00000001",
      "filename": "notes.txt",
      "stored_relative_path": "objects/00000001-notes.txt",
      "decision": "accepted_for_ingestion",
      "size_bytes": 13,
      "sha256": "<64 hex>",
      "detected_mime_type": "text/plain",
      "encoding": "utf-8",
      "line_count": 1,
      "malware_scan_status": "clean",
      "flags": [],
      "checks": [ { "name": "filesystem", "decision": "accepted_for_ingestion", "errors": [] } ],
      "errors": []
    }
  ],
  "duplicate_groups": [],
  "next_stage": "ingestion",
  "eligible_artifact_ids": ["artifact_00000001"]
}
```

Three derived fields:

| Field | Rule |
|---|---|
| `batch_status` | `"valid"` if the manifest was trusted, else `"quarantined"` |
| `next_stage` | `"ingestion"` if the batch is valid **and** at least one artifact was accepted (`result.summary['accepted']` is a count; 0 is falsy), else `"quarantine"` |
| `eligible_artifact_ids` | ids of the artifacts whose decision is `accepted_for_ingestion` |

So a batch with one accepted and one quarantined file is `valid`, goes on to `ingestion`, and lists one eligible id. `incoming_batch` stores the absolute path of the batch directory on the machine that ran the inspection.

The record is published as `manifest.json` under `storage/catalog/inspections/<inspection_id>/`, and the function returns that file's path. The script takes the id back out of it with `report.parent.name`.

```python
def completed_batches(policy, catalog_dir: Path = INSPECTIONS_DIR,
                      quarantine_dir: Path = QUARANTINE_DIR):
    """Legacy batch-local reports never satisfy the current inspection contract."""
    completed = set()
    for path in catalog_dir.glob('inspection_*/manifest.json'):
        try:
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != path.with_suffix('.json.sha256').read_text().strip():
                continue
            record = json.loads(data)
            if not isinstance(record, dict):
                continue
            if (record.get('schema_version') == '2.0.0' and record.get('inspector_version') == INSPECTOR_VERSION
                    and record.get('policy') == policy):
                if record['inspection_id'] != path.parent.name:
                    continue
                if record['errors'] or record['summary']['quarantined'] or record['summary']['rejected']:
                    reference = quarantine_dir / record['batch_id'] / record['inspection_id'] / 'quarantine.json'
                    reference_bytes = reference.read_bytes()
                    if hashlib.sha256(reference_bytes).hexdigest() != reference.with_suffix('.json.sha256').read_text().strip():
                        continue
                completed.add(record['incoming_batch'])
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return completed
```

`completed_batches` decides which batches do **not** need inspecting again. It returns a set of batch directory paths; the script inspects every batch whose path is not in the set.

`catalog_dir.glob('inspection_*/manifest.json')` finds every report. Each one counts only if all of the following hold; otherwise `continue` skips to the next report:

1. **The report is intact.** The SHA-256 of its bytes equals the content of its `.sha256` file. `path.with_suffix('.json.sha256')` replaces the final `.json` of `manifest.json`, giving `manifest.json.sha256`. `.strip()` removes the newline.
2. It parses as a JSON object.
3. **Same rules.** `schema_version` is `2.0.0`, `inspector_version` equals the current `INSPECTOR_VERSION`, and the `policy` stored in the report is equal to the policy in force now. Dict equality compares every key and value.
4. The `inspection_id` inside the file equals the name of its directory.
5. **If anything was not accepted** (batch errors, or a non-zero quarantined or rejected count), the matching quarantine record must exist at `storage/quarantine/<batch_id>/<inspection_id>/quarantine.json` and pass its own checksum.

Only then is `record['incoming_batch']` added to the set. The `except` clause covers a missing file (`OSError`), bad JSON (`ValueError`), and a missing or wrongly typed field (`KeyError`, `TypeError`): any of those simply means "this report does not count".

Consequences worth understanding:

- Changing *any* value in `configs/inspection.json` makes every stored policy differ from the current one, so every batch becomes pending again and the next plain run re-inspects all of them. That is deliberate: a verdict is only valid for the rules that produced it.
- If the process stops after writing the report but before writing the quarantine record, rule 5 fails and the batch is inspected again on the next run.
- The comparison is on the absolute path text stored in `incoming_batch`. If the project folder is moved or renamed, the stored paths no longer match and every batch counts as pending.

The docstring's "legacy batch-local reports" refers to an older layout that kept an inspection file inside the batch directory; this function only looks in the catalog, so such files are ignored.

#### `src/corpus_factory/inspection/quarantine.py`

**Why this file exists** — When a batch or some of its artifacts were not accepted, it writes a short, separate record listing exactly those items and why. It is an index of problems, kept apart from the main catalog.

**What enters / what leaves** — `quarantine_batch(batch_dir, result, inspection_id, quarantine_dir)` returns the path of the written `quarantine.json`, or `None` if there was nothing to record. It writes `storage/quarantine/<batch_id>/<inspection_id>/quarantine.json` and `quarantine.json.sha256`. It does not copy, move or delete any incoming file.

**How it connects** — Called by `scripts/inspection.py` right after `write_inspection_report`, with that report's id. `completed_batches` in `report.py` later checks that this record exists. No other pipeline stage in `src/` or `scripts/` reads the quarantine records; the admin part of the serving backend refers to the directory.

**The code, section by section**

```python
"""Quarantine holds control references, never copies or moves incoming objects."""
from pathlib import Path

from paths import QUARANTINE_DIR
from src.corpus_factory.inspection.report import publish_record, utc_now
from src.corpus_factory.inspection.result import InspectionDecision as D, InspectionResult
```

`QUARANTINE_DIR` is `storage/quarantine` from `paths.py`. `publish_record` and `utc_now` are reused from `report.py`, so quarantine records get the same atomic, checksummed publication.

```python
def quarantine_batch(batch_dir: Path, result: InspectionResult, inspection_id: str,
                     quarantine_dir: Path = QUARANTINE_DIR) -> Path | None:
    references = [
        {'batch_id': result.batch_id, 'artifact_id': a.artifact_id,
         'decision': a.decision, 'reason': a.errors,
         'inspection_id': inspection_id,
         'source_reference': str(Path(batch_dir).absolute() / a.stored_relative_path)}
        for a in result.artifacts if a.decision != D.ACCEPTED
    ]
    if not references and result.batch_valid:
        return None
    record = {
        'schema_version': '2.0.0', 'record_type': 'quarantine_record',
        'inspection_id': inspection_id, 'batch_id': result.batch_id,
        'created_at': utc_now(), 'incoming_batch': str(Path(batch_dir).absolute()),
        'batch_errors': result.errors, 'artifacts': references,
    }
    return publish_record(quarantine_dir / result.batch_id, inspection_id, 'quarantine.json', record)
```

`references` is a list comprehension with a filter: one small dict for each artifact whose decision is *not* accepted. Each holds the batch id, the artifact id, the decision, the reasons (`a.errors`, every error message from every check), the inspection id, and `source_reference`: the absolute path where the file still sits in the incoming batch.

`if not references and result.batch_valid: return None` — a fully accepted batch with a trusted manifest produces no quarantine record and no directory.

Otherwise the record is built and published. For a batch whose manifest failed, `artifacts` is an empty list and `batch_errors` carries the manifest error. The shape (made-up values):

```json
{
  "schema_version": "2.0.0",
  "record_type": "quarantine_record",
  "inspection_id": "inspection_20260101T120000000000Z_<32 hex>",
  "batch_id": "my-source-20260101T115900Z-ab12cd34",
  "created_at": "2026-01-01T12:00:00.100000Z",
  "incoming_batch": "<absolute path of the batch directory>",
  "batch_errors": [],
  "artifacts": [
    {
      "batch_id": "my-source-20260101T115900Z-ab12cd34",
      "artifact_id": "artifact_00000002",
      "decision": "quarantined",
      "reason": ["content MIME unavailable or inconsistent with extension"],
      "inspection_id": "inspection_20260101T120000000000Z_<32 hex>",
      "source_reference": "<absolute path>/objects/00000002-report.pdf"
    }
  ]
}
```

`publish_record(quarantine_dir / result.batch_id, inspection_id, 'quarantine.json', record)` uses the batch id as the parent folder and the inspection id as the record folder. Since each inspection has a new id, re-inspecting a batch adds another folder beside the earlier ones.

**What it means in the pipeline:** "quarantined" and "rejected" are both statements in records, not actions on files. The incoming batch stays byte-for-byte as acquisition left it. What keeps a bad file out of the corpus is that later stages consult the inspection report and only take artifacts marked `accepted_for_ingestion`.

#### What I should understand before moving on

- Inspection reads the incoming batch and writes records about it. It never changes, moves or deletes an incoming file; "quarantine" is a JSON record pointing at the file.
- There are three decisions on an ordered scale, and `add_check` only ever moves an artifact toward the more severe end.
- `UnsafeContent` means a definite violation and leads to `rejected`; other errors mean "broken or could not be verified" and lead to `quarantined`.
- A manifest problem quarantines the whole batch before any file is opened; a file problem affects only that artifact.
- The file name is never trusted: the type is derived from the first bytes of the content and then compared with what the extension is allowed to contain.
- Each artifact is read once into a private snapshot while being hashed, and all content checks run on that snapshot, so the recorded hash and the verdict describe the same bytes.
- The deep validators read declared sizes and counts first, compare them with limits, and parse in fixed-size chunks without building the document in memory.
- Reports are published by writing into a temporary directory, syncing, and renaming; a batch counts as done only for the exact policy and inspector version that produced its report.

#### Self-test

1. An artifact passes the filesystem, limits, extension and integrity checks, is quarantined by the MIME check, and then passes the text check. What is its final decision, and which line of code guarantees that?
2. Someone renames a Windows program to `poem.txt` and uploads it. Which check stops it, what does that check look at, and is the result `quarantined` or `rejected`?
3. Why does `inspect_artifact` copy the file into a temporary file instead of running each check directly on the incoming file?
4. A `.docx` contains a member whose directory entry declares 10 bytes compressed and 50,000 bytes uncompressed, with `max_compression_ratio` at 200. What happens, and why is this tested before any member is decompressed?
5. `source.json` was edited by hand after acquisition to fix a typo in a filename. What does the next inspection run do with that batch, and how many of its files are opened?
6. You change `max_line_characters` in `configs/inspection.json` and run `python -m scripts.inspection` with no arguments. Which batches are inspected, and why?
7. Why does `publish_record` create its temporary directory inside the destination's parent folder rather than in the system temporary directory?
8. With the current policy (`require_malware_scan` is `false`), what happens to an artifact when (a) no scanner is installed, (b) the scanner reports an infection?

<details><summary>Answers</summary>

1. `quarantined`. `add_check` computes the new decision with `more_restrictive_decision(result.decision, check.decision)`, which returns the more severe of the two, so the passing text check cannot lower it.
2. The MIME check. `_detect_mime` reads the first bytes of the content, finds the `MZ` signature and returns `application/x-dosexec`, which is in `blocked_mime_types`; the artifact is `rejected` and the function returns at once. The extension `.txt` played no part in the detection.
3. So that every check judges exactly the bytes that were hashed. The source is read once, hashed and copied in the same pass; if the incoming file were changed during inspection, checks reading it directly could see different content from what the recorded SHA-256 describes.
4. The ratio is 50,000 / 10 = 5,000, above 200, so `_inspect_zip` raises `UnsafeContent` ("archive expansion limit exceeded") and the artifact is `rejected`. The test uses only the numbers in the central directory; doing it first means the program never starts expanding data that is declared to be a bomb.
5. The SHA-256 of the edited `source.json` no longer equals the content of `source.json.sha256`, so `read_manifest` raises, `inspect_batch` returns a result with a `quarantined` `manifest` check and no artifacts, and the report has `batch_status` `quarantined`. None of the object files are opened.
6. All of them. `completed_batches` counts a report only if its stored `policy` equals the current policy; after the change no stored policy matches, so no batch is in the completed set and each one gets a new inspection record.
7. `os.rename` is only atomic, and only possible as a simple rename, within one filesystem. A directory created inside the same parent folder is guaranteed to be on the same filesystem as the destination.
8. (a) The malware status is recorded as `unavailable`, but the `malware` check's decision is `accepted_for_ingestion`, so the artifact keeps whatever decision the earlier checks gave it. (b) The status is `infected` and the check is `rejected` regardless of the setting.

</details>

---

### 4.3 Provenance

| | |
|---|---|
| **INPUT** | A batch id, the batch's `source.json` written by acquisition (`storage/incoming/batches/<batch-id>/source.json`), and any decision records already stored under `storage/catalog/provenance/`. The inspection catalog (`storage/catalog/inspections/`) is used by the driving scripts only to find out which batch ids exist. |
| **PROCESS** | A person records a decision for a batch: `allowed`, `denied` or `review_required`, with a written reason. Later, the gate looks up the newest valid decision for a batch and answers one question: may this batch be used for training? |
| **OUTPUT** | Writing a decision: a new folder `storage/catalog/provenance/provenance_<time>_<random>/` containing `manifest.json` and `manifest.json.sha256`. Asking the gate: a small in-memory object, `RightsDecision(allowed, status, reason)`. The gate writes nothing. |
| **WHY IT EXISTS** | Inspection answers "is this file safe to open?". It does not answer "am I allowed to train a model on it?". That second question cannot be answered by a program, so the pipeline stops and waits for a human to say yes, and keeps the answer on disk as evidence. |

**Provenance** means "where something came from". For training data it covers two things: the origin of the text (who wrote it, where you got it) and the rights attached to it (licence, permission, privacy). A language model can reproduce pieces of what it was trained on, and you cannot remove one document from a trained model afterwards except by training again. So the cheapest moment to refuse a document is before it enters the corpus. A **rights gate** is that refusal point: a step that lets a batch through only when there is a recorded "yes".

In this project the default is "no". Acquisition writes every `source.json` with `"training_use": "review_required"` in its `license` block (4.1). Nothing downstream can turn that into a "yes" except a decision record written by `src/corpus_factory/provenance/decision.py`.

The stage has two source files and two driving scripts:

| File | Lines | Role |
|---|---|---|
| `src/corpus_factory/provenance/decision.py` | 86 | Writes one decision record to disk. |
| `src/corpus_factory/provenance/gate.py` | 134 | Reads decision records and answers allowed / not allowed. |
| `scripts/provenance_review.py` | 25 | `python -m scripts.provenance_review <batch-id> <allowed\|denied\|review_required> <basis>` — records a manual decision by calling `write_rights_decision`. |
| `scripts/provenance.py` | 75 | `python -m scripts.provenance` — a report. For every inspection manifest it prints `ALLOW:` or `BLOCK:` with the gate's reason. It writes nothing. |

Both scripts are shown in chapter 12. Two facts about the flow are worth knowing now, because the stage name can mislead:

- Running `scripts.provenance` does not "do" the provenance stage. It only prints what the gate currently thinks. The folder `storage/catalog/provenance/` only ever receives files from `scripts.provenance_review`.
- The gate is enforced inside the next stage. `scripts/ingestion.py` calls `evaluate_training_rights` itself for every batch and skips the batch when the answer is not allowed (4.4). You could never run `scripts.provenance` and the pipeline would behave the same.

**What the gate takes from inspection.** Less than you might expect. Inspection leaves one record per inspection run in `storage/catalog/inspections/inspection_<time>_<random>/manifest.json` (written by `write_inspection_report` in `src/corpus_factory/inspection/report.py`). That record contains, among other keys, `batch_id`, `incoming_batch` (the batch folder as a path string), `batch_status`, `next_stage`, and `artifacts` — one entry per file with `artifact_id`, `stored_relative_path`, `sha256` and `decision`. The scripts read `batch_id` (or the last part of `incoming_batch`) from those records to know which batches to ask about. The gate functions themselves never open an inspection record: they receive a batch id and the contents of `source.json`, and they read the provenance catalog. Whether a batch passed inspection is checked separately, by ingestion, file by file.

At the time of writing the provenance catalog holds 2 decision records, and all 8 batches under `storage/incoming/batches/` carry `training_use: review_required` in their `source.json`.

#### `src/corpus_factory/provenance/decision.py`

**Why this file exists** — To turn a human judgement ("this batch may be used for training because …") into a permanent, checksummed record on disk that the gate can find later.

**What enters / what leaves** — Enters: `batch_id` (text), `training_use` (one of three words), `basis` (free text: the reason). Leaves: the `Path` of the new `manifest.json`. Written: a new directory under `storage/catalog/provenance/` with two files, `manifest.json` and `manifest.json.sha256`. Nothing is read from disk.

**How it connects** — Called only by `scripts/provenance_review.py`. Its output is read by `find_latest_provenance_decision` in `gate.py`.

**The code, section by section**

```python
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from paths import PROVENANCE_CATALOG_DIR
```

- `hashlib` — Python's standard hashing module; used for the SHA-256 checksum of the manifest (hashing is taught in 4.1).
- `json` — turns a Python dictionary into JSON text.
- `uuid` — makes random identifiers; used for the random tail of the decision id.
- `datetime`, `timezone` — the current time in UTC, for the id and the `created_at` field.
- `Path` — only used here as the return type hint.
- `PROVENANCE_CATALOG_DIR` — defined in `paths.py` as `storage/catalog/provenance`.

```python
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
```

Returns the current time as text. `datetime.now(timezone.utc)` is "now" in UTC, not in your local time zone. `.isoformat()` formats it as, for example, `2026-01-02T03:04:05.123456+00:00`. `.replace("+00:00", "Z")` swaps the UTC offset for the shorter, equivalent letter `Z`. A real example with a fixed time: `2026-01-02T03:04:05+00:00` becomes `2026-01-02T03:04:05Z`.

The same helper is defined again in `ingestion/ingest.py` and in `inspection/report.py`; each stage carries its own copy.

```python
def write_rights_decision(
    batch_id: str,
    training_use: str,
    basis: str,
) -> Path:

    if training_use not in {
        "allowed",
        "denied",
        "review_required",
    }:
        raise ValueError(
            f"Invalid training_use: {training_use}"
        )
```

The one function of the file. Its three parameters are the three things a reviewer supplies.

The first statement is a guard. `{ "allowed", "denied", "review_required" }` is a set literal, and `not in` asks whether the given word is missing from it. Any other spelling (`"yes"`, `"Allowed"`, `"allow"`) raises `ValueError` and nothing is written. This matters because the gate later compares the stored word with `==`; a typo stored on disk would silently behave as "not allowed".

Notice what is not checked: `batch_id` is not compared with the batches that exist. You can record a decision for a batch id that was never acquired; the record will simply never match anything.

```python
    now = datetime.now(timezone.utc)

    decision_id = (
        f"provenance_{now:%Y%m%dT%H%M%SZ}_"
        f"{uuid.uuid4().hex[:8]}"
    )
```

Builds the name of the record.

- `{now:%Y%m%dT%H%M%SZ}` is an f-string with a format specification after the colon. For a `datetime`, the specification is a date pattern: `%Y` four-digit year, `%m` month, `%d` day, a literal `T`, `%H%M%S` hours, minutes and seconds, a literal `Z`. For 2 January 2026, 03:04:05 UTC it produces `20260102T030405Z`.
- `uuid.uuid4()` creates a random 128-bit identifier. `.hex` is its 32 hexadecimal characters; `[:8]` keeps the first 8.
- Two adjacent f-strings inside parentheses are joined into one string by Python.

The result looks like `provenance_20260102T030405Z_abcd1234`. The timestamp makes the folder names sort by time when you list them; the random tail keeps two decisions made in the same second from colliding.

```python
    decision_dir = (
        PROVENANCE_CATALOG_DIR / decision_id
    )

    decision_dir.mkdir(
        parents=True,
        exist_ok=False,
    )
```

`decision_dir` is `storage/catalog/provenance/<decision_id>`.

**What Python does** — `mkdir(parents=True, ...)` creates the folder and any missing parent folders. `exist_ok=False` makes it raise `FileExistsError` if the folder is already there.

**What it means in the pipeline** — A decision record is never overwritten. Changing your mind does not edit the old record; it adds a new one, and the gate picks the newest. The catalog is therefore a history: you can see that a batch was `review_required` on one day and `allowed` on another.

```python
    manifest = {
        "schema_version": "1.0.0",
        "record_type": "provenance_decision",
        "decision_id": decision_id,
        "batch_id": batch_id,
        "created_at": utc_now(),
        "training_use": training_use,
        "basis": basis,
        "review_method": "manual",
        "next_stage": (
            "ingestion"
            if training_use == "allowed"
            else None
        ),
    }
```

The decision record itself, as a dictionary with nine keys:

| Key | Value | Meaning |
|---|---|---|
| `schema_version` | `"1.0.0"` | Version of this record layout. |
| `record_type` | `"provenance_decision"` | Says what kind of JSON file this is. |
| `decision_id` | the id built above | Same as the folder name. |
| `batch_id` | the argument | Which batch the decision is about. |
| `created_at` | `utc_now()` | When the decision was recorded. The gate sorts by this. |
| `training_use` | `allowed` / `denied` / `review_required` | The decision. |
| `basis` | the argument | The reviewer's reason, free text. |
| `review_method` | always `"manual"` | Fixed text: there is no automatic reviewer. |
| `next_stage` | `"ingestion"` or `None` | A hint for a reader of the file. |

`"ingestion" if training_use == "allowed" else None` is a conditional expression: it evaluates to the first value when the condition is true, otherwise to the value after `else`. `None` becomes `null` in JSON.

`created_at` calls `utc_now()` a second time, a few microseconds after `now` was taken for the id. The two timestamps are not the same object, but they differ only by that tiny amount.

Nothing in the code reads `schema_version`, `record_type`, `decision_id`, `review_method` or `next_stage` back. The gate uses only `batch_id`, `created_at`, `training_use` and `basis`.

```python
    manifest_path = decision_dir / "manifest.json"

    encoded = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    manifest_path.write_bytes(encoded)
```

Turns the dictionary into bytes and writes them.

- `json.dumps(manifest, ...)` returns the JSON as a Python string.
- `ensure_ascii=False` keeps non-ASCII characters as themselves. A basis written in Arabic is stored as Arabic letters, not as `مر…` escapes.
- `indent=2` puts each key on its own line, indented by two spaces, so a person can read the file.
- `sort_keys=True` writes keys in alphabetical order, so the same dictionary always produces the same text.
- `+ "\n"` ends the file with a newline.
- `.encode("utf-8")` converts the string to bytes (bytes versus text is taught in chapter 6).
- `write_bytes(encoded)` writes exactly those bytes.

The bytes are built first and kept in the variable `encoded` because the next lines hash the very same bytes.

```python
    digest = hashlib.sha256(encoded).hexdigest()

    checksum_path = (
        decision_dir / "manifest.json.sha256"
    )

    checksum_path.write_text(
        f"{digest}  manifest.json\n",
        encoding="utf-8",
    )

    return manifest_path
```

**What Python does** — `hashlib.sha256(encoded).hexdigest()` computes the SHA-256 of the manifest bytes as 64 hexadecimal characters. The checksum file gets one line: the digest, two spaces, the file name. That is the layout the command-line tool `shasum -a 256` prints, so you can check a record by hand with `shasum -a 256 -c manifest.json.sha256` inside its folder.

**What it means in the pipeline** — The checksum lets the gate detect a decision record that was edited after it was written. If someone opens `manifest.json` and changes `"denied"` to `"allowed"`, the bytes no longer match the digest and the gate ignores the record (see `_verify_manifest` below). This is a guard against accidents and casual edits, not against a determined person, who could recompute the checksum file too.

This write is not atomic in the sense of 4.1/4.2: the manifest is written directly, then the checksum. If the program stopped between the two, the folder would hold a manifest without a checksum, and the gate would treat it as invalid and skip it — the failure is on the safe side.

The function returns the manifest path, which `scripts/provenance_review.py` prints.

#### `src/corpus_factory/provenance/gate.py`

**Why this file exists** — To answer "may batch X be used for training?" from the records on disk, in one place, so that every caller gets the same answer.

**What enters / what leaves** — `evaluate_training_rights(source_manifest, batch_id)` takes the parsed `source.json` of the batch (a dictionary) and the batch id. It reads every `storage/catalog/provenance/*/manifest.json` and its `.sha256` neighbour. It returns a `RightsDecision`. It writes nothing.

**How it connects** — Called by `scripts/provenance.py` (to print a report) and by `scripts/ingestion.py` (to decide whether to ingest a batch). It reads what `decision.py` wrote.

**The code, section by section**

```python
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from paths import PROVENANCE_CATALOG_DIR
```

`hashlib` to recompute a checksum, `json` to parse the manifests, `dataclass` for the small result class, `Path` for type hints, and the provenance catalog path from `paths.py`.

```python
@dataclass(frozen=True)
class RightsDecision:
    allowed: bool
    status: str
    reason: str
```

The answer the gate gives. `@dataclass` (primer in chapter 1) generates the constructor from the three annotated fields. `frozen=True` makes instances read-only: assigning `decision.allowed = True` after creation raises `FrozenInstanceError`. A gate answer should not be changeable by the code that receives it.

- `allowed` — the only field callers branch on. `True` means "go ahead".
- `status` — a word describing the state: `allowed`, `denied`, `review_required`.
- `reason` — a sentence for a human, printed by the scripts.

```python
def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()
```

Computes the SHA-256 of a file by reading it in pieces of `1024 * 1024` bytes (1 MiB). The pattern — open in binary mode, loop with the walrus operator `:=` until `read` returns empty bytes, feed each piece to `digest.update` — is explained in full in 4.1. The leading underscore in the name is a Python convention for "internal helper, not meant to be imported elsewhere".

A decision manifest is a few hundred bytes, so the loop runs once here; the chunked form costs nothing and would also work for a large file.

```python
def _verify_manifest(manifest_path: Path) -> bool:
    checksum_path = manifest_path.with_suffix(
        manifest_path.suffix + ".sha256"
    )

    if not checksum_path.is_file():
        return False
```

Checks one decision record against its checksum file. Returns `True` only when they agree.

`manifest_path.suffix` is `".json"`. `with_suffix(".json.sha256")` replaces the last suffix of the path with that longer one, so `…/manifest.json` becomes `…/manifest.json.sha256`. If that file does not exist, the record is not trusted.

```python
    expected = (
        checksum_path
        .read_text(encoding="utf-8")
        .strip()
        .split()[0]
    )

    actual = _sha256_file(manifest_path)

    return expected == actual
```

A chain of four calls, read top to bottom: read the checksum file as text; `.strip()` removes the trailing newline; `.split()` with no argument splits on any run of whitespace, giving `['<digest>', 'manifest.json']`; `[0]` takes the digest. `actual` is the digest of the manifest as it is on disk right now. The record is valid when the two strings are equal.

If the checksum file exists but is empty, `.split()` returns an empty list and `[0]` raises `IndexError`. Nothing catches it, so the calling script would stop with a traceback.

```python
def find_latest_provenance_decision(
    batch_id: str,
) -> dict | None:

    if not PROVENANCE_CATALOG_DIR.exists():
        return None

    decisions = []
```

Finds the newest valid decision for one batch. The return type `dict | None` means "a dictionary, or `None` when there is no decision". If the catalog folder has never been created, there is certainly no decision.

```python
    for manifest_path in PROVENANCE_CATALOG_DIR.glob(
        "*/manifest.json"
    ):
        if not _verify_manifest(manifest_path):
            continue

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        if manifest.get("batch_id") == batch_id:
            decisions.append(manifest)
```

`glob("*/manifest.json")` yields every `manifest.json` that sits exactly one folder below the catalog — one per decision record. For each:

1. `_verify_manifest` — if the checksum is missing or wrong, `continue` jumps to the next record. A tampered or half-written record is treated as if it did not exist; no message is printed.
2. `json.loads(...)` parses the file into a dictionary.
3. `manifest.get("batch_id")` reads the key, giving `None` instead of an error if the key is absent. Records for other batches are ignored.

Every call re-reads and re-hashes every record in the catalog. With 2 records that is instant; it grows linearly with the number of decisions ever written.

```python
    if not decisions:
        return None

    decisions.sort(
        key=lambda item: item.get("created_at", "")
    )

    return decisions[-1]
```

No matching record → `None`. Otherwise the list is sorted by `created_at` and the last element (`[-1]`) is returned.

**What Python does** — `key=lambda item: item.get("created_at", "")` tells `sort` to compare the records by their `created_at` text. A `lambda` is a small unnamed function; this one takes a record and returns its timestamp, or an empty string if the key is missing. The timestamps are strings, so the comparison is alphabetical.

**What it means in the pipeline** — "Latest wins". Because the timestamps are written in one fixed layout, year first, alphabetical order is time order, and the last element is the most recent decision. This is what makes a review reversible: record `denied` after `allowed` and the batch is blocked again from then on. It does not undo an ingestion that already happened.

```python
def evaluate_training_rights(
    source_manifest: dict,
    batch_id: str,
) -> RightsDecision:

    provenance = find_latest_provenance_decision(
        batch_id
    )
```

The gate itself. `source_manifest` is the parsed `source.json` of the batch; `batch_id` identifies it. The first step is to look for an explicit decision.

```python
    # Explicit provenance decision takes priority
    if provenance is not None:
        training_use = provenance.get(
            "training_use",
            "review_required",
        )

        basis = provenance.get(
            "basis",
            "unspecified",
        )
```

When a decision record exists, its `training_use` and `basis` are read. The second argument of `.get` is the fallback for a missing key: a record without `training_use` counts as `review_required`, the cautious choice.

```python
        if training_use == "allowed":
            return RightsDecision(
                allowed=True,
                status="allowed",
                reason=f"approved by provenance: {basis}",
            )

        if training_use == "denied":
            return RightsDecision(
                allowed=False,
                status="denied",
                reason=f"denied by provenance: {basis}",
            )

        return RightsDecision(
            allowed=False,
            status="review_required",
            reason=f"provenance review required: {basis}",
        )
```

Three outcomes. This first `return` is the only place in the whole file where `allowed=True` is produced. `denied` gives a refusal with its reason. Anything else — `review_required` or any unexpected word — falls through to the last `return` and is also a refusal. Each `return` ends the function, so no `elif` is needed.

```python
    # No provenance decision yet
    license_info = source_manifest.get(
        "license",
        {}
    )

    training_use = license_info.get(
        "training_use",
        "review_required",
    )

    return RightsDecision(
        allowed=False,
        status=training_use,
        reason=f"training use status: {training_use}",
    )
```

Reached only when no decision record exists for the batch. The code reads the `license` block that acquisition put in `source.json` and takes its `training_use`, defaulting to `review_required`. Then it returns `allowed=False` in every case, and uses the word it found only as the `status` and in the `reason`.

That last point is easy to misread, so here is real output from calling the function for a batch id that has no decision record:

```
evaluate_training_rights({}, "no-such-batch-xyz")
→ RightsDecision(allowed=False, status='review_required', reason='training use status: review_required')

evaluate_training_rights({"license": {"training_use": "allowed"}}, "no-such-batch-xyz")
→ RightsDecision(allowed=False, status='allowed', reason='training use status: allowed')
```

Even a `source.json` that says `training_use: allowed` does not open the gate: the result has `status='allowed'` but `allowed=False`. Callers test `allowed`, so the batch is blocked. The complete decision table is:

| Newest valid decision record for the batch | `source.json` `license.training_use` | `allowed` | `reason` begins |
|---|---|---|---|
| `allowed` | anything | `True` | `approved by provenance:` |
| `denied` | anything | `False` | `denied by provenance:` |
| `review_required` or any other word | anything | `False` | `provenance review required:` |
| none | anything, or missing | `False` | `training use status:` |

So the rule of the whole stage is one line: **a batch is used for training only if its most recent valid decision record says `allowed`.**

### 4.4 Ingestion

| | |
|---|---|
| **INPUT** | For each batch: the newest inspection record in `storage/catalog/inspections/`, the batch's `source.json`, the gate's answer from 4.3, and the files under `storage/incoming/batches/<batch-id>/objects/`. |
| **PROCESS** | For every batch the gate allows, copy each file that inspection marked `accepted_for_ingestion` into raw storage under a new document id, then write a manifest listing the copies and a checksum of that manifest. |
| **OUTPUT** | `storage/raw/<batch-id>/objects/<document_id>-<stored file name>` (one per accepted file), `storage/raw/<batch-id>/manifest.json`, `storage/raw/<batch-id>/manifest.json.sha256`. |
| **WHY IT EXISTS** | `storage/incoming` holds everything that was uploaded, including files that were rejected, quarantined or not cleared for training. `storage/raw` holds only what passed both gates. Every later stage reads from `raw` and can therefore assume "safe and permitted" without re-checking. |

**Ingestion** is the admission step. It does not change a single byte of any file; it copies. What it adds is identity: each admitted file becomes a **document** with a **document id** of its own, and from this point on the pipeline talks about documents, not uploads.

Three identifiers are now in play, and it helps to keep them apart:

| Identifier | Made by | Example shape | Names |
|---|---|---|---|
| batch id | acquisition (4.1) | `<source>-<time>-…` | one upload session: a folder of files plus `source.json` |
| artifact id | acquisition (4.1) | text inside `source.json` | one file inside a batch, as received |
| document id | ingestion | `doc_` + 32 hex characters | one admitted file, from raw storage to the training dataset |

The document id becomes the file name in every later stage (`<document_id>.txt` in `storage/extracted` and `storage/processed/*`) and the `document_id` field of each dataset record (chapter 5).

The driving script is `scripts/ingestion.py` (`python -m scripts.ingestion`, code in chapter 12). Its loop, in words:

1. Read every inspection record; keep the last one seen per batch (the records are visited in sorted folder-name order, and folder names start with a timestamp, so "last" is "newest").
2. For each batch: load `source.json`; ask `evaluate_training_rights`; if not allowed, print `BLOCK:` and move on.
3. For each artifact in the inspection record whose `decision` is exactly `accepted_for_ingestion`: call `ingest_artifact`.
4. If at least one document was ingested, call `write_ingestion_manifest`.

The folder `src/corpus_factory/ingestion/` contains five Python files. Tracing the imports from `scripts/ingestion.py` gives a clear split:

| File | Lines | Used by the current pipeline? |
|---|---|---|
| `ingest.py` | 94 | **Yes.** `scripts/ingestion.py` imports `ingest_artifact` and `write_ingestion_manifest` from it. |
| `document.py` | 8 | No. Imported only by `worker.py`. |
| `worker.py` | 13 | No. Imported only by `dispatcher.py`. |
| `dispatcher.py` | 11 | No. Imported only by `loader.py`. |
| `loader.py` | 12 | No. Nothing in `src/` or `scripts/` imports it. |

So `loader.py → dispatcher.py → worker.py → document.py` is a chain that nothing starts. A search of every `.py` file under `src/` and `scripts/` finds no call to `load_documents`. The folder's `README.md` describes that chain as "Distributed Ingestion": a loader lists the raw files, a dispatcher hands them to several worker processes, and each worker is meant to pass a file to a reader and return a `Document`. That is a design for reading very large corpora in parallel. Today the workers do not read anything (see `worker.py` below), and the real pipeline reads documents one at a time in `scripts/extraction.py`. The four files are still documented here in full, because they are in the tree and because they contain the first `yield from` you will meet.

#### `src/corpus_factory/ingestion/ingest.py`

**Why this file exists** — To copy one accepted file into raw storage under a new document id, and to write the manifest that tells the next stage which documents a batch contains.

**What enters / what leaves** — `ingest_artifact` takes the path of a file in `storage/incoming`, the batch id, the artifact id and the file's SHA-256 (as recorded by inspection); it copies the file and returns a dictionary describing the new document. `write_ingestion_manifest` takes the batch id and the list of those dictionaries; it writes `manifest.json` and `manifest.json.sha256` in `storage/raw/<batch-id>/` and returns the manifest path.

**How it connects** — Called by `scripts/ingestion.py`. The manifest it writes is the only thing `scripts/extraction.py` reads to find documents (4.5).

**The code, section by section**

```python
import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from paths import RAW_STORAGE_DIR


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
```

The imports match `decision.py` with one addition: `shutil`, the standard library's module for copying and moving files. `RAW_STORAGE_DIR` is `storage/raw` (from `paths.py`). `utc_now` is the same helper explained in 4.3, repeated here.

```python
def ingest_artifact(
    source_path: Path,
    batch_id: str,
    artifact_id: str,
    sha256: str,
) -> dict:
    document_id = f"doc_{uuid.uuid4().hex}"
```

Four parameters: where the file is now, which batch and artifact it is, and the hash inspection computed for it.

**What Python does** — `uuid.uuid4().hex` is 32 random hexadecimal characters. The f-string puts `doc_` in front, giving a 36-character id such as `doc_3f0c…` (32 hex characters after the prefix).

**What it means in the pipeline** — The document id is random. It is not derived from the file's content, name or batch. Two consequences follow. First, two different files can never clash, whatever they are called. Second, the same file ingested twice gets two different ids: running `scripts.ingestion` again copies every accepted file again under fresh ids. The link back to the original is kept in the manifest (`artifact_id`, `sha256`), not in the id.

```python
    batch_dir = RAW_STORAGE_DIR / batch_id
    objects_dir = batch_dir / "objects"

    objects_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
```

Raw storage mirrors the incoming layout: one folder per batch, files in an `objects` sub-folder. `exist_ok=True` — unlike the decision folder in 4.3 — means "no error if it already exists", which is needed because this function runs once per file and all files of a batch share the folder.

```python
    destination = (
        objects_dir
        / f"{document_id}-{source_path.name}"
    )

    shutil.copy2(
        source_path,
        destination,
    )
```

`source_path.name` is the last part of the incoming path — the stored file name acquisition gave the file. The destination name is the document id, a hyphen, and that name; the extension therefore survives, which extraction relies on to choose how to read the file.

**What Python does** — `shutil.copy2(src, dst)` copies the file's contents and also its metadata, such as the modification time. The original is left where it was.

**What it means in the pipeline** — Ingestion copies, it does not move. `storage/incoming` stays complete and untouched (acquisition marks its batches as append-only), so you can always re-inspect or re-ingest. The cost is disk space: every admitted file now exists twice.

The copy is not verified. The `sha256` parameter is the hash from the inspection record; the function does not hash the file again before or after copying. If the file in `storage/incoming` were changed between inspection and ingestion, the changed bytes would be copied and the manifest would still carry the old hash.

```python
    return {
        "document_id": document_id,
        "batch_id": batch_id,
        "artifact_id": artifact_id,
        "sha256": sha256,
        "source_path": source_path.as_posix(),
        "stored_relative_path": (
            Path("objects") / destination.name
        ).as_posix(),
    }
```

The description of the new document: six keys.

- `document_id`, `batch_id`, `artifact_id`, `sha256` — identity and lineage. `artifact_id` and `sha256` are what let you trace a document back to the exact uploaded file.
- `source_path` — where the file was copied from. `.as_posix()` writes the path with forward slashes on every operating system. Because `scripts/ingestion.py` builds this path from `BATCHES_DIR`, which is absolute, the value stored is an absolute path on the machine that ran the script.
- `stored_relative_path` — `objects/<document_id>-<name>`, relative to the batch folder in raw storage. `Path("objects") / destination.name` builds it and `.as_posix()` turns it into text, for example `objects/doc_x-a.txt`. Storing it relative means raw storage can be moved without breaking the manifest.

```python
def write_ingestion_manifest(
    batch_id: str,
    documents: list[dict],
) -> Path:
    batch_dir = RAW_STORAGE_DIR / batch_id

    manifest = {
        "schema_version": "1.0.0",
        "record_type": "ingestion_manifest",
        "batch_id": batch_id,
        "created_at": utc_now(),
        "documents": documents,
        "summary": {
            "documents": len(documents),
        },
        "next_stage": "extraction",
    }
```

Builds the **raw manifest**: the table of contents of one batch in raw storage. `documents` is the list of dictionaries returned by `ingest_artifact`, one per file. `summary.documents` is their count. `next_stage` is a label for a human reader; no code reads it.

The function does not create `batch_dir`. It relies on `ingest_artifact` having created `batch_dir/objects` already, which is true whenever `documents` is not empty — and `scripts/ingestion.py` only calls this function when it is not.

```python
    manifest_path = batch_dir / "manifest.json"

    encoded = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")

    manifest_path.write_bytes(encoded)
```

Identical in form to the manifest writing in `decision.py` (4.3): JSON with readable indentation and sorted keys, non-ASCII kept as is, a final newline, encoded to UTF-8, written as bytes.

One difference in behaviour: the path is fixed (`storage/raw/<batch-id>/manifest.json`), so a second run for the same batch replaces the manifest. The new manifest lists only the documents of that run, with their new ids. The files copied by the earlier run stay in `objects/` but are no longer listed anywhere. Since extraction reads only the manifest, those older copies are ignored from then on.

```python
    digest = hashlib.sha256(encoded).hexdigest()

    checksum_path = batch_dir / "manifest.json.sha256"

    checksum_path.write_text(
        f"{digest}  manifest.json\n",
        encoding="utf-8",
    )

    return manifest_path
```

The checksum of the manifest bytes, written next to it in the `<digest>  manifest.json` layout, exactly as in 4.3. Be precise about what this checksum covers: it is the hash of `manifest.json`, so it can reveal that the manifest was altered. The per-document `sha256` values inside the manifest are the hashes of the files as inspection saw them.

Nothing in the current code checks either of them again. `scripts/extraction.py` opens `manifest.json` without reading `manifest.json.sha256`, and no later stage re-hashes a raw object. The checksums are evidence you can verify by hand (`shasum -a 256 -c manifest.json.sha256`), not an enforced check.

#### `src/corpus_factory/ingestion/document.py`

**Why this file exists** — To define the shape of "one document" for the unused loader chain. Not used by the current pipeline.

**What enters / what leaves** — Nothing; it only defines a class.

**How it connects** — Imported by `worker.py` only.

**The code, section by section**

```python
from dataclasses import dataclass


@dataclass
class Document:
    source_path: str
    source_type: str
    raw_text: str
```

A dataclass with three fields: where the file is, what kind it is (`txt`, `pdf`, …) and its text. It is not frozen, so fields can be reassigned.

This `Document` class is unrelated to the "document" dictionaries that `ingest_artifact` returns. The real pipeline never creates a `Document` object; its documents are dictionaries in a manifest and `.txt` files on disk.

#### `src/corpus_factory/ingestion/worker.py`

**Why this file exists** — It is the function each worker process would run for one file in the unused loader chain. Not used by the current pipeline.

**What enters / what leaves** — Takes a file path, returns a `Document`. Reads nothing from disk.

**How it connects** — Imported by `dispatcher.py`, which passes `process_file` to a process pool.

**The code, section by section**

```python
from pathlib import Path

from src.corpus_factory.ingestion.document import Document


def process_file(file_path: Path) -> Document:
    source_type = file_path.suffix.lower().lstrip(".")

    return Document(
        source_path=str(file_path),
        source_type=source_type,
        raw_text=None,
    )
```

`file_path.suffix` is the extension with its dot (`.TXT`); `.lower()` makes it lower-case; `.lstrip(".")` removes the leading dot. Real output:

```
process_file(Path("some/dir/Notes.TXT"))
→ Document(source_path='some/dir/Notes.TXT', source_type='txt', raw_text=None)
```

The function never opens the file. `raw_text` is set to `None` even though the dataclass declares it as `str` — Python does not enforce type hints at run time, so this is accepted. The worker is a placeholder: it labels a file with its type and stops. The `README.md` diagram shows `worker.py → txt_reader.py`, but there is no such call in the code.

#### `src/corpus_factory/ingestion/dispatcher.py`

**Why this file exists** — To spread `process_file` over several operating-system processes in the unused loader chain. Not used by the current pipeline.

**What enters / what leaves** — Takes any iterable of paths and a worker count; yields `Document` objects one at a time, in the same order as the paths.

**How it connects** — Imported by `loader.py`; calls `worker.process_file`.

**The code, section by section**

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable

from src.corpus_factory.ingestion.worker import process_file
```

- `ProcessPoolExecutor` — a standard-library class that starts a pool of separate Python processes and runs function calls in them. Separate processes can use several CPU cores at once, which ordinary Python threads cannot do for pure-Python work.
- `Iterable` — a type hint meaning "anything you can loop over": a list, a generator, the result of `rglob`.
- `process_file` — the function each process will run.

```python
def dispatch(files: Iterable[Path], workers: int = 4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for document in executor.map(process_file, files):
            yield document
```

`workers: int = 4` is a parameter with a default value.

`with ProcessPoolExecutor(...) as executor:` starts the pool and guarantees it is shut down when the block ends. `executor.map(process_file, files)` schedules `process_file(f)` for every `f` in `files` and gives the results back in input order.

`yield document` makes `dispatch` a **generator function**: calling it does not run its body; it returns an object that produces one `Document` each time a loop asks for the next one. Generators and `yield` are taught properly in chapter 5. The practical meaning here is that the caller can start working with the first documents before the last ones are ready, and never needs the whole list in memory.

#### `src/corpus_factory/ingestion/loader.py`

**Why this file exists** — To be the entry point of the unused loader chain: "give me every document in raw storage". Not used by the current pipeline; nothing imports it.

**What enters / what leaves** — Takes a worker count. Would walk `storage/raw` and yield one `Document` per file found.

**How it connects** — Calls `dispatcher.dispatch`. Nothing calls it.

**The code, section by section**

```python
from paths import RAW_STORAGE_DIR
from src.corpus_factory.ingestion.dispatcher import dispatch


def load_documents(workers: int = 4):
    files = (
        path
        for path in RAW_STORAGE_DIR.rglob("*")
        if path.is_file()
    )

    yield from dispatch(files, workers=workers)
```

`files` is a generator expression (primer in chapter 1): it describes "every path under `storage/raw`, at any depth, that is a file" without building a list. `rglob("*")` is the recursive form of `glob`: it descends into sub-folders.

Because it takes every file, it would not only yield the documents in `objects/` but also each batch's `manifest.json` and `manifest.json.sha256`, and the `.gitkeep` placeholder in `storage/raw`. The function makes no use of the raw manifest.

**`yield from`, the short version.** A function that contains `yield` is a generator. `yield from other` means "produce every value that `other` produces, one by one, as if I had yielded them myself". The last line is shorthand for:

```
for document in dispatch(files, workers=workers):
    yield document
```

**What Python does** — `load_documents` becomes a generator that passes through whatever `dispatch` yields, until `dispatch` is finished.

**What it means in the pipeline** — It lets one generator hand its work to another without loading anything into a list in between. `dispatcher.py` above writes the long form with a `for` loop; `loader.py` writes the same idea with `yield from`. Chapter 5 uses this for streaming a dataset file record by record and explains generators from the start.

### 4.5 Extraction

| | |
|---|---|
| **INPUT** | For each batch folder in `storage/raw/`: its `manifest.json` (the list of documents) and the files under `objects/`. |
| **PROCESS** | For every document in the manifest, turn the stored file into one plain Python string. Today that means: read `.txt` and `.md` files as UTF-8 text; refuse everything else. |
| **OUTPUT** | `storage/extracted/<batch-id>/<document_id>.txt` — one UTF-8 text file per document that could be read. Documents that could not be read produce a `SKIP:` line on the screen and no file. |
| **WHY IT EXISTS** | A model trains on text, but uploads arrive as files in many formats. Extraction is the single place where "a file of some type" becomes "text". After it, every stage handles only `.txt` files named by document id and never needs to know what the original format was. |

**Extraction** in general means pulling the readable text out of a container: the paragraphs out of a PDF's drawing instructions, the words out of the zipped XML inside a `.docx`. For a plain text file there is nothing to pull out — the file already is the text — so extraction reduces to decoding the bytes.

The driving script is `scripts/extraction.py` (`python -m scripts.extraction`, code in chapter 12). For each batch in raw storage that has a `manifest.json`, it loops over the manifest's `documents`, builds the file path from `stored_relative_path`, calls `extract_text`, and writes the returned string to `storage/extracted/<batch-id>/<document_id>.txt`. If `extract_text` raises `ValueError`, the script prints `SKIP: <file name> — <message>` and continues with the next document. From here on the original file name is gone: the output is named by document id only.

The folder holds one working file and a `readers/` sub-folder:

| File | Lines | State |
|---|---|---|
| `src/corpus_factory/extraction/extractor.py` | 14 | Used. Called by `scripts/extraction.py`. |
| `src/corpus_factory/extraction/readers/txt_reader.py` | 6 | Has code, but nothing imports it. |
| `src/corpus_factory/extraction/readers/md_reader.py` | 0 | Empty file. |
| `src/corpus_factory/extraction/readers/pdf_reader.py` | 0 | Empty file. |
| `src/corpus_factory/extraction/readers/docx_reader.py` | 0 | Empty file. |

There is a gap between stages that you should know about. The inspection policy (`configs/inspection.json`) lists 24 allowed extensions, including `.pdf`, `.docx`, `.html`, `.json` and `.csv`. Inspection can mark such a file `accepted_for_ingestion`, and ingestion will then copy it into `storage/raw`. Extraction accepts two extensions. A PDF therefore travels as far as raw storage and stops here with a `SKIP:` message; it never reaches the training data. At the time of writing, raw storage contains one object, a `.txt` file.

#### `src/corpus_factory/extraction/extractor.py`

**Why this file exists** — To be the one function that maps a file to its text, choosing how by the file's extension.

**What enters / what leaves** — Takes a `Path`. Returns the file's text as a `str`. Raises `ValueError` for an extension it does not handle. Reads the one file; writes nothing.

**How it connects** — Called by `scripts/extraction.py` once per document listed in a raw manifest. Its return value is written to `storage/extracted`, which the cleaning stage reads (4.6.1).

**The code, section by section**

```python
from pathlib import Path


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
```

`file_path.suffix` is the last extension including the dot; `.lower()` makes the comparison case-insensitive, so `Notes.TXT` is treated like `notes.txt`. A file with no extension has the suffix `""`.

```python
    if suffix in {".txt", ".md"}:
        return file_path.read_text(
            encoding="utf-8"
        )
```

The whole of today's extraction. If the extension is `.txt` or `.md`, the file is read and returned.

**What Python does** — `read_text(encoding="utf-8")` opens the file, decodes all its bytes as UTF-8 into one string, and closes it. Two details of text mode matter:

- Line endings are translated while reading. `\r\n` (Windows) and a lone `\r` (old Mac) both become `\n`. A file with the bytes `hello\r\nworld\rend` is returned as `'hello\nworld\nend'` (real output).
- If the bytes are not valid UTF-8, `read_text` raises `UnicodeDecodeError`.

**What it means in the pipeline** — Three consequences, each checked by running the function on small temporary files:

1. **A Markdown file is not interpreted.** `.md` is read exactly like `.txt`. The characters `# Title\n\n**bold**` come back unchanged, markup included. The `#` and `**` become part of the training text.
2. **A UTF-16 text file is skipped.** Inspection accepts `.txt` files encoded as UTF-8, UTF-8 with a byte-order mark, or UTF-16 (see `detect_encoding` in 4.2). Extraction decodes only UTF-8. For a UTF-16 file `read_text` raises `UnicodeDecodeError`. In Python, `UnicodeDecodeError` is a subclass of `ValueError`, so the `except ValueError` in `scripts/extraction.py` catches it and prints a `SKIP:` line with the decoding error.
3. **A byte-order mark is kept.** A UTF-8 file that starts with a byte-order mark (BOM, the invisible character U+FEFF that some Windows editors add) is returned with that character at the front: reading a file containing BOM + `hello` gives `'﻿hello'`. Neither cleaning nor normalization removes it, so it would reach the dataset as the first character of the document.

The whole file is read into memory at once. That is fine for documents; it would not be for a single multi-gigabyte file.

```python
    raise ValueError(
        f"Unsupported extraction type: {suffix}"
    )
```

Every other extension ends here. Real messages: for `file.PDF` the error text is `Unsupported extraction type: .pdf`; for a file named `README` with no extension it is `Unsupported extraction type: ` followed by nothing. Raising instead of returning an empty string forces the caller to notice: the script reports the skip and writes no output file, so an unreadable document cannot slip into the corpus as an empty one.

`extract_text` does not use anything from the `readers/` folder. The `.txt`/`.md` reading is written directly in this function.

#### `src/corpus_factory/extraction/readers/txt_reader.py`

**Why this file exists** — It is a reader for plain text files, written as its own small module. It is not used: no file in `src/` or `scripts/` imports `read_txt`. The only mention of it outside its own file is the diagram in `src/corpus_factory/ingestion/README.md`, which shows a worker handing files to `txt_reader.py`.

**What enters / what leaves** — Takes a `Path`, returns the file's text.

**How it connects** — Nothing calls it; it calls nothing in the project.

**The code, section by section**

```python
from pathlib import Path


def read_txt(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
```

`open(file_path, "r", encoding="utf-8")` opens the file for reading as UTF-8 text; `file.read()` returns everything; the `with` block closes the file. This does the same job as `file_path.read_text(encoding="utf-8")` in `extractor.py`, in the longer spelling.

#### `src/corpus_factory/extraction/readers/md_reader.py`

Empty file (0 bytes). Nothing imports it. Markdown files are handled inside `extract_text` as plain text.

#### `src/corpus_factory/extraction/readers/pdf_reader.py`

Empty file (0 bytes). Nothing imports it. There is no PDF text extraction in the project, and no PDF library in `requirements.txt` (which lists `torch`, `numpy`, `fastapi`, `uvicorn`).

#### `src/corpus_factory/extraction/readers/docx_reader.py`

Empty file (0 bytes). Nothing imports it. There is no Word document extraction in the project.

### 4.6 Preprocessing

| | |
|---|---|
| **INPUT** | `storage/extracted/<batch-id>/<document_id>.txt` — the text of every extracted document. |
| **PROCESS** | Four small steps in a fixed order, each reading the folder the previous one wrote: **cleaning** (tidy line endings and stray whitespace), **normalization** (one Unicode spelling per character), **filtering** (drop empty and very short documents), **deduplication** (drop exact repeats). |
| **OUTPUT** | `storage/processed/cleaned/`, `storage/processed/normalized/`, `storage/processed/filtered/`, `storage/processed/deduplicated/`, each with the same `<batch-id>/<document_id>.txt` layout. The last folder is what dataset building reads. |
| **WHY IT EXISTS** | A model learns from every byte it is shown, including the accidental ones. Preprocessing removes differences that carry no meaning (two ways to end a line, two ways to encode the same letter) and removes documents that would teach nothing (empty) or teach the same thing twice (duplicates). |

Each of the four steps is one pure function in `src/corpus_factory/preprocessing/` plus one script in `scripts/` that applies it to every file:

| Step | Function | Script | Reads | Writes |
|---|---|---|---|---|
| Cleaning | `clean_text(text) -> str` | `scripts/cleaning.py` | `storage/extracted` | `storage/processed/cleaned` |
| Normalization | `normalize_text(text) -> str` | `scripts/normalization.py` | `storage/processed/cleaned` | `storage/processed/normalized` |
| Filtering | `filter_text(text) -> FilterResult` | `scripts/filtering.py` | `storage/processed/normalized` | `storage/processed/filtered` |
| Deduplication | `text_sha256(text) -> str` | `scripts/deduplication.py` | `storage/processed/filtered` | `storage/processed/deduplicated` |

A **pure function** takes values and returns a value, and touches nothing else: no files, no globals, no printing. All four functions here are pure. That is why you can test them on a made-up string in one line, as this section does. All the file reading and writing lives in the scripts (chapter 12).

The first two steps change text; every document that goes in comes out. The last two steps change nothing inside a document; they decide whether the document continues, and a rejected document is simply not written to the next folder.

Keeping a full copy of the corpus after every step costs disk space and buys visibility: you can compare a document before and after any step with an ordinary `diff`, and you can re-run one step without re-running the ones before it.

**Other things in the folder.** Next to the four `.py` files there are four sub-folders with the same names: `preprocessing/cleaning/`, `preprocessing/normalization/`, `preprocessing/filtering/` and `preprocessing/deduplication/`. Each contains exactly one file, an empty `.gitkeep` (a placeholder whose only job is to make Git keep an otherwise empty folder). They hold no code. Having both `cleaning.py` and a folder `cleaning/` side by side looks ambiguous, but Python resolves it: an import of `src.corpus_factory.preprocessing.cleaning` loads the `.py` file (verified: the imported module's file is `src/corpus_factory/preprocessing/cleaning.py`). There is also a four-line `README.md` giving the intent of each step in one phrase: cleaning removes garbage, broken text and empty content; normalization unifies written forms; filtering accepts or rejects a document by quality, language or policy; deduplication removes repetition. The code today implements a deliberately small part of that intent, as the following sections show. In particular there is no language check and no policy check.

**What consumes the result.** `scripts/dataset_building.py` lists every `*.txt` under `storage/processed/deduplicated/<batch-id>/`, uses the file name without `.txt` as the `document_id` and the folder name as the `batch_id`, and writes one JSON record per document — `{"document_id", "batch_id", "text"}` — into `train.jsonl`, `validation.jsonl` or `test.jsonl` under `storage/training/dataset/` (chapter 5). Whatever characters are in a deduplicated file are, unchanged, the `text` the tokenizer and the model will see.

At the time of writing each of the four `storage/processed/*` folders holds one document.

#### 4.6.1 Cleaning

**Cleaning** removes technical noise: characters that are artefacts of how a file was produced, not part of what the author wrote. This implementation is intentionally minimal. It touches line endings, whitespace at the ends of lines, and blank lines at the very start and end of the document. It does not touch any letter.

##### `src/corpus_factory/preprocessing/cleaning.py`

**Why this file exists** — To give every document the same line-ending convention and trim meaningless edge whitespace, before any step that compares or measures text.

**What enters / what leaves** — One string in, one string out. No files.

**How it connects** — Called by `scripts/cleaning.py` on each file of `storage/extracted`; the result is written to `storage/processed/cleaned` and read by normalization.

**The code, section by section**

```python
def clean_text(text: str) -> str:
    """
    Minimal production-safe cleaning.

    This stage only removes technical formatting noise.
    It does NOT normalize Arabic or change linguistic content.
    """
```

The file has no imports; it uses only built-in string methods. The triple-quoted string directly under the `def` line is a **docstring**: documentation attached to the function, not executed. It states the contract: formatting noise only, no change to language content.

```python
    # Normalize line endings:
    # Windows \r\n and old Mac \r -> Unix \n
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
```

`\n` (line feed) and `\r` (carriage return) are two control characters. Unix and macOS end a line with `\n`, Windows with the pair `\r\n`, and very old Mac files with `\r` alone.

**What Python does** — `str.replace(old, new)` returns a new string with every occurrence replaced. The order of the two lines matters. Replacing `\r\n` first turns each Windows ending into one `\n`. Only then are the remaining lone `\r` characters replaced. In the other order, `\r\n` would become `\n\n` and every Windows line would gain an empty line.

**What it means in the pipeline** — To a model, `\r\n` and `\n` are different byte sequences. If half the corpus used one and half the other, the model would spend capacity learning two spellings of "new line", and the deduplication step would treat two otherwise identical documents as different.

In the pipeline as it runs today these two lines find nothing to replace. Extraction already read the file in text mode, which translates `\r\n` and `\r` to `\n` (4.5), and `scripts/cleaning.py` reads its input in text mode as well. The lines still matter whenever `clean_text` is given a string that did not come through such a read.

```python
    # Remove trailing whitespace from each line
    lines = [
        line.rstrip()
        for line in text.split("\n")
    ]
```

`text.split("\n")` cuts the text into a list of lines. The list comprehension builds a new list in which each line has had `.rstrip()` applied.

`rstrip()` with no argument removes whitespace from the right-hand end only. "Whitespace" here is Python's Unicode definition, which is wider than space and tab: it includes the no-break space U+00A0 and the ideographic space U+3000. Real output: `'a \xa0\nb　'` becomes `'a\nb'`. It does not include invisible formatting characters such as the right-to-left mark U+200F: `'x\x0cy ‏\n'` becomes `'x\x0cy ‏'` — the mark at the end of the line counts as a non-space character, so it and the space before it stay.

Whitespace at the start of a line (indentation) is kept, and spaces between words are untouched.

```python
    # Remove empty lines from the beginning
    while lines and not lines[0].strip():
        lines.pop(0)

    # Remove empty lines from the end
    while lines and not lines[-1].strip():
        lines.pop()
```

Two loops that trim blank lines from both ends of the document.

Read the condition `lines and not lines[0].strip()` in two parts. `lines` alone is true when the list is not empty; it comes first so that `lines[0]` is never evaluated on an empty list (`and` stops at the first false part). `lines[0].strip()` removes whitespace from both ends of the first line; an empty string is false in Python, so `not ...strip()` is true exactly when the line is blank. `lines.pop(0)` removes the first element; `lines.pop()` with no argument removes the last.

Blank lines in the middle of the document are not touched: `'a\n\n\nb'` is returned as `'a\n\n\nb'`. Paragraph breaks are content.

```python
    return "\n".join(lines)
```

`"\n".join(lines)` glues the lines back together with a single `\n` between each pair. There is no `\n` after the last line, so a cleaned document never ends with a newline: `'hello\n'` becomes `'hello'`.

Real before/after examples from calling `clean_text`:

| Input (`repr`) | Output (`repr`) | What happened |
|---|---|---|
| `'\n\n  hello  \r\nworld\t \r\r\n \n'` | `'  hello\nworld'` | Line endings unified, trailing spaces and tab removed, blank lines at both ends removed, leading indent kept. |
| `'مرحبا  \r\n  بك   \n\n'` | `'مرحبا\n  بك'` | Same rules for Arabic text. No letter changed. |
| `'  hello'` | `'  hello'` | Leading spaces on the first line are kept. |
| `'a\n\n\nb'` | `'a\n\n\nb'` | Interior blank lines are kept. |
| `'hello\n'` | `'hello'` | Final newline removed. |
| `'   \n \n'` | `''` | A whitespace-only document becomes the empty string. |

The last row is the hand-off to filtering: cleaning does not drop empty documents, it reduces them to `''` and writes an empty file; filtering (4.6.3) is the step that rejects it.

What cleaning does not do, so you do not assume it: it does not remove HTML tags, Markdown markup, URLs, control characters, a byte-order mark, repeated spaces, or repeated blank lines.

#### 4.6.2 Normalization

**Normalization** makes text that means the same thing be stored the same way. The reason is in how this model sees text: the tokenizer of chapter 6 works on the UTF-8 bytes of the string. Two strings that look identical on screen but are built from different code points are different bytes, hence different tokens, hence — to the model — different text.

**Unicode in four sentences.** Every character has a number called a **code point**, written like U+0645 (the Arabic letter meem). Some visible characters can be written two ways: as one **precomposed** code point, or as a base letter followed by a **combining mark** that attaches to it. For example `é` is either U+00E9, or `e` (U+0065) followed by the combining acute accent (U+0301). Unicode declares such pairs **canonically equivalent** — the same text — and defines **normalization forms** that pick one spelling.

**NFC** (Normalization Form C, "composed") is the form used here. It does two things:

1. It puts runs of combining marks into a fixed, standard order.
2. It replaces a base letter plus combining mark by the precomposed code point wherever Unicode has one.

NFC only ever converts between canonically equivalent spellings. It never replaces a character with a merely similar one. That stricter kind of replacement belongs to the "compatibility" forms NFKC and NFKD, which this project does not use.

##### `src/corpus_factory/preprocessing/normalization.py`

**Why this file exists** — To apply Unicode NFC to every document so that canonically equivalent text is byte-for-byte identical before filtering, deduplication and tokenization.

**What enters / what leaves** — One string in, one string out. No files.

**How it connects** — Called by `scripts/normalization.py` on each file of `storage/processed/cleaned`; the result is written to `storage/processed/normalized` and read by filtering.

**The code, section by section**

```python
import unicodedata


def normalize_text(text: str) -> str:
    """
    Minimal normalization.

    This stage keeps linguistic meaning intact.
    It does NOT remove tatweel, diacritics, or change Arabic letters.
    """
```

`unicodedata` is the standard-library module that carries the Unicode character database: the tables that say which code points combine into which. The docstring again states a contract, and names three things that Arabic text pipelines often do and this one deliberately does not.

```python
    # Canonical Unicode normalization only
    text = unicodedata.normalize("NFC", text)

    return text
```

**What Python does** — `unicodedata.normalize("NFC", text)` returns a new string in NFC. The first argument selects the form; the others accepted by Python are `"NFD"`, `"NFKC"` and `"NFKD"`.

**What it means in the pipeline** — One spelling per character. Real output for the Latin example: the two-code-point string `e` + U+0301 has length 2 and 3 UTF-8 bytes; after `normalize_text` it is the single code point U+00E9, length 1 and 2 bytes. Both display as `é`.

**What NFC changes in Arabic.** Each row is real output of `normalize_text`, shown as code points.

| Input | Output | Meaning |
|---|---|---|
| U+0627 U+0653 (alef + combining madda above) | U+0622 | Composed into آ. |
| U+0627 U+0654 (alef + combining hamza above) | U+0623 | Composed into أ. |
| U+0627 U+0655 (alef + combining hamza below) | U+0625 | Composed into إ. |
| U+0648 U+0654 (waw + combining hamza above) | U+0624 | Composed into ؤ. |
| U+064A U+0654 (yeh + combining hamza above) | U+0626 | Composed into ئ. |
| U+062F U+0651 U+064E (dal, shadda, fatha) | U+062F U+064E U+0651 | The two diacritics are put into Unicode's standard order (fatha before shadda). Both are kept; the display is the same. |
| U+062F U+064E U+0651 (dal, fatha, shadda) | unchanged | Already in standard order. |

So for Arabic, NFC does exactly two things: it joins a letter with a separately typed hamza or madda into the usual single letter, and it sorts stacked diacritics into one order. Most Arabic text is typed in the composed form already and passes through unchanged; the decomposed form mostly appears in text that some other tool has converted.

**What NFC does not change in Arabic.** Also real output; every row came back identical to its input.

| Input | Why you might expect a change | Result |
|---|---|---|
| U+0645 U+0640 U+0640 U+0631 (meem, two tatweel, reh) | Tatweel (ـ) is a stretching stroke with no meaning. | Kept. |
| Any letter with fatha, damma, kasra, shadda, sukun, tanween | Many pipelines strip diacritics (tashkeel). | Kept. |
| U+0623 U+0625 U+0622 U+0627 (أ إ آ ا) | Many pipelines fold all alef forms into bare ا. | Four different letters, kept apart. |
| U+0629 U+0647 (ة ه) | Teh marbuta is often folded into heh. | Kept apart. |
| U+0649 U+064A (ى ي) | Alef maksura is often folded into yeh. | Kept apart. |
| U+06CC U+06A9 (Farsi yeh ی, keheh ک) | They look like Arabic ي and ك. | Kept as the Farsi code points. |
| U+0661 U+0662 U+0663 (١٢٣) | Arabic-Indic digits versus `123`. | Kept. |
| U+FEFB (the single-code-point lam-alef ligature ﻻ) | It is the same as lam + alef. | Kept. Only the compatibility forms would split it. |
| U+FE8F (an Arabic "presentation form" of beh) | It is a display shape of ب. | Kept. |
| U+00A0 (no-break space), U+200C (zero-width non-joiner), U+200F (right-to-left mark) | Invisible or special spacing characters. | Kept. |

The folding operations in the second table are sometimes called "Arabic normalization" too, but they are a different thing. They are **lossy**: after folding أ إ آ into ا you cannot tell which the author wrote, and a model trained on folded text will produce folded text. NFC is not lossy in that sense — what it replaces is equivalent by definition. The code chooses the safe option and says so in its docstring. The price is that the model must learn, for instance, that كتاب with and without tatweel or diacritics are the same word, from data alone.

NFC also does nothing to whitespace, letter case or line endings: `normalize_text('Hello  World\r\n')` returns the same string. Those are cleaning's business or nobody's.

**Why normalization comes before deduplication.** Two documents that differ only in how `é` or `أ` is encoded are the same document to a reader. After NFC they are the same bytes, so the hash comparison in 4.6.4 recognises them as duplicates. 4.6.4 shows this with real hashes.

#### 4.6.3 Filtering

**Filtering** is a yes/no decision per document. It changes no text. The purpose in general is to keep material out of the corpus that would make the model worse or teach it nothing: empty files, fragments, boilerplate, the wrong language, low-quality text. This implementation makes two checks, both about size.

##### `src/corpus_factory/preprocessing/filtering.py`

**Why this file exists** — To reject documents that are empty or too short to be useful, and to say why.

**What enters / what leaves** — One string in; a `FilterResult` out (accepted or not, with a reason word). No files.

**How it connects** — Called by `scripts/filtering.py` on each file of `storage/processed/normalized`. When `accepted` is true the script copies the text unchanged to `storage/processed/filtered`. When it is false the script prints `FILTERED OUT: <file> — <reason>` and writes nothing; the reason is not stored anywhere on disk.

**The code, section by section**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FilterResult:
    accepted: bool
    reason: str
```

A small read-only result type, the same pattern as `RightsDecision` in 4.3. Returning an object with a `reason`, and not a bare `True`/`False`, lets the caller report why a document was dropped. `frozen=True` prevents the result from being altered after it is made.

```python
def filter_text(text: str) -> FilterResult:
    if not text.strip():
        return FilterResult(
            accepted=False,
            reason="empty_document",
        )
```

First check. `text.strip()` removes whitespace from both ends; if nothing is left, the string is empty and `not` makes the condition true. So a document that is empty, or consists only of spaces, tabs and newlines, is rejected as `empty_document`. This catches the `''` that cleaning produces from a whitespace-only file.

```python
    if len(text) < 20:
        return FilterResult(
            accepted=False,
            reason="too_short",
        )
```

Second check: fewer than 20 characters is `too_short`.

**What Python does** — `len(text)` on a string counts code points, not bytes and not words. `'مرحبا'` has `len` 5 although it occupies 10 bytes in UTF-8.

**What it means in the pipeline** — The threshold is the number `20` written directly in the code; it is not read from a config file. It is a floor against fragments, not a quality measure. A few points about what exactly is counted:

- The count is on the text as given, not on `text.strip()`. Whitespace counts. A string of 19 spaces followed by `a` has length 20 and is accepted.
- Combining marks count. Fully vowelled Arabic reaches 20 sooner than the same words without diacritics.
- Nothing looks at what the characters are. Twenty exclamation marks pass.

```python
    return FilterResult(
        accepted=True,
        reason="accepted",
    )
```

Everything else is accepted, with the reason word `accepted`.

Real results from `filter_text`:

| Input | `len` | Result |
|---|---|---|
| `''` | 0 | rejected, `empty_document` |
| `'   \n\t'` | 5 | rejected, `empty_document` |
| `'hello'` | 5 | rejected, `too_short` |
| `'مرحبا'` | 5 | rejected, `too_short` |
| `'i love coffee'` | 13 | rejected, `too_short` |
| `'a' * 19` | 19 | rejected, `too_short` |
| `'a' * 20` | 20 | accepted |
| `'i love coffee so much'` | 21 | accepted |
| `'مرحبا بكم في المدرسة'` | 20 | accepted (37 bytes, but 20 characters) |
| `'!!!!!!!!!!!!!!!!!!!!'` | 20 | accepted |

The first check is not redundant with the second: both would reject `''`, but the reason differs, and a long run of whitespace (say 50 spaces) is caught only by the first.

There is no upper limit, no language detection, no check for repeated characters or for the share of letters versus symbols. Whether a 20-character document is worth training on is not judged.

#### 4.6.4 Deduplication

**Deduplication** removes repeated documents. Repeats are common in collected text: the same file uploaded twice, the same notice copied into several folders. They matter for a language model in two ways:

- **Skewed training.** A document that appears five times is seen five times per pass over the data. The model is pushed five times as hard towards reproducing it, which encourages memorising that text over learning general patterns.
- **Leaking between splits.** The dataset is divided into train, validation and test by document id (chapter 5). Ingestion gives the same content a different id each time it is admitted. Without deduplication, one copy could land in train and another in test; the model would then be "tested" on text it was trained on, and the evaluation numbers of chapter 9 would look better than they should.

This implementation detects **exact** duplicates only: two documents are duplicates when their text is identical character for character.

##### `src/corpus_factory/preprocessing/deduplication.py`

**Why this file exists** — To give every document a short fingerprint so that "have I seen this text before?" becomes a lookup in a set of fingerprints.

**What enters / what leaves** — One string in; a 64-character hexadecimal string out. No files.

**How it connects** — Called by `scripts/deduplication.py`. The script keeps one Python `set` named `seen_hashes` for the whole run, across all batches. For each file of `storage/processed/filtered`, in sorted order, it computes the fingerprint: if it is already in the set, it prints `DUPLICATE:` and writes nothing; otherwise it adds the fingerprint to the set and copies the text unchanged to `storage/processed/deduplicated`, which dataset building reads.

**The code, section by section**

```python
import hashlib


def text_sha256(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()
```

The entire file. Note that the function does not decide anything about duplicates; it only fingerprints. The comparison lives in the script.

**What Python does** — `text.encode("utf-8")` turns the string into bytes, because a hash function works on bytes. `hashlib.sha256(...)` computes the SHA-256 hash of those bytes (taught in 4.1). `.hexdigest()` returns it as 64 hexadecimal characters. `text_sha256("hello")` gives the same value as `hashlib.sha256(b"hello").hexdigest()`.

**What it means in the pipeline** — A document of any length is reduced to 64 characters that are, for all practical purposes, unique to its exact content. Remembering the fingerprints of a million documents takes a few tens of megabytes; remembering the million documents would not fit in memory. Checking whether a fingerprint is in a `set` takes the same short time however many are stored.

Real fingerprints:

| Text (`repr`) | `text_sha256` |
|---|---|
| `'hello'` | `2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824` |
| `'hello '` | `5e3235a8346e5a4585f8c58562f5052b8fe26a3bb122e1e96c76784964dfc461` |
| `'Hello'` | `185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969` |
| `'hello\n'` | `5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03` |
| `'مرحبا'` | `80eff1a750bb540045622ad23c148c8875790515e3f768c77d5dff8c1d221b49` |

One extra space, one capital letter or one trailing newline gives a completely different fingerprint. That is the nature of a hash, and it is the reason the earlier steps come first: cleaning removes the trailing space and the final newline, so `'hello '` and `'hello\n'` would both have become `'hello'` before reaching this step.

The same holds for Unicode spelling. The two encodings of `é` from 4.6.2 hash differently:

| Text | `text_sha256` |
|---|---|
| `e` + U+0301 (decomposed) | `bf12767b0f2a56b2190075bae8169f656e3ce8d6357d4aff184bc6c7ea48f9f6` |
| U+00E9 (composed) | `4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c` |

Normalization turns the first into the second, so by the time documents arrive here both forms share the second fingerprint.

What exact matching does not catch — these all count as different documents:

- the same text with different capitalisation, or with one word changed;
- the same Arabic text with and without diacritics or tatweel (normalization keeps those, 4.6.2);
- one document that contains another, or two documents that share most of their paragraphs.

Detecting those is called near-duplicate detection and is not present in the project.

Two properties of the surrounding script are part of understanding the stage. The first copy wins: files are visited batch by batch in sorted name order, so which of two identical documents is kept depends on batch id and document id, not on which was uploaded first. And `seen_hashes` exists only while the script runs; it is rebuilt from the files in `storage/processed/filtered` on every run and is not saved.

#### What I should understand before moving on

- Inspection decides whether a file is safe; provenance decides whether you may train on it. A batch passes the rights gate only when its newest valid decision record says `allowed`; with no record, or with any other word, the answer is no — whatever `source.json` says.
- Decision records are append-only and checksummed. A new decision is a new folder; the gate picks the latest by `created_at` and ignores any record whose checksum does not match.
- Ingestion copies accepted files from `storage/incoming` to `storage/raw` under a new random document id and writes a manifest that links each document back to its artifact id and SHA-256. It is the manifest, not the folder contents, that tells extraction what exists.
- Only `ingest.py` is used in the ingestion folder. The loader/dispatcher/worker/document chain is not called by anything, and the worker does not read files.
- Extraction today is "decode `.txt` and `.md` as UTF-8". Other formats that inspection accepts are ingested and then skipped. The three non-text reader files are empty and `txt_reader.py` is unused.
- Cleaning unifies line endings and trims whitespace at line ends and blank lines at document ends. Normalization applies Unicode NFC, which merges equivalent spellings and removes nothing from Arabic: tatweel, diacritics and letter variants stay.
- Filtering rejects empty documents and documents under 20 characters. Deduplication drops a document whose SHA-256 matches one already seen in the same run; it is exact matching, so the earlier steps determine what counts as "the same".
- The order clean → normalize → filter → deduplicate is not arbitrary: each step makes the next one's test meaningful.

#### Self-test

1. A batch's `source.json` is edited by hand so that its `license.training_use` reads `allowed`. No decision record exists for the batch. Will `scripts.ingestion` ingest it? Which line of `gate.py` decides that?
2. You record `allowed` for a batch on Monday and `denied` on Tuesday. On Wednesday someone opens Tuesday's `manifest.json` in an editor and changes `denied` to `allowed`, without touching the `.sha256` file. What does the gate return for the batch on Wednesday, and why?
3. You run `python -m scripts.ingestion` twice in a row for the same allowed batch containing one accepted file. How many files are in `storage/raw/<batch-id>/objects/` afterwards, how many documents does `manifest.json` list, and how many will extraction process?
4. In `loader.py`, what would change for the caller if `yield from dispatch(files, workers=workers)` were replaced by `return dispatch(files, workers=workers)`? And what would change if it were replaced by `yield dispatch(files, workers=workers)`?
5. A `.txt` file saved by a Windows editor as UTF-16 passes inspection and is ingested. Describe exactly what happens to it at extraction, including which `except` clause is involved and why it matches.
6. In `clean_text`, why must `text.replace("\r\n", "\n")` run before `text.replace("\r", "\n")`? What would `"a\r\nb"` become if the two lines were swapped?
7. Two documents contain the same Arabic sentence. In one, أ is typed as a single key (U+0623); in the other it is stored as alef followed by a combining hamza (U+0627 U+0654). In a third document the same sentence is fully vowelled with diacritics. After the whole preprocessing chain, how many of the three survive deduplication, and which step is responsible for each outcome?
8. A document consists of the 12-character sentence `"i love tea.\n"` preceded by 30 blank lines. Follow it through cleaning, normalization and filtering: what string does each step produce or decide? Would the outcome differ if filtering ran before cleaning?

<details><summary>Answers</summary>

1. No. With no decision record, `find_latest_provenance_decision` returns `None`, and `evaluate_training_rights` reaches its final `return RightsDecision(allowed=False, status=training_use, ...)`. The word from `source.json` is copied into `status` and `reason`, but `allowed` is the literal `False` on that line. `scripts/ingestion.py` tests `rights.allowed`, prints `BLOCK:` and skips the batch.
2. `allowed=True`, from Monday's record. The edit changed the bytes of Tuesday's manifest, so `_verify_manifest` computes a digest that no longer equals the one in `manifest.json.sha256` and returns `False`. `find_latest_provenance_decision` skips that record with `continue`. The only valid record left for the batch is Monday's `allowed`, so it is the latest. The tampering did not succeed in the way intended (the edited record is ignored), but it did remove the `denied` decision from consideration. No message is printed about the skipped record.
3. Two files in `objects/`, because each run calls `ingest_artifact`, which creates a new random `document_id` and copies the file again; the first copy is not removed. The manifest lists one document: `write_ingestion_manifest` rewrites `manifest.json` with only the documents of the latest run. Extraction processes one, because it reads the manifest and never lists the `objects/` folder. (It writes a new `<document_id>.txt` in `storage/extracted`, next to the one from the first run.)
4. With `return dispatch(...)`, `load_documents` would stop being a generator function (it would contain no `yield`) and would become an ordinary function that returns the generator made by `dispatch`. A caller looping over the result would see the same documents. With `yield dispatch(...)`, `load_documents` would be a generator that yields exactly one value — the `dispatch` generator object itself — so a `for` loop over it would run once and receive a generator, not `Document` objects. `yield from` is what flattens: it yields each item of the inner generator.
5. `scripts/extraction.py` calls `extract_text`. The suffix is `.txt`, so `file_path.read_text(encoding="utf-8")` runs. The UTF-16 bytes (starting with a byte-order mark that is not valid UTF-8) cannot be decoded, and `read_text` raises `UnicodeDecodeError`. The script's `except ValueError as error:` catches it because `UnicodeDecodeError` is a subclass of `ValueError`. It prints `SKIP: <file name> — <decoding error>` and continues. No file is written to `storage/extracted`, so the document silently leaves the pipeline at this point even though inspection accepted it.
6. `\r\n` is one line ending made of two characters. Handling the pair first turns it into one `\n`; the second replace then only meets lone `\r`. Swapped, the first replace would turn the `\r` of `\r\n` into `\n`, giving `"a\n\nb"`; the second replace (`"\r\n"` → `"\n"`) would then find nothing. The document would gain an empty line after every Windows line.
7. Two survive. The first and second documents become identical at normalization: NFC composes U+0627 U+0654 into U+0623, so their bytes and therefore their SHA-256 fingerprints match, and deduplication drops whichever comes second in sorted order. The vowelled document survives because NFC does not remove diacritics; its text is different, so its fingerprint is different. Exact-match deduplication treats it as a separate document.
8. Cleaning: the 30 leading blank lines are popped and the final empty line (after the last `\n`) is popped, leaving `"i love tea."` — 11 characters. Normalization: unchanged, the text is ASCII and already NFC. Filtering: `text.strip()` is not empty, so it is not `empty_document`; `len(text)` is 11, which is less than 20, so the result is `accepted=False, reason="too_short"`, and the document is not written to `storage/processed/filtered`. If filtering ran first on the raw text, the length would be 30 newlines + 12 characters = 42, which is not less than 20, and the document would be accepted. Cleaning first is what makes the length test measure content and not padding.

</details>

---

## 5. Dataset

| | |
|---|---|
| **INPUT** | The deduplicated plain-text documents in `storage/processed/deduplicated/<batch>/*.txt` (the end of chapter 4), and later the tokenized files in `storage/training/tokenized/*.jsonl`. |
| **PROCESS** | Decide, for every document, whether it belongs to `train`, `validation` or `test` (`src/dataset/builder.py`). Read JSONL files one record at a time and cut token lists into `(x, y)` next-token pairs (`src/dataset/loader.py`). |
| **OUTPUT** | Three text files, `storage/training/dataset/{train,validation,test}.jsonl`; and, at training time, a stream of pairs of integer tensors `(x, y)`. |
| **WHY IT EXISTS** | Everything before this point produced clean text. Everything after this point needs that text in a fixed, repeatable form: grouped into splits, one document per line, and finally sliced into fixed-size pieces the model can train on. |

The `src/dataset/` directory contains exactly two source files, `builder.py` (50 lines) and `loader.py` (111 lines), plus Python's `__pycache__` folder. There is no `__init__.py`; Python still imports `src.dataset.builder` because a directory without `__init__.py` is treated as a "namespace package".

The two files are used at different moments, so keep this map in mind:

| Moment | Driving script (code shown in chapter 12) | Uses from this chapter |
|---|---|---|
| Dataset building | `scripts/dataset_building.py` | `assign_splits` |
| Tokenizer training (chapter 6) | `scripts/tokenizer_training.py` | `load_texts` |
| Tokenize dataset (chapter 6) | `scripts/tokenize_dataset.py` | `load_jsonl` |
| Training (chapter 8) and evaluation (chapter 9) | `scripts/train.py` and the evaluator | `make_training_examples` |
| Model statistics | `scripts/model_stats.py` | `load_token_sequences` |

**Why splits exist at all.** A language model is trained by showing it text and adjusting it until it predicts that text well. If you then measure how good it is on the same text, the number tells you almost nothing: a model can score perfectly by memorising its training text and still be useless on anything new. So the corpus is divided into three groups that never mix:

| Split | Share here | What it is for |
|---|---|---|
| `train` | 90% | The only text the model's weights (and the tokenizer's merges) are learned from. |
| `validation` | 5% | Text the model never trains on, checked *during* development. If the training loss keeps falling while the validation loss rises, the model is memorising (overfitting). You use this number to make decisions: when to stop, which settings are better. |
| `test` | 5% | Text touched only at the very end, for one honest final score. Because you made decisions by looking at validation, validation is slightly "used up"; test is the number you have not tuned towards. |

The split is made **per document**, not per line or per sentence. If half of a document were in train and the other half in validation, the validation half would look very much like text the model has already seen, and the validation score would be flattering.

**The two JSONL shapes.** JSONL ("JSON Lines") is a text file in which every line is one complete JSON object. It suits datasets because you can append a record by writing one line and read a record by reading one line, without ever holding the whole file in memory.

Stage 1, `storage/training/dataset/<split>.jsonl`, written by `scripts/dataset_building.py`. One line per document, three keys:

```text
{"document_id": "doc-a", "batch_id": "batch-1", "text": "hello"}
{"document_id": "doc-b", "batch_id": "batch-1", "text": "مرحبا"}
```

| Key | Value |
|---|---|
| `document_id` | The file name of the deduplicated `.txt` file without its extension (`source_file.stem`). This is the string that gets hashed to choose the split. |
| `batch_id` | The name of the batch directory the file came from. |
| `text` | The whole document as one string. Newlines inside the text are stored as `\n` inside the JSON string, so the record still occupies exactly one line of the file. |

Stage 2, `storage/training/tokenized/<split>.jsonl`, written by `scripts/tokenize_dataset.py`. Same documents, same order, but the text has been replaced by numbers:

```text
{"document_id": "doc-a", "batch_id": "batch-1", "input_ids": [256, 104, 101, 108, 108, 111, 257], "num_tokens": 7}
```

| Key | Value |
|---|---|
| `document_id`, `batch_id` | Copied unchanged from stage 1. |
| `input_ids` | The document as a list of token ids: `256` (BOS) first, `257` (EOS) last, the encoded text in between. Chapter 6 explains every one of these numbers. |
| `num_tokens` | `len(input_ids)`, stored for convenience. Nothing in `src/` reads it back. |

(The values above are made up. `[104, 101, 108, 108, 111]` really is `"hello"` as bytes, as you will see in 6.1.)

**What is really on disk today.** Counts only:

| Split | Documents | Stage 1 file | Tokens in stage 2 |
|---|---|---|---|
| `train` | 1 | 663 bytes; the text is 297 characters, 536 UTF-8 bytes | 259 (257 for the text + BOS + EOS) |
| `validation` | 0 | 0 bytes (empty file) | 0 |
| `test` | 0 | 0 bytes (empty file) | 0 |

The whole corpus is one short document. That fact shapes several things in this chapter, starting with the "tiny-corpus rule" in `assign_splits`.

#### `src/dataset/builder.py`

**Why this file exists.** It answers one question, the same way every time: "which split does this document belong to?"

**What enters / what leaves.** In: document ids (strings). Out: a split name (`"train"`, `"validation"` or `"test"`) for one id, or a dictionary `{document_id: split}` for a list of ids. It reads no files and writes no files; it is pure calculation.

**How it connects.** `scripts/dataset_building.py` lists the deduplicated `.txt` files (previous stage: deduplication, chapter 4), calls `assign_splits` once with all their ids, and writes each document's record into the file for its split. `choose_split` is called only from `assign_splits`.

**The code, section by section.**

```python
import hashlib
```

`hashlib` is the standard-library module of hash functions. It is the only import, and the file needs it for one function, `hashlib.sha256`. SHA-256 is explained fully in 4.1; the one property that matters here is: the same input bytes always give the same 64-hex-digit output, and the output looks random (changing one character of the input changes it completely).

```python
def choose_split(document_id: str) -> str:
    """
    Deterministic split based on document_id.

    90% train
    5% validation
    5% test
    """
```

A function that takes one string and returns one string. The triple-quoted text is a docstring: documentation attached to the function, not executed. "Deterministic" means "no randomness: same input, same answer, on every run and every machine".

```python
    digest = hashlib.sha256(
        document_id.encode("utf-8")
    ).hexdigest()

    bucket = int(digest[:8], 16) % 100
```

These two statements are the whole idea. Follow them with the made-up id `"doc-a"` (every value below is real output):

| Step | Expression | Value for `"doc-a"` |
|---|---|---|
| 1 | `document_id.encode("utf-8")` | `b'doc-a'` — the text turned into bytes, because hash functions work on bytes, not on text (bytes vs text: 6.1) |
| 2 | `hashlib.sha256(...).hexdigest()` | a 64-character string of hex digits beginning `1fb08630b1ed4e62…` |
| 3 | `digest[:8]` | `"1fb08630"` — a slice: the first 8 characters |
| 4 | `int("1fb08630", 16)` | `531662384` — read those 8 characters as a base-16 number |
| 5 | `531662384 % 100` | `84` — the remainder after dividing by 100 |

**What Python does.** `digest[:8]` takes characters `0` to `7`. `int(text, 16)` converts text to an integer, treating it as hexadecimal (digits `0-9` then `a-f` for ten to fifteen). Eight hex digits can express any number from `0` to `4294967295` (that is `ffffffff`, 2³² − 1). `%` is the modulo operator: `a % 100` is always one of `0, 1, …, 99`.

**What it means in the pipeline.** The hash turns an arbitrary id into a number that behaves like a random draw from about four billion values, and `% 100` folds that into 100 equally likely "buckets". A bucket number is then a percentage position: buckets `0–89` are 90 of the 100, and so on. Only 8 of the 64 hex digits are used because 32 bits is far more than enough to spread documents over 100 buckets.

```python
    if bucket < 90:
        return "train"

    if bucket < 95:
        return "validation"

    return "test"
```

Three ranges. `return` leaves the function immediately, so the second `if` is reached only when `bucket` is 90 or more, and the last line only when it is 95 or more.

| Bucket | Count of buckets | Split |
|---|---|---|
| `0`–`89` | 90 | `train` |
| `90`–`94` | 5 | `validation` |
| `95`–`99` | 5 | `test` |

So `"doc-a"` (bucket `84`) is `train`. Two more made-up ids, real output: `"doc-1"` → digest starts `bb0e4f49` → `3138277193` → bucket `93` → `validation`; `"doc-24"` → `e6cc2ccf` → `3872140495` → bucket `95` → `test`. Over the 10,000 ids `"doc-0"` … `"doc-9999"` the function gives 8,999 train, 495 validation and 506 test: close to 90/5/5, not exactly, which is what you expect from something that behaves like chance.

**Why a hash instead of `random.choice`.** Three reasons, in order of importance:

1. *Stability across runs.* The dataset is rebuilt whenever the corpus changes. With random choice, a document that was in `test` yesterday could land in `train` today, the model would train on it, and your test score would then be measured on text the model has seen. That is called leakage, and it silently makes scores too good. With the hash, a document's split depends only on its own id, forever.
2. *Stability when the corpus grows.* Adding or removing other documents does not move any existing document. (A seeded random shuffle is repeatable too, but only as long as the list of documents and their order stay identical.)
3. *No state to store.* Nothing needs to remember earlier decisions; any machine can recompute them.

The price: the percentages are only approximate, and with very few documents they can be far off, which is what the second function deals with.

```python
def assign_splits(
    document_ids: list[str],
) -> dict[str, str]:
    """
    Split every document, keeping train non-empty.

    On a tiny corpus the hash split can leave train
    with no documents, which makes tokenizer training
    and model training impossible. In that case every
    document goes to train.
    """
```

Takes the list of all document ids, returns a dictionary mapping each id to its split. (In the file there is a single blank line between `choose_split` and this function rather than the usual two; that is a style detail and changes nothing.)

```python
    splits = {
        document_id: choose_split(document_id)
        for document_id in document_ids
    }
```

A dict comprehension (see the primer in 1): for each id, the key is the id and the value is the result of `choose_split`. For `["doc-1", "doc-a"]` it produces `{'doc-1': 'validation', 'doc-a': 'train'}`. If the same id appeared twice in the list it would simply be stored once, since a dictionary has one value per key.

```python
    if splits and "train" not in splits.values():
        return {
            document_id: "train"
            for document_id in splits
        }

    return splits
```

**What Python does.** `splits` on its own is "truthy" when the dictionary is not empty. `splits.values()` is the collection of split names; `"train" not in …` is true when no document at all was assigned to train. `and` requires both. When both hold, a new dictionary is built with the same keys and the value `"train"` for every one. Otherwise the hash result is returned unchanged. For an empty list the function returns `{}`.

**What it means in the pipeline.** This is the tiny-corpus rule. With one document there is a 10% chance the hash puts it in `validation` or `test`, leaving `train.jsonl` empty. Then the tokenizer could not be trained ("Cannot train tokenizer on an empty corpus", 6.2) and the model would have nothing to learn from. The rule is all-or-nothing: it fires only when train would be completely empty, and then it moves *everything* to train.

Real outputs showing the rule:

```text
assign_splits(["doc-1"])            -> {'doc-1': 'train'}                         (hash said validation; rule fired)
assign_splits(["doc-1", "doc-24"])  -> {'doc-1': 'train', 'doc-24': 'train'}      (hash said validation + test; rule fired)
assign_splits(["doc-1", "doc-a"])   -> {'doc-1': 'validation', 'doc-a': 'train'}  (train not empty; rule did not fire)
```

**The real situation today.** The corpus has one document. Hashing its real id gives bucket `92`, which `choose_split` maps to `validation`. So the rule fired: the document was moved to `train`, and `validation.jsonl` and `test.jsonl` are empty files. Two consequences you should hold on to:

- There is currently no held-out text. Any loss or perplexity you see is measured on the same document the model was trained on; it tells you how well the model memorised, not how well it generalises.
- The rule makes a split depend on the rest of the corpus in this one case. When a second document arrives and lands in `train` by hash, the rule stops firing and the first document returns to `validation`: text the already-trained model has seen. Retrain from scratch after such a change if you want the validation number to mean anything.

#### `src/dataset/loader.py`

**Why this file exists.** It is the single place that reads JSONL files, and the place where a list of token ids becomes the `(x, y)` pairs that training consumes.

**What enters / what leaves.** In: a `Path` to a `.jsonl` file (and, for the last function, a `context_length`). Out: a *stream* of items: dictionaries, strings, lists of integers, or pairs of tensors. It writes nothing.

**How it connects.** The four functions are stacked: `load_jsonl` reads lines; `load_texts` and `load_token_sequences` each sit on `load_jsonl` and pick one field; `make_training_examples` sits on `load_token_sequences`. Callers: `scripts/tokenizer_training.py` (`load_texts`), `scripts/tokenize_dataset.py` (`load_jsonl`), `scripts/model_stats.py` (`load_token_sequences`), `src/training/trainer.py` and `src/evaluation/evaluator.py` (`make_training_examples`).

**Generators and `yield` (this is their home in the document).** Every function in this file contains the keyword `yield`, and that changes what kind of function it is. A normal function runs to its `return` and hands back one finished value. A function containing `yield` is a *generator function*: calling it runs none of its body. It hands back a *generator object*, and the body runs only when something asks that object for the next item, and only as far as the next `yield`. There it pauses, with all its local variables intact, until the next item is requested.

A demonstration, separate from the project code:

```python
def numbers():
    print("  (generator starts)")
    for n in [1, 2, 3]:
        print("  (about to yield", n, ")")
        yield n

g = numbers(); print("created:", type(g).__name__)
print("first:", next(g)); print("second:", next(g))
print("rest:", list(g)); print("again:", list(g))
```

Real output:

```text
created: generator
  (generator starts)
  (about to yield 1 )
first: 1
  (about to yield 2 )
second: 2
  (about to yield 3 )
rest: [3]
again: []
```

Read it line by line: creating `g` printed nothing from inside the function. The first `next(g)` ran the body up to the first `yield`. `list(g)` drained what was left. The second `list(g)` gave `[]`: **a generator can be consumed only once.** A `for` loop over a generator is just repeated `next()` until it is exhausted.

Why this matters for a dataset: a JSONL file can be far larger than memory. A generator that yields one record at a time needs memory for one record, however large the file. That is what "streaming" means. (`yield from`, a shorthand for "yield everything from this other iterable", was introduced in 4.4; this file does not use it.)

```python
import json
from collections.abc import Iterator
from pathlib import Path

import torch
```

| Import | What it is | Why this file needs it |
|---|---|---|
| `json` | Standard-library JSON reader/writer. | `json.loads` turns one line of text into a Python dictionary. |
| `Iterator` | A type name from `collections.abc` meaning "something you can call `next()` on". | Only for type hints: `-> Iterator[dict]` tells the reader that the function yields dictionaries one at a time. It has no effect at run time. |
| `Path` | File-path object (primer in 1). | Type hint for the `path` parameters, and `path.open(...)`. |
| `torch` | PyTorch, the tensor library. | `make_training_examples` returns `torch.Tensor` objects. Tensors are explained in chapter 7; here it is enough to know a tensor is PyTorch's array of numbers. |

```python
def load_jsonl(path: Path) -> Iterator[dict]:
    """
    Stream JSONL records one by one.
    """

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue
```

`path.open("r", encoding="utf-8")` opens the file for reading as UTF-8 text; `with` guarantees it is closed afterwards (primer in 1). Looping over an open text file gives one line at a time; Python reads the file in small pieces behind the scenes instead of loading it whole. `enumerate(file, start=1)` pairs each line with a counter starting at `1`, so `line_number` is the human line number, kept only for the error message below.

`line.strip()` removes whitespace from both ends, including the trailing newline. `if not line: continue` skips lines that are empty after stripping, so a blank line in the file is tolerated instead of crashing the JSON parser.

```python
            try:
                record = json.loads(line)

            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSONL at {path}, "
                    f"line {line_number}"
                ) from error

            yield record
```

`json.loads(line)` parses the line ("loads" = "load from string"). For `{"document_id": "doc-a", "text": "hello"}` the result is a Python `dict` with those two keys. If the line is not valid JSON, `json.loads` raises `json.JSONDecodeError`; the `except` catches it and raises a `ValueError` whose message names the file and the line. `from error` keeps the original error attached as the cause (primer in 1). Checked with a made-up file whose second line was `{oops`: the message was `Invalid JSONL at <path>/demo_bad.jsonl, line 2`.

**What Python does.** `yield record` hands one dictionary to whoever is iterating and pauses right there, inside the `for` loop, inside the `with` block, with the file still open. When the caller asks for the next record, execution resumes after the `yield`, loops to the next line, and so on. When the lines run out, the loop ends, the `with` block closes the file, and the generator is finished.

**What it means in the pipeline.** At any moment only one line of the file is held in memory. Two side effects of laziness are worth knowing: (1) calling `load_jsonl(path)` on a file that does not exist does *not* fail at the call; `FileNotFoundError` appears at the first `next()` (verified); (2) an invalid line in the middle of a file is reported only when the reader gets there, after earlier records have already been processed.

```python
def load_texts(path: Path) -> Iterator[str]:
    """
    Stream only text fields.
    Used for tokenizer training.
    """

    for record in load_jsonl(path):
        text = record.get("text")

        if not isinstance(text, str):
            raise ValueError(
                f"Invalid text field in "
                f"{record.get('document_id', 'unknown')}"
            )

        yield text
```

A generator built on a generator. It iterates over `load_jsonl(path)` and yields only each record's `"text"`. `record.get("text")` is the dictionary lookup that returns `None` instead of raising when the key is missing. `isinstance(text, str)` checks that the value really is a string; a missing key (`None`) or a wrong type (say, a number) raises a `ValueError` naming the document. `record.get('document_id', 'unknown')` is `.get` with a default: if even the id is missing, the message says `unknown`. On a made-up two-line stage-1 file, `list(load_texts(p))` returned `['hello', 'مرحبا']`.

This reads stage-1 files (records with `text`). It is what feeds the tokenizer trainer in 6.2.

```python
def load_token_sequences(
    path: Path,
) -> Iterator[list[int]]:
    """
    Stream tokenized documents.
    """

    for record in load_jsonl(path):
        input_ids = record.get("input_ids")

        if not isinstance(input_ids, list):
            raise ValueError(
                f"Invalid input_ids in "
                f"{record.get('document_id', 'unknown')}"
            )

        yield input_ids
```

The same pattern for stage-2 files: yield each record's `input_ids`. The check confirms the value is a list; it does not look inside the list, so it would not notice a list containing something other than integers. One yielded item is one whole document as a list of ids, for example `[256, 104, 101, 108, 108, 111, 257]`.

```python
def make_training_examples(
    path: Path,
    context_length: int,
) -> Iterator[
    tuple[torch.Tensor, torch.Tensor]
]:
    """
    Build next-token prediction examples.

    x = current tokens
    y = same sequence shifted one token forward
    """
```

Parameters: `path`, a stage-2 (tokenized) JSONL file; `context_length`, the largest number of tokens the model reads at once (`128` in `src/model/config.py`). The return hint says: this yields tuples of two tensors.

**The idea.** A language model is trained on one task: given the tokens so far, predict the next one. So a training example needs an input `x` (some tokens) and a target `y` (for every position of `x`, the token that actually came next). You do not need to label anything by hand: the text itself is the answer key. If the document is `[A, B, C, D]`, then after `A` comes `B`, after `A B` comes `C`, after `A B C` comes `D`. Written as two aligned lists: `x = [A, B, C]`, `y = [B, C, D]`. `y` is `x` moved one place forward. How these pairs become a loss is chapter 8; here you only need to see how they are cut.

```python
    for token_ids in load_token_sequences(path):

        if len(token_ids) < 2:
            continue
```

One document at a time. A document with fewer than two tokens cannot give even one "this token, then that token" pair, so it is skipped. Because documents are handled one at a time, **no example ever spans two documents**: the model is never asked to predict the start of document 2 from the end of document 1.

```python
        for start in range(
            0,
            len(token_ids) - 1,
            context_length,
        ):
            chunk = token_ids[
                start:start + context_length + 1
            ]

            if len(chunk) < 2:
                continue
```

This is the cutting step.

**What Python does.** `range(0, stop, step)` produces `0, step, 2*step, …` for as long as the value is less than `stop`. Here the step, called the *stride*, is `context_length`, and `stop` is `len(token_ids) - 1`. The slice `token_ids[start:start + context_length + 1]` takes up to `context_length + 1` tokens beginning at `start`; a slice that runs past the end of a list simply returns what is there, without error.

**What it means in the pipeline.** Three decisions are encoded in those numbers:

- *Why `+ 1` in the slice.* To make an `x` of `context_length` tokens you need `context_length + 1` tokens, because the last position of `x` needs a target too: the token that follows it.
- *Why the stride is `context_length` and not `context_length + 1`.* Consecutive chunks overlap by exactly one token. The last token of one chunk is used there only as a target; it becomes the first *input* of the next chunk. The result is that every adjacent pair of tokens in the document (token `i` → token `i+1`) is used as a (input, target) exactly once: none skipped, none repeated.
- *Why `stop` is `len(token_ids) - 1`.* The last token of the document has nothing after it, so it can never be an input. Stopping one short ensures no chunk starts there.

With `start` at most `len(token_ids) - 2`, every chunk contains at least two tokens, so the `if len(chunk) < 2` guard never triggers for a positive `context_length`; it is a safety net. In the same way, the earlier `len(token_ids) < 2` check is covered by the `range`, which would be empty anyway.

```python
            x = torch.tensor(
                chunk[:-1],
                dtype=torch.long,
            )

            y = torch.tensor(
                chunk[1:],
                dtype=torch.long,
            )

            yield x, y
```

**What Python/PyTorch does.** `chunk[:-1]` is the chunk without its last element; `chunk[1:]` is the chunk without its first. Both have length `len(chunk) - 1`. `torch.tensor(list, dtype=torch.long)` copies a Python list into a one-dimensional tensor of shape `[T]`, where `T` is that length. `dtype` is the type of the numbers stored; `torch.long` is another name for `torch.int64`, a 64-bit whole number. `yield x, y` yields a tuple of the two tensors.

**What it means in the LLM.** `x[i]` is the token the model sees at position `i`; `y[i]` is the token it should predict there, which is `x[i+1]`. The dtype must be an integer type because token ids are *indices*: the model uses each id to look up a row in its embedding table (chapter 7), and the loss uses each target id to pick one entry out of the model's output (chapter 8). PyTorch requires `long` for both. Ids are never to be treated as quantities: token `200` is not "twice" token `100`.

**A worked example, run for real.** A made-up stage-2 file with three documents:

```text
{"document_id": "doc-a", "input_ids": [256, 10, 11, 12, 13, 14, 15, 16, 17, 257]}
{"document_id": "doc-b", "input_ids": [256, 257]}
{"document_id": "doc-c", "input_ids": [256]}
```

`doc-a` has 10 tokens. With `context_length = 4`: `range(0, 9, 4)` gives `start = 0, 4, 8`.

| `start` | slice `[start : start+5]` | `chunk` | `x = chunk[:-1]` | `y = chunk[1:]` |
|---|---|---|---|---|
| `0` | `[0:5]` | `[256, 10, 11, 12, 13]` | `[256, 10, 11, 12]` | `[10, 11, 12, 13]` |
| `4` | `[4:9]` | `[13, 14, 15, 16, 17]` | `[13, 14, 15, 16]` | `[14, 15, 16, 17]` |
| `8` | `[8:13]` → only 2 tokens exist | `[17, 257]` | `[17]` | `[257]` |

Token `13` is the last target of the first chunk and the first input of the second: that is the one-token overlap. The third chunk is the **partial last chunk**: the document ran out, so `x` has length `1` instead of `4`. It is still yielded.

The real output of `for x, y in make_training_examples(path, 4): print(x, y, x.dtype, x.shape)`:

```text
tensor([256,  10,  11,  12]) tensor([10, 11, 12, 13]) torch.int64 torch.Size([4])
tensor([13, 14, 15, 16]) tensor([14, 15, 16, 17]) torch.int64 torch.Size([4])
tensor([17]) tensor([257]) torch.int64 torch.Size([1])
tensor([256]) tensor([257]) torch.int64 torch.Size([1])
```

The fourth line is `doc-b`: two tokens, one pair, "after BOS comes EOS". `doc-c` (one token) produced nothing. Count the pairs for `doc-a`: 4 + 4 + 1 = 9, which is exactly the number of adjacent pairs in a 10-token list.

The same file with other context lengths (real output, `doc-a` rows only):

```text
context_length = 3:  x=[256, 10, 11]  y=[10, 11, 12]
                     x=[12, 13, 14]   y=[13, 14, 15]
                     x=[15, 16, 17]   y=[16, 17, 257]        (divides evenly: no partial chunk)
context_length = 9:  x=[256, 10, 11, 12, 13, 14, 15, 16, 17]  y=[10, 11, 12, 13, 14, 15, 16, 17, 257]   (whole document in one example)
```

Things this function does *not* do, so you do not assume them: it does not shuffle (examples come in file order, the same every time); it does not group examples into batches (each yielded pair is a single example; the trainer adds the batch dimension itself, chapter 8); it does not pad short chunks to a fixed length (so the PAD token of 6.3 is never needed here); and chunks do not share context: the second chunk's `x` begins at token `13` with no memory of what came before it.

**On the real data.** The one training document has 259 tokens and `context_length` is `128`. `range(0, 258, 128)` gives `start = 0, 128, 256`, so one pass over the file yields exactly three examples with `x` shapes `[128]`, `[128]` and `[2]` (verified by running the function on the real file and printing only the shapes). 128 + 128 + 2 = 258 = 259 − 1. One epoch of training is therefore three steps.

Finally, because a generator is single-use, the trainer calls `make_training_examples(...)` afresh at the start of every epoch: each call reopens the file and streams it again from the first line.

#### What I should understand before moving on

- A split decides what the model may learn from (`train`) and what is kept back to measure it honestly (`validation` during development, `test` at the end). Splitting is done per document.
- `choose_split` is deterministic: SHA-256 of the id → first 8 hex digits → integer → `% 100` → a bucket from `0` to `99`; `0–89` train, `90–94` validation, `95–99` test.
- `assign_splits` overrides the hash in exactly one case, when train would be empty, by sending every document to train. That is the case today: one document, hash bucket `92`, moved to train; validation and test are empty.
- JSONL is one JSON object per line. Stage 1 records carry `document_id`, `batch_id`, `text`; stage 2 records carry `document_id`, `batch_id`, `input_ids`, `num_tokens`.
- A function with `yield` returns a generator: lazy, one item at a time, usable once. That is how files larger than memory are read.
- `make_training_examples` cuts each document into chunks of `context_length + 1` tokens, stepping by `context_length`; `x` is the chunk without its last token and `y` is the chunk without its first. Every adjacent token pair is used exactly once, the last chunk may be shorter, and no example crosses a document boundary.
- `x` and `y` are one-dimensional `int64` tensors of equal length, because token ids are indices.

#### Self-test

1. You rebuild the dataset after adding 50 new documents. Under the hash rule, which existing documents change split? What is the one situation in this code where an existing document *can* change split?
2. Compute by reasoning, not by running: if `digest[:8]` were `"00000064"`, which split would the document get?
3. Why would splitting a single long document half into train and half into validation give a misleading validation score?
4. A document has 7 token ids `[256, 1, 2, 3, 4, 5, 257]` and `context_length` is `3`. Write every `(x, y)` pair that `make_training_examples` yields.
5. Why does the slice take `context_length + 1` tokens while the loop steps by only `context_length`?
6. You write `examples = make_training_examples(path, 128)` and then loop over `examples` twice in a row. What happens in the second loop, and how does the trainer avoid the problem?
7. With today's data, what does a validation loss computed from `storage/training/tokenized/validation.jsonl` tell you?
8. `load_jsonl(Path("missing.jsonl"))` is called and the result is stored but never iterated. Is an error raised? Why?

<details><summary>Answers</summary>

1. None of them: each document's split depends only on its own id. The exception is the tiny-corpus rule: if train was empty before (so everything had been forced into train) and a new document now lands in train by hash, the rule stops firing and the forced documents go back to the split their hash gives them.
2. Hex `64` is decimal `100`. `100 % 100` is `0`. Bucket `0` is less than `90`, so `train`.
3. The two halves share topic, vocabulary and style, so the validation half is very similar to what the model trained on. The score would look good without showing that the model can handle text from a document it has never seen.
4. `range(0, 6, 3)` gives `start = 0, 3`. Chunk `[256, 1, 2, 3]` → `x = [256, 1, 2]`, `y = [1, 2, 3]`. Chunk `[3, 4, 5, 257]` → `x = [3, 4, 5]`, `y = [4, 5, 257]`. Two pairs, six predictions, equal to the six adjacent pairs in a 7-token list.
5. An input of `context_length` tokens needs `context_length` targets, and the target of the last input is one token further on, hence `+ 1`. Stepping by `context_length` makes that extra token the first input of the next chunk, so no adjacent pair is lost or repeated.
6. The second loop runs zero times, because the generator is already exhausted. The trainer calls `make_training_examples(...)` again inside the epoch loop, getting a fresh generator each epoch.
7. Nothing: the file is empty, so no examples are produced. All text is in train, so every measurement available today is on text the model has trained on.
8. No. Calling a generator function only creates the generator object; the body, including `path.open`, has not started. `FileNotFoundError` is raised at the first `next()` (or the first loop iteration).

</details>

## 6. Tokenization

| | |
|---|---|
| **INPUT** | Text: the `text` field of every record in `storage/training/dataset/train.jsonl` (to learn the tokenizer), and later any string at all (dataset text, a user's prompt). |
| **PROCESS** | Turn text into UTF-8 bytes, then repeatedly replace the most frequent adjacent pair of tokens with a new token (byte-pair encoding, BPE). Record the list of replacements ("merges"). Apply the same list to encode new text; reverse it to decode. |
| **OUTPUT** | The tokenizer file `artifacts/tokenizer/tokenizer.json` (41 merges, vocabulary size `300`), and the tokenized dataset `storage/training/tokenized/*.jsonl`. At run time: lists of integers ("token ids") from text, and text from lists of integers. |
| **WHY IT EXISTS** | A neural network computes with numbers, not letters. The tokenizer is the fixed, reversible dictionary between the two. The model's very first layer and very last layer are both sized by it. |

`src/tokenization/` contains two source files, `bpe.py` (125 lines) and `tokenizer.py` (237 lines), plus `__pycache__`. There is no `__init__.py` and no `.gitkeep` there. (A zero-byte `.gitkeep` does exist next to the output, in `artifacts/tokenizer/`; its only job is to make git keep that otherwise-empty directory.)

Driving scripts (code in chapter 12): `scripts/tokenizer_training.py` learns the merges from the train split and saves `tokenizer.json`; `scripts/tokenize_dataset.py` loads that file and encodes every document of every split into `storage/training/tokenized/`.

### 6.1 Why a tokenizer, and why byte-level BPE

**Text is not what the computer stores.** A Python `str` such as `"hello"` is a sequence of *characters*: abstract symbols, each identified by a number called a Unicode code point (`h` is `104`, `م` is `1605`, `😀` is `128512`). A file on disk, a network packet, or memory is a sequence of *bytes*: whole numbers from `0` to `255`. An *encoding* is the rule for turning characters into bytes and back. This project uses UTF-8 everywhere, which is the standard.

Python keeps the two worlds apart with two types:

| | `str` (text) | `bytes` |
|---|---|---|
| Written as | `"hello"` | `b"hello"` or `b'\xd9\x85'` |
| An element is | a character | an integer `0`–`255` |
| Go to the other | `"hello".encode("utf-8")` | `b"hello".decode("utf-8")` |
| As a list of numbers | — | `list(b"hello")` → `[104, 101, 108, 108, 111]` |

When Python prints a `bytes` object it shows printable ASCII bytes as letters (`b'h'`) and everything else as `\x` followed by two hex digits (`b'\xd8\xa7'` is the two bytes `216, 167`). The data is the same; only the display differs.

**UTF-8 uses a different number of bytes for different characters.** Real output of `list(ch.encode("utf-8"))`:

| Character | Code point | UTF-8 bytes | Same bytes in binary |
|---|---|---|---|
| `h` | 104 | `[104]` | `01101000` |
| `é` | 233 | `[195, 169]` | `11000011 10101001` |
| `م` | 1605 | `[217, 133]` | `11011001 10000101` |
| `€` | 8364 | `[226, 130, 172]` | `11100010 10000010 10101100` |
| `😀` | 128512 | `[240, 159, 152, 128]` | `11110000 10011111 10011000 10000000` |

The rule behind the table:

| Code point range | Bytes | Bit pattern (`x` = bits of the code point) | First byte is in |
|---|---|---|---|
| 0 – 127 (ASCII: English letters, digits, space, newline) | 1 | `0xxxxxxx` | 0–127 |
| 128 – 2047 (accented Latin, Greek, Hebrew, **Arabic**, …) | 2 | `110xxxxx 10xxxxxx` | 194–223 |
| 2048 – 65535 (most other scripts, `€`) | 3 | `1110xxxx 10xxxxxx 10xxxxxx` | 224–239 |
| 65536 and above (emoji, rare scripts) | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 240–244 |

The first byte of a multi-byte character (the *lead byte*) announces by its top bits how many bytes follow. Every following byte (a *continuation byte*) starts with the bits `10`, which means it lies between `128` and `191`. A continuation byte can never be mistaken for the start of a character.

**Why Arabic letters take two bytes.** One byte of the form `0xxxxxxx` has 7 free bits, enough for 128 values, and those are all taken by ASCII. Arabic letters have code points between 1536 and 1791, which need 11 bits; the two-byte form `110xxxxx 10xxxxxx` has exactly 5 + 6 = 11 free bits. Take `م`, code point 1605, which is `11001000101` in binary. Split it 5 + 6: `11001` and `000101`. Insert into the pattern: `110`+`11001` = `11011001` = `217`, and `10`+`000101` = `10000101` = `133`. So `م` is `[217, 133]`. In practice almost every Arabic letter you will meet starts with lead byte `216` or `217`; the second byte tells them apart.

That is why the made-up word `"مرحبا"` is 5 characters but 10 bytes:

```text
list("مرحبا".encode("utf-8")) -> [217, 133, 216, 177, 216, 173, 216, 168, 216, 167]
                                  م         ر         ح         ب         ا
```

Half a character is not a character. The single byte `216` on its own is not valid UTF-8, and neither is `[217, 133, 216]` (one letter and half of the next). This becomes important in 6.3 and again in chapter 10.

**From bytes to token ids.** A *token* is one unit of the model's vocabulary; a *token id* is the integer naming it. The model has one row of numbers per token id (chapter 7), so the vocabulary must be a fixed, finite list. The design options:

| Vocabulary | Problem |
|---|---|
| One token per word | Unbounded: new words, typos and names appear forever, and need an "unknown" token that destroys information. Arabic, with prefixes and suffixes attached to words, makes it worse. |
| One token per character | Unicode has well over a hundred thousand characters; most would never be seen in training, and an unseen one still needs "unknown". |
| **One token per byte** | Only 256 possible values, and *every* string in *every* language is made of them. Nothing can be unknown. But sequences are long: one Arabic letter costs two tokens. |

This project starts from bytes and then shortens the sequences with BPE. The full id space is:

| Ids | Count | Meaning |
|---|---|---|
| `0` – `255` | 256 | The **base vocabulary**: token id `n` *is* the byte with value `n`. Token `104` is the byte for `h`; token `216` is an Arabic lead byte. |
| `256` | 1 | **BOS**, "beginning of sequence". |
| `257` | 1 | **EOS**, "end of sequence". |
| `258` | 1 | **PAD**, "padding". |
| `259` – `299` | 41 | **Merged tokens**, each standing for two or more bytes, learned from the corpus. |

**Special tokens** (this is their home in the document) are ids that stand for no bytes at all. They are signals to the model, not text:

- **BOS** is put at the start of every document. It gives the model a fixed first input, so that there is something to predict the first real token *from*.
- **EOS** is put at the end of every document. The model learns "after text like this, the document ends", and at generation time producing EOS is how it says "I am done" (chapter 10).
- **PAD** is a filler used when several sequences of different lengths must be stacked into one rectangular batch. This project defines it and reserves the id, but nothing currently inserts it: training feeds one example at a time (chapter 8), and the real tokenized file contains zero PAD tokens.

They sit at `256`, `257`, `258`, immediately after the bytes, for a precise reason: no byte can have a value above `255`, so encoding text can never produce these ids by accident. Typing the five characters `<BOS>` into a prompt gives `[60, 66, 79, 83, 62]` (the bytes of `<`, `B`, `O`, `S`, `>`), not `256` (verified). The special ids enter a sequence only when code puts them there deliberately.

**Merges.** BPE looks at the training text as token sequences and asks: which two tokens appear next to each other most often? It invents a new token id meaning "those two, glued", replaces every occurrence, and repeats. Each such decision is one *merge*, written as a pair `(left, right)`. The first merge gets id `259`, the next `260`, and so on. A later merge may glue tokens that are themselves merges, so tokens grow: byte → letter → pair of letters → whole word. The ordered list of merges *is* the tokenizer; nothing else is learned.

What that buys: shorter sequences. The real training document is 536 bytes; after 41 merges it is 257 tokens. The model's context window of 128 tokens therefore covers roughly twice as much text, and each prediction is a larger step.

### 6.2 Learning the merges: `src/tokenization/bpe.py`

| | |
|---|---|
| **INPUT** | An iterable of strings (one per document) and a target vocabulary size. |
| **PROCESS** | Convert each document to a list of byte values; count adjacent pairs across all documents; merge the most frequent pair into a new id; repeat until the target size is reached or no pair occurs twice. |
| **OUTPUT** | A `BPEModel` holding the ordered tuple of merges. |
| **WHY IT EXISTS** | This is the "training" of the tokenizer. It is a counting algorithm with no neural network and no randomness. |

#### `src/tokenization/bpe.py`

**Why this file exists.** It defines the id layout (the constants), the two primitive operations of BPE (count pairs, merge a pair), and the training loop built from them.

**What enters / what leaves.** `train_bpe(texts, target_vocab_size)` returns a `BPEModel`. It reads and writes no files; it prints one line per merge.

**How it connects.** `scripts/tokenizer_training.py` calls `train_bpe` with `load_texts(train.jsonl)` (chapter 5) and `target_vocab_size=300`, then wraps the result in a `Tokenizer` (6.3) and saves it. `tokenizer.py` imports the constants, `BPEModel` and `merge_pair` from here, so encoding uses the very same merge function as training.

**The code, section by section.**

```python
from collections import Counter
from dataclasses import dataclass
from collections.abc import Iterable
```

| Import | What it is | Why this file needs it |
|---|---|---|
| `Counter` | A dictionary specialised for counting: a missing key counts as `0`, and `.most_common(n)` returns the `n` highest counts. | Counting how often each pair occurs. |
| `dataclass` | Decorator that writes a class's `__init__` and friends from its field list (primer in 1). | `BPEModel`. |
| `Iterable` | Type name for "anything a `for` loop can go over": a list, a generator, … | Type hint for `texts`, which in practice is the generator from `load_texts`. |

```python
Pair = tuple[int, int]

BYTE_VOCAB_SIZE = 256

BOS_ID = 256
EOS_ID = 257
PAD_ID = 258

FIRST_MERGE_ID = 259
```

`Pair = tuple[int, int]` is a *type alias*: a short name for "a tuple of two integers", used in the hints below. It creates no objects.

The constants are the id layout from 6.1, written down once:

| Constant | Value | Meaning |
|---|---|---|
| `BYTE_VOCAB_SIZE` | `256` | Number of byte tokens, ids `0`–`255`. Defined here but not referenced anywhere else in the project; the code that needs the number writes `256` directly. |
| `BOS_ID` | `256` | Beginning-of-sequence. |
| `EOS_ID` | `257` | End-of-sequence. |
| `PAD_ID` | `258` | Padding. |
| `FIRST_MERGE_ID` | `259` | The id given to the first learned merge. Everything from here upward is a merged token. |

These numbers are frozen into every tokenized file and every trained checkpoint. Changing one of them would silently change the meaning of data already on disk.

```python
@dataclass(frozen=True)
class BPEModel:
    merges: tuple[Pair, ...]

    @property
    def vocab_size(self) -> int:
        return FIRST_MERGE_ID + len(self.merges)
```

The whole trained tokenizer model is one field: `merges`, a tuple of pairs. `tuple[Pair, ...]` reads "a tuple of any length whose elements are all `Pair`s". Position matters: `merges[0]` created token `259`, `merges[1]` created `260`, in general `merges[i]` created `FIRST_MERGE_ID + i`. The new ids are not stored because they follow from the position.

`frozen=True` makes instances read-only: assigning `model.merges = …` raises `FrozenInstanceError` (verified). Together with using a tuple (which cannot be changed in place) rather than a list, this protects the merge order from accidental modification, and the order is everything.

`@property` lets a method be read like an attribute: `model.vocab_size`, no parentheses. The value is `259 + number of merges`: 256 bytes + 3 specials + the merges. With 41 merges that is `300`. This single number sizes the model's embedding table and output layer (chapter 7).

```python
def count_pairs(
    sequences: list[list[int]],
) -> Counter[Pair]:
    counts: Counter[Pair] = Counter()

    for tokens in sequences:
        for left, right in zip(
            tokens,
            tokens[1:],
        ):
            counts[(left, right)] += 1

    return counts
```

`sequences` is a list of documents, each a list of token ids. The function returns how many times each adjacent pair occurs, over all documents together.

**What Python does.** `tokens[1:]` is the list without its first element. `zip(a, b)` walks two sequences in step and stops at the shorter one. Zipping a list with itself shifted by one gives every adjacent pair: for `[97, 97, 98]` it yields `(97, 97)` then `(97, 98)`. `counts[(left, right)] += 1` uses the tuple as a dictionary key and adds one; a `Counter` treats a missing key as `0`, so no "is it there yet?" check is needed. (`counts: Counter[Pair] = Counter()` is an empty counter with a type hint.)

**What it means in the tokenizer.** The `zip` runs *inside* the loop over documents, once per document. The last token of one document is never paired with the first token of the next, so the count never includes a pair that straddles two documents. Note also that overlapping occurrences all count: in `[97, 97, 97]` the pair `(97, 97)` is counted twice.

```python
def merge_pair(
    tokens: list[int],
    pair: Pair,
    new_token_id: int,
) -> list[int]:
    output = []
    index = 0

    while index < len(tokens):
        if (
            index + 1 < len(tokens)
            and tokens[index] == pair[0]
            and tokens[index + 1] == pair[1]
        ):
            output.append(new_token_id)
            index += 2

        else:
            output.append(tokens[index])
            index += 1

    return output
```

Takes one sequence and returns a *new* list in which every occurrence of `pair` has been replaced by `new_token_id`. The input list is not modified.

Step by step: `index` walks the list from the left. At each position the `if` asks three things joined by `and`: is there a next element at all (`index + 1 < len(tokens)`, which prevents reading past the end), does the current token equal the pair's left half, does the next token equal its right half? If all three hold, the new id is appended and `index` jumps forward by 2, consuming both tokens. Otherwise the current token is copied and `index` moves by 1. `and` stops at the first false condition, so `tokens[index + 1]` is never evaluated when it would be out of range.

Because matched tokens are consumed, replacements are left-to-right and never overlap. Real output: `merge_pair([97, 97, 97, 97, 97], (97, 97), 259)` → `[259, 259, 97]`: two pairs replaced, one `97` left over.

This one function does double duty: training calls it to apply each newly chosen merge, and `Tokenizer.encode` (6.3) calls it to replay the merges on new text. Using the same code for both guarantees that text is encoded exactly the way the merges were learned.

```python
def train_bpe(
    texts: Iterable[str],
    target_vocab_size: int,
) -> BPEModel:
    if target_vocab_size < FIRST_MERGE_ID:
        raise ValueError(
            f"Byte-level BPE vocab must be at least "
            f"{FIRST_MERGE_ID}"
        )
```

`texts`: the documents. `target_vocab_size`: the vocabulary size to aim for. The 259 ids for bytes and specials always exist, so a target below 259 is impossible and is rejected (`train_bpe(["x"], 258)` raises `Byte-level BPE vocab must be at least 259`). A target of exactly `259` is accepted and means "no merges".

**What `target_vocab_size=300` means.** The script passes `300`. Since 259 ids are fixed, that leaves room for `300 − 259 = 41` merges, ids `259` to `299`. It is a ceiling, not a promise: the loop below can stop earlier.

```python
    # Keep every document as an independent sequence.
    # BPE must not learn merges across document boundaries.
    sequences = [
        list(text.encode("utf-8"))
        for text in texts
        if text
    ]

    if not sequences:
        raise ValueError(
            "Cannot train tokenizer on an empty corpus"
        )
```

**What Python does.** A list comprehension with a filter. For each `text`, `text.encode("utf-8")` gives its bytes and `list(...)` turns those into a list of integers `0`–`255`, the starting token sequence. `if text` skips empty strings. The result is a list of lists, one inner list per document. If `texts` is a generator (it is), this line consumes it completely: from here on, the whole training text is in memory as integers. An empty result (no documents, or only empty ones) raises the error; this is the failure the tiny-corpus rule of chapter 5 prevents.

**What it means in the tokenizer: why merges must not cross document boundaries.** The alternative would be to glue all documents into one long sequence. Then the last byte of one document and the first byte of the next would sit side by side and be counted as a pair, although no author ever wrote them together. Which documents happen to be neighbours is an accident of file order, so such pairs are noise, and a merge learned from them would describe the order of your files rather than the language. Keeping one list per document, combined with `count_pairs` zipping within each list, makes it impossible. Real output for the difference:

```text
count_pairs([list(b"ababab")])                       -> Counter({(97, 98): 3, (98, 97): 2})
count_pairs([list(b"ab"), list(b"ab"), list(b"ab")]) -> Counter({(97, 98): 3})
```

As one sequence, `b` followed by `a` is seen twice. As three documents, it is never seen, which is the truth: no document contains `ba`.

Notice also that these sequences contain only byte values. BOS and EOS are not present during tokenizer training, so no merge can ever include a special token.

```python
    merges: list[Pair] = []
    next_token_id = FIRST_MERGE_ID

    while next_token_id < target_vocab_size:
        pair_counts = count_pairs(sequences)

        if not pair_counts:
            break
```

`merges` collects the chosen pairs in order. `next_token_id` is the id the next merge will receive, starting at `259`. The `while` loop runs one merge per pass and ends when the next id would reach the target (ids `259`…`299` for a target of `300`).

Each pass recounts all pairs from scratch over the current sequences. `if not pair_counts: break` stops when there are no pairs left at all, which happens when every document has shrunk to a single token (or was one byte long to begin with).

```python
        best_pair, frequency = (
            pair_counts.most_common(1)[0]
        )

        # A pair occurring once is not useful for this MVP.
        if frequency < 2:
            break
```

`pair_counts.most_common(1)` returns a list with the single highest entry, like `[((97, 97), 4)]`. `[0]` takes that entry, and the assignment unpacks it into the pair and its count. When several pairs share the highest count, `most_common` returns the one that was counted first, which is the one that appears earliest in the text. So ties are broken by position, and the result is fully deterministic: same texts in the same order, same merges.

`if frequency < 2: break` is the second early exit. If the best pair occurs only once, a merge would save one token in one place while spending a vocabulary id; the code stops instead. This is why `target_vocab_size` is a ceiling: `train_bpe(["abc"], 300)` returns a model with zero merges.

```python
        sequences = [
            merge_pair(
                tokens=tokens,
                pair=best_pair,
                new_token_id=next_token_id,
            )
            for tokens in sequences
        ]

        merges.append(best_pair)
```

The chosen merge is applied to every document: each sequence is replaced by its merged version, and the pair is recorded. After this, the sequences contain the new id, so the next pass can count pairs that involve it. That is how merges stack.

```python
        print(
            f"merge {next_token_id}: "
            f"{best_pair} "
            f"frequency={frequency}"
        )

        next_token_id += 1

    return BPEModel(
        merges=tuple(merges)
    )
```

One progress line per merge, then move to the next id. After the loop, the list is frozen into a tuple and wrapped in a `BPEModel`.

**A complete training by hand.** Take the made-up string `"aaabdaaabac"` as a one-document corpus. Its bytes (`a`=97, `b`=98, `c`=99, `d`=100):

```text
[97, 97, 97, 98, 100, 97, 97, 97, 98, 97, 99]          11 tokens
```

*Merge 1.* Count adjacent pairs:

| Pair | Meaning | Count |
|---|---|---|
| `(97, 97)` | `aa` | 4 (each `aaa` contains two overlapping `aa`) |
| `(97, 98)` | `ab` | 2 |
| `(98, 100)` | `bd` | 1 |
| `(100, 97)` | `da` | 1 |
| `(98, 97)` | `ba` | 1 |
| `(97, 99)` | `ac` | 1 |

Most frequent: `(97, 97)`. It becomes token `259`. Replace left to right; in each `97, 97, 97` the first two are consumed and the third remains:

```text
[259, 97, 98, 100, 259, 97, 98, 97, 99]                9 tokens
```

The count said 4 but only 2 replacements happened, because overlapping occurrences cannot both be merged.

*Merge 2.* Recount: `(259, 97)`: 2, `(97, 98)`: 2, `(98, 100)`: 1, `(100, 259)`: 1, `(98, 97)`: 1, `(97, 99)`: 1. A tie at 2. `(259, 97)` was met first in the sequence, so it wins and becomes token `260` (which stands for `aaa`):

```text
[260, 98, 100, 260, 98, 97, 99]                        7 tokens
```

*Merge 3.* Recount: `(260, 98)`: 2, and `(98, 100)`, `(100, 260)`, `(98, 97)`, `(97, 99)` once each. `(260, 98)` becomes token `261` (`aaab`):

```text
[261, 100, 261, 97, 99]                                5 tokens
```

*Stop.* Recount: `(261, 100)`, `(100, 261)`, `(261, 97)`, `(97, 99)`, each once. The best frequency is 1, which is below 2, so the loop breaks, with only 3 of the 41 allowed merges used.

Now the real code. `train_bpe(["aaabdaaabac"], 300)` prints and returns:

```text
merge 259: (97, 97) frequency=4
merge 260: (259, 97) frequency=2
merge 261: (260, 98) frequency=2
BPEModel(merges=((97, 97), (259, 97), (260, 98)))      vocab_size = 262
```

and the intermediate `count_pairs` / `merge_pair` results printed by the real functions match the tables above exactly, including the tie-break. A tokenizer built from this model encodes `"aaabdaaabac"` as `[261, 100, 261, 97, 99]`.

**What happened on the real corpus.** `scripts/tokenizer_training.py` ran this on the one training document (536 bytes) with target `300`. All 41 merges were found before the frequency dropped below 2: the first, `(216, 167)`, occurred 34 times; the last, `(298, 284)`, occurred twice. The resulting `vocab_size` is exactly `300`, which is the same number written as the default in `src/model/config.py`. Re-running `train_bpe` in memory on the current `train.jsonl` reproduces the 41 merges stored in `tokenizer.json`, so the saved tokenizer and the dataset are in step. With 41 merges learned from 536 bytes, the vocabulary is closely fitted to that one document; several of the last merges are whole words from it.

### 6.3 Using the merges: `src/tokenization/tokenizer.py`

| | |
|---|---|
| **INPUT** | A `BPEModel` (fresh from `train_bpe`, or rebuilt from `tokenizer.json`), then text to encode or token ids to decode. |
| **PROCESS** | Encode: text → UTF-8 bytes → replay every merge in learned order → optionally add BOS/EOS. Decode: look up each id's bytes → join → decode as UTF-8. |
| **OUTPUT** | `list[int]` from `encode`; `str` from `decode`; `bytes` from the two byte helpers; a JSON file from `save`. |
| **WHY IT EXISTS** | `bpe.py` learns the merges once. This class is what every later stage actually holds and calls: dataset tokenization, inference, and the server. |

#### `src/tokenization/tokenizer.py`

**Why this file exists.** It wraps a `BPEModel` in an object with the operations the rest of the project needs: encode, decode, look up a token's bytes, save to disk, load from disk.

**What enters / what leaves.** Construction takes a `BPEModel`. `save(path)` writes one JSON file; `Tokenizer.load(path)` reads it. Everything else is in-memory conversion between `str`, `bytes` and `list[int]`.

**How it connects.** Created by `scripts/tokenizer_training.py` (then saved). Loaded by `scripts/tokenize_dataset.py` (encodes each document with `add_bos=True, add_eos=True`), by `scripts/inference.py` and `scripts/model_stats.py`, and by `src/serving/model_manager.py`. `src/inference/generator.py` uses `encode`, `decode`, `token_to_bytes`, `tokens_to_bytes`, `vocab_size`, `bos_id`, `eos_id` and `pad_id` (chapter 10).

**The code, section by section.**

```python
import json
from pathlib import Path

from src.tokenization.bpe import (
    BPEModel,
    BOS_ID,
    EOS_ID,
    PAD_ID,
    FIRST_MERGE_ID,
    merge_pair,
)
```

`json` and `Path` are for `save` and `load`. From `bpe.py` come the model class, the four id constants, and `merge_pair`. `count_pairs` and `train_bpe` are not imported: this file never learns anything, it only applies what was learned.

```python
class Tokenizer:
    def __init__(
        self,
        model: BPEModel,
    ):
        self.model = model

        self._token_bytes = {
            token_id: bytes([token_id])
            for token_id in range(256)
        }
```

`__init__` runs when you write `Tokenizer(model)`. It stores the model and then builds `self._token_bytes`, a dictionary from token id to the bytes that token stands for. The leading underscore is the Python convention for "internal; use the methods instead".

**What Python does.** `bytes([n])` builds a `bytes` object of length one containing the value `n`: `bytes([104])` is `b'h'`. The dict comprehension does this for `0` through `255`.

**What it means in the tokenizer.** This is the base vocabulary made concrete: token `n` ↔ the single byte `n`.

```python
        for index, pair in enumerate(
            self.model.merges
        ):
            token_id = FIRST_MERGE_ID + index

            self._token_bytes[token_id] = (
                self._token_bytes[pair[0]]
                + self._token_bytes[pair[1]]
            )
```

Now the merged tokens. `enumerate` gives each merge with its position; the token id is `259 + index`, the same rule training used. The bytes of a merged token are the bytes of its left half followed by the bytes of its right half (`+` on `bytes` joins them).

This works only because the merges are processed in order: by the time merge number `index` is handled, both halves of its pair are either bytes (already in the dictionary) or earlier merges (added in a previous iteration). A merge can never refer to a later one. With the hand-trained model from 6.2: `259` → `b'aa'`; `260` = `(259, 97)` → `b'aa' + b'a'` = `b'aaa'`; `261` = `(260, 98)` → `b'aaab'` (verified).

The dictionary ends up with `256 + len(merges)` entries. Ids `256`, `257`, `258` are deliberately absent: special tokens have no bytes.

```python
    @property
    def vocab_size(self) -> int:
        return self.model.vocab_size

    @property
    def bos_id(self) -> int:
        return BOS_ID

    @property
    def eos_id(self) -> int:
        return EOS_ID

    @property
    def pad_id(self) -> int:
        return PAD_ID
```

Four read-only attributes. `tokenizer.vocab_size` forwards to the model (`259 + merges`, `300` for the trained tokenizer). The other three return the module constants, so code holding a tokenizer can write `tokenizer.eos_id` without importing from `bpe.py`. `vocab_size` counts the three special ids even though they have no bytes: the model needs a row for each of them.

```python
    def encode(
        self,
        text: str,
        add_bos: bool = False,
        add_eos: bool = False,
    ) -> list[int]:

        tokens = list(
            text.encode("utf-8")
        )
```

`encode` turns a string into token ids. `add_bos` and `add_eos` default to `False`, so a plain `encode(text)` returns only the text's tokens. First step, identical to training: text → UTF-8 bytes → list of integers `0`–`255`.

```python
        for index, pair in enumerate(
            self.model.merges
        ):
            new_token_id = (
                FIRST_MERGE_ID + index
            )

            tokens = merge_pair(
                tokens=tokens,
                pair=pair,
                new_token_id=new_token_id,
            )
```

**What Python does.** For every merge, in learned order, make one full pass over the sequence with `merge_pair`, replacing that pair by its id. With 41 merges that is 41 passes, whether or not a given pair occurs in this text.

**What it means in the tokenizer.** Encoding is a replay of training on new text. The order is essential: merge `261` in the trained tokenizer is `(259, 216)`, which can match only after merge `259` has already created some `259` tokens. Applying merges in a different order would produce different, wrong ids. And because nothing here depends on chance or on other texts, the same string always encodes to the same ids.

```python
        if add_bos:
            tokens.insert(
                0,
                BOS_ID,
            )

        if add_eos:
            tokens.append(
                EOS_ID
            )

        return tokens
```

`tokens.insert(0, BOS_ID)` puts `256` at the front; `tokens.append(EOS_ID)` puts `257` at the end. They are added *after* merging, so the special tokens never take part in a merge. Who asks for what:

| Caller | Flags | Why |
|---|---|---|
| `scripts/tokenize_dataset.py` | `add_bos=True, add_eos=True` | A training document is a complete unit: it starts, and it ends. |
| A prompt at generation time (chapter 10) | see that chapter | A prompt is a beginning that the model should continue, so ending it with EOS would tell the model the text is already over. |

`encode("")` returns `[]`, and `encode("", add_bos=True, add_eos=True)` returns `[256, 257]` (verified).

```python
    def token_to_bytes(
        self,
        token_id: int,
    ) -> bytes:

        if token_id in {
            BOS_ID,
            EOS_ID,
            PAD_ID,
        }:
            return b""

        if token_id not in self._token_bytes:
            raise ValueError(
                f"Unknown token id: {token_id}"
            )

        return self._token_bytes[token_id]
```

One id → its bytes. `{BOS_ID, EOS_ID, PAD_ID}` is a set literal, and `in` tests membership. A special token returns `b""`, the empty bytes object: it contributes nothing to the text. An id that is not in the dictionary (for the trained tokenizer, anything `300` or above, or negative) raises `ValueError`, for example `Unknown token id: 300`. Otherwise the stored bytes are returned.

Chapter 10 relies on this method: before accepting a candidate next token, the generator looks at its bytes to check whether they would keep the output valid UTF-8.

```python
    def tokens_to_bytes(
        self,
        token_ids: list[int],
    ) -> bytes:

        parts = []

        for token_id in token_ids:
            if token_id in {
                BOS_ID,
                EOS_ID,
                PAD_ID,
            }:
                continue

            parts.append(
                self.token_to_bytes(
                    token_id
                )
            )

        return b"".join(parts)
```

A list of ids → all their bytes joined. `b"".join(parts)` concatenates a list of `bytes` objects with nothing between them. Special tokens are skipped with `continue` (they would have contributed `b""` anyway, so the result is the same either way). This method stops at bytes and never attempts to turn them into text, so it cannot fail on an incomplete character. Real output: `tokens_to_bytes([256, 104, 257])` → `b'h'`.

```python
    def decode(
        self,
        token_ids: list[int],
        skip_special_tokens: bool = True,
        errors: str = "strict",
    ) -> str:

        data_parts = []

        for token_id in token_ids:
            if token_id in {
                BOS_ID,
                EOS_ID,
                PAD_ID,
            }:
                if skip_special_tokens:
                    continue

                raise ValueError(
                    "Cannot decode special token as text"
                )

            data_parts.append(
                self.token_to_bytes(
                    token_id
                )
            )
```

`decode` goes all the way from ids to a `str`. The loop gathers bytes like `tokens_to_bytes`, with one difference in how special tokens are treated:

- `skip_special_tokens=True` (the default): special tokens are silently dropped. `decode([256, 104, 105, 257, 258])` → `'hi'`.
- `skip_special_tokens=False`: meeting a special token raises `ValueError("Cannot decode special token as text")`. Read the name carefully: `False` does not mean "show them as `<BOS>`". It means "special tokens are not allowed here; fail if one appears". There is no mode that renders them as text.

```python
        return b"".join(
            data_parts
        ).decode(
            "utf-8",
            errors=errors,
        )
```

**What Python does.** Join all the bytes, then call `bytes.decode("utf-8", errors=errors)` to interpret them as text. The `errors` argument is passed straight through to Python and decides what happens when the bytes are not valid UTF-8:

| `errors` | Behaviour on invalid bytes |
|---|---|
| `"strict"` (default) | Raise `UnicodeDecodeError`. |
| `"replace"` | Put the replacement character `�` (U+FFFD) where the bad bytes are. |
| `"ignore"` | Drop the bad bytes silently. |

**What it means in the LLM.** Bytes produced by `encode` always decode cleanly, because they came from real text. But a model generates tokens one at a time and can stop anywhere, or choose a token whose bytes do not continue the previous ones legally. Then the byte string is not valid UTF-8, and this last step is where it shows. The default is `"strict"` on purpose: a broken character raises an error instead of being quietly hidden.

```python
    def save(
        self,
        path: Path,
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
```

`save` writes the tokenizer to a JSON file. `-> None` says it returns nothing. `path.parent` is the directory containing the file; `mkdir(parents=True, exist_ok=True)` creates it, along with any missing directories above it, and does not complain if it already exists.

```python
        data = {
            "type": "byte_level_bpe",
            "version": "1.0.0",

            "base_vocab_size": 256,

            "special_tokens": {
                "bos": {
                    "token": "<BOS>",
                    "id": BOS_ID,
                },
                "eos": {
                    "token": "<EOS>",
                    "id": EOS_ID,
                },
                "pad": {
                    "token": "<PAD>",
                    "id": PAD_ID,
                },
            },

            "first_merge_id": FIRST_MERGE_ID,
            "vocab_size": self.vocab_size,

            "merges": [
                [left, right]
                for left, right
                in self.model.merges
            ],
        }
```

A plain dictionary describing the tokenizer. This is the file format:

| Key | Value in the real file | Meaning |
|---|---|---|
| `type` | `"byte_level_bpe"` | A label for the kind of tokenizer. |
| `version` | `"1.0.0"` | A label for the format version. |
| `base_vocab_size` | `256` | Ids `0`–`255` are raw bytes. |
| `special_tokens` | `bos`→`256`, `eos`→`257`, `pad`→`258` | Each entry has a display name (`"<BOS>"`, …) and its id. The display names are for humans reading the file; no code matches text against them. |
| `first_merge_id` | `259` | Id of the first merge. |
| `vocab_size` | `300` | `259 + len(merges)`. |
| `merges` | a list of 41 two-element lists | The learned pairs, in order. Entry `i` created token `259 + i`. |

JSON has no tuple type, so each `(left, right)` tuple is written as a two-element list; the list comprehension does that conversion.

```python
        path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
```

`json.dumps` turns the dictionary into a JSON string. `indent=2` pretty-prints it with two-space indentation (which puts every number of every merge on its own line). `ensure_ascii=False` lets non-ASCII characters be written as themselves instead of `\uXXXX` escapes; this file contains only ASCII, so here it makes no visible difference. `path.write_text(..., encoding="utf-8")` writes the string to the file, replacing any existing file. This is a direct write, not the "write to `.tmp` then replace" pattern of 4.1.

The real `artifacts/tokenizer/tokenizer.json` is 1,734 bytes. Its structure, with the middle of the merge list left out and the layout compacted:

```text
{
  "type": "byte_level_bpe",
  "version": "1.0.0",
  "base_vocab_size": 256,
  "special_tokens": {
    "bos": {"token": "<BOS>", "id": 256},
    "eos": {"token": "<EOS>", "id": 257},
    "pad": {"token": "<PAD>", "id": 258}
  },
  "first_merge_id": 259,
  "vocab_size": 300,
  "merges": [[216, 167], [217, 133], [259, 216], [32, 216], [217, 132], [217, 138], ... 35 more ...]
}
```

Reading the first merges tells you what BPE found in an Arabic corpus:

| Id | Pair | Bytes of the new token | What it is |
|---|---|---|---|
| `259` | `(216, 167)` | `[216, 167]` | The letter `ا`. The two bytes of the most frequent letter become one token. |
| `260` | `(217, 133)` | `[217, 133]` | The letter `م`. |
| `261` | `(259, 216)` | `[216, 167, 216]` | `ا` followed by the *lead byte* of the next letter. One and a half characters. |
| `262` | `(32, 216)` | `[32, 216]` | A space followed by a lead byte. Half a character again. |
| `263` | `(217, 132)` | `[217, 132]` | The letter `ل`. |
| `264` | `(217, 138)` | `[217, 138]` | The letter `ي`. |

Tokens `261` and `262` show something that surprises most people: **BPE has no idea what a character is.** It counts bytes. "`ا` then byte `216`" is frequent simply because many letters start with `216`, so it was merged, producing a token that ends in the middle of a character. There is also a token (`283`) that *begins* with a continuation byte. Tokens like these are legitimate and encode/decode correctly inside a full sequence, but on their own they are not valid text. Later merges build up: by the end of the list there are tokens covering whole words, the longest being 12 bytes (six Arabic letters).

```python
    @classmethod
    def load(
        cls,
        path: Path,
    ) -> "Tokenizer":

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
```

`@classmethod` makes `load` a method you call on the class, not on an existing object: `Tokenizer.load(path)`. Its first parameter `cls` is the class itself (the counterpart of `self`). It is the standard way to write an alternative constructor, "build me one from a file". The return type is written as the string `"Tokenizer"` because, at the moment Python reads this line, the class `Tokenizer` is still being defined and the name does not exist yet; quoting it defers the lookup.

`path.read_text(encoding="utf-8")` reads the whole file as a string and `json.loads` parses it into a dictionary.

```python
        merges = tuple(
            (left, right)
            for left, right
            in data["merges"]
        )

        return cls(
            BPEModel(
                merges=merges
            )
        )
```

The reverse of `save`: each two-element list becomes a tuple again (a generator expression inside `tuple(...)`, primer in 1), the tuples go into a `BPEModel`, and `cls(...)` calls `Tokenizer.__init__`, which rebuilds `_token_bytes`.

Only one key of the file is read: `"merges"`. The other keys (`type`, `version`, `base_vocab_size`, `special_tokens`, `first_merge_id`, `vocab_size`) are written for the benefit of someone reading the file and are not checked on load. The special ids and the first merge id always come from the constants in `bpe.py`, whatever the file says.

**A real round trip.** All output below is from the trained tokenizer, `Tokenizer.load(Path("artifacts/tokenizer/tokenizer.json"))`.

English, `"i love coffee"` (13 characters, 13 bytes):

```text
encode("i love coffee")
  -> [105, 32, 108, 111, 118, 101, 32, 99, 111, 102, 102, 101, 101]                     13 tokens
encode("i love coffee", add_bos=True, add_eos=True)
  -> [256, 105, 32, 108, 111, 118, 101, 32, 99, 111, 102, 102, 101, 101, 257]           15 tokens
decode(that)  -> 'i love coffee'
```

Every token is a raw byte: `105` is `i`, `32` is the space, `108` is `l`, and so on. Not one merge applied, because the merges were learned from Arabic text and none of these byte pairs was frequent there. The tokenizer still handles English perfectly; it just does not compress it. A tokenizer is fitted to its training corpus.

Arabic, `"مرحبا"` (5 characters, 10 bytes):

```text
bytes:   [217, 133, 216, 177, 216, 173, 216, 168, 216, 167]                              10 byte tokens
encode("مرحبا") -> [260, 266, 216, 173, 273, 259]                                         6 tokens
```

The merges that fired, in order (each line is the sequence after that merge):

```text
merge 259 (216, 167):  [217, 133, 216, 177, 216, 173, 216, 168, 259]
merge 260 (217, 133):  [260, 216, 177, 216, 173, 216, 168, 259]
merge 266 (216, 177):  [260, 266, 216, 173, 216, 168, 259]
merge 273 (216, 168):  [260, 266, 216, 173, 273, 259]
```

The byte view of the result, token by token (`token_to_bytes` on each id):

| Token id | Bytes | Text |
|---|---|---|
| `260` | `[217, 133]` | `م` |
| `266` | `[216, 177]` | `ر` |
| `216` | `[216]` | first half of `ح` |
| `173` | `[173]` | second half of `ح` |
| `273` | `[216, 168]` | `ب` |
| `259` | `[216, 167]` | `ا` |

Four letters became single tokens. `ح` did not: the pair `(216, 173)` was not among the 41 learned merges, so that letter remains two separate byte tokens. A single character spread across two tokens is normal for a byte-level tokenizer.

With the special tokens, and back again:

```text
encode("مرحبا", add_bos=True, add_eos=True) -> [256, 260, 266, 216, 173, 273, 259, 257]
tokens_to_bytes(that) == "مرحبا".encode("utf-8")  -> True
decode(that)                                      -> 'مرحبا'      (equal to the input: True)
```

The round trip is exact: `decode(encode(text)) == text` for any string, because encoding only regroups the bytes and decoding ungroups them.

**When a sequence ends in the middle of a character.** Take the six tokens of `"مرحبا"` and append the single token `216`, a lead byte with nothing after it. This is what a generating model produces if it is stopped (or stops itself) between the two halves of a letter:

```text
ids:    [260, 266, 216, 173, 273, 259, 216]
bytes:  [217, 133, 216, 177, 216, 173, 216, 168, 216, 167, 216]      11 bytes: five complete letters + one stray lead byte

decode(ids)                    -> UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd8 in position 10: unexpected end of data
decode(ids, errors="replace")  -> 'مرحبا�'
decode(ids, errors="ignore")   -> 'مرحبا'
```

(`0xd8` is `216` in hexadecimal; position 10 is the eleventh byte.) The same happens with as little as `[217, 133, 216]`: strict decoding fails, `"replace"` gives `'م�'`.

Three observations to carry into chapter 10:

1. `tokens_to_bytes` succeeded on that sequence; only the final bytes → text step failed. Bytes are always available; text exists only when the bytes form complete characters.
2. Whether a sequence is decodable is a property of the *whole* byte string, not of individual tokens. `[216]` then `[173]` are each invalid alone and valid together.
3. Since tokens such as `261` end with a lead byte, a model can leave a character unfinished even when it emits only "learned" tokens. The inference code therefore checks candidate tokens at the byte level, using `token_to_bytes`, so that the final strict `decode` does not fail.

#### What I should understand before moving on

- Text (`str`) and bytes are different things; UTF-8 is the rule between them. ASCII characters are one byte, Arabic letters two (a lead byte, usually `216` or `217`, plus a continuation byte in `128`–`191`), and half a character is not decodable.
- The id space is fixed: `0`–`255` raw bytes, `256` BOS, `257` EOS, `258` PAD, `259` upward learned merges. Text can never encode to a special id.
- BPE training is counting: find the most frequent adjacent pair, give it the next id, replace it everywhere, repeat. It stops at the target vocabulary size or when the best pair occurs fewer than twice. `target_vocab_size=300` allows at most 41 merges.
- Documents are kept as separate sequences so that no merge is learned from an accidental boundary between two documents.
- The tokenizer *is* the ordered list of merges. Encoding replays them in that order; decoding expands each id to its bytes and decodes the bytes as UTF-8.
- BPE works on bytes and knows nothing about characters: some learned tokens end or begin mid-character.
- `tokenizer.json` stores descriptive fields plus `merges`; only `merges` is read back.
- The vocabulary is fitted to the corpus. Today that is one short Arabic document, so Arabic compresses (536 bytes → 257 tokens) and English does not compress at all.

#### Self-test

1. `"مرحبا"` has 5 characters. Why does `len("مرحبا".encode("utf-8"))` return 10, and what do you know about the 2nd, 4th, 6th, 8th and 10th byte values without looking them up?
2. A user's prompt contains the literal text `<EOS>`. Does the encoded prompt contain token id `257`? Why does the id layout guarantee your answer?
3. Train BPE by hand on the single document `"abababc"` with a large target vocabulary. Give the merges in order, the final sequence, and the reason training stops.
4. Two documents are `"xa"` and `"bx"`, repeated many times in the corpus in that alternating order. Can the pair (`a`, `b`) ever be merged? Which lines of code decide that?
5. You change `target_vocab_size` from `300` to `1000` and retrain on today's corpus. Will the vocabulary size be `1000`? What else in the project must agree with the number you actually get?
6. Why must `encode` apply merges in the order they were learned, rather than, say, longest token first?
7. `decode(ids)` raises `UnicodeDecodeError` for some generated `ids`, but `tokens_to_bytes(ids)` works. What does that tell you about the sequence, and why is no single token necessarily "the bad one"?
8. Someone edits `tokenizer.json` and changes `"eos": {"id": 257}` to `999`. What changes in the tokenizer's behaviour after `Tokenizer.load`?

<details><summary>Answers</summary>

1. Each Arabic letter has a code point above 127 and below 2048, so UTF-8 uses the two-byte form `110xxxxx 10xxxxxx` for it. The second byte of each letter is a continuation byte: it begins with bits `10`, so it lies between `128` and `191`.
2. No. `encode` turns the text into UTF-8 bytes, which are values `0`–`255`, then applies merges, which produce ids `259` and above. Id `257` is neither a byte value nor a merge id; it appears only when `add_eos=True` appends it. The five characters become `[60, 69, 79, 83, 62]`.
3. Bytes `[97, 98, 97, 98, 97, 98, 99]`. Counts: `(97, 98)`: 3, `(98, 97)`: 2, `(98, 99)`: 1. Merge 1: `(97, 98)` → `259`, giving `[259, 259, 259, 99]`. Counts: `(259, 259)`: 2, `(259, 99)`: 1. Merge 2: `(259, 259)` → `260`, giving `[260, 259, 99]` (left to right: the first two are merged, the third is left). Counts are now all 1, so `frequency < 2` stops training. Merges: `((97, 98), (259, 259))`.
4. No. `train_bpe` builds one list per document, and `count_pairs` zips each list only with itself, so the pair (`a`, `b`) is never counted, however the documents are ordered. It would be counted only if both bytes were adjacent inside one document.
5. No. The loop also stops when the most frequent pair occurs only once, and a 536-byte document runs out of repeated pairs long before 741 merges: run in memory on today's corpus, training stops at a vocabulary size of `330` (71 merges). The model's `vocab_size` (the default in `src/model/config.py`, and the value stored in a checkpoint) must equal the tokenizer's real `vocab_size`; the server compares the two and refuses to load a model when they differ. Existing tokenized files and checkpoints would also be invalid, since ids would mean different things.
6. Later merges are defined in terms of earlier ones: a pair like `(259, 216)` can match only once token `259` exists in the sequence. The training text was segmented by applying merges in that order, and the model learned from that segmentation. Any other order can yield a different sequence of ids for the same text, which the model never saw during training.
7. The bytes as a whole are not valid UTF-8: somewhere a character is incomplete or a continuation byte appears without its lead byte. Validity depends on how neighbouring tokens' bytes fit together; a token holding only a lead byte is fine when the next token supplies the continuation byte and wrong when it does not.
8. Nothing. `load` reads only `"merges"`. `eos_id` still returns the constant `EOS_ID = 257` from `bpe.py`. The file would simply be misleading.

</details>

---

## 7. The model

| | |
|---|---|
| **INPUT** | A tensor of token ids of shape `[B, T]`: `B` sequences, each `T` tokens long, every id an integer from `0` to `299`. |
| **PROCESS** | Turn each id into a vector of 128 numbers, add a vector for its position, pass the result through 4 identical transformer blocks (attention, then a feed-forward network), normalise once more, and project each vector to 300 scores. |
| **OUTPUT** | A tensor of logits of shape `[B, T, 300]`: for every position, one score per token in the vocabulary, saying how likely that token is to come next. |
| **WHY IT EXISTS** | Everything before this chapter prepared numbers; everything after it either adjusts this function (training) or calls it (evaluation, inference, serving). The model is the only part of the project that "knows" anything about language. |

The model lives in five source files under `src/model/`:

| File | Lines | Contains |
|---|---|---|
| `src/model/config.py` | 13 | `ModelConfig` — the six numbers that fix the model's size |
| `src/model/embeddings.py` | 48 | `TokenAndPositionEmbedding` |
| `src/model/attention.py` | 124 | `CausalSelfAttention` |
| `src/model/transformer.py` | 69 | `FeedForward`, `TransformerBlock` |
| `src/model/model.py` | 52 | `TinyLLM` — the whole model |

There is nothing else in the folder except `__pycache__/`, which holds Python's compiled copies of these five files and can be ignored. There is no `__init__.py`; Python still treats `src/model` as a package (a "namespace package"), which is why `from src.model.config import ModelConfig` works when you run from the project directory.

### 7.1 What the model is

#### A function from ids to scores

Forget the word "intelligence" for a moment. `TinyLLM` is a function. You hand it a grid of integers; it hands back a grid of decimal numbers.

```
input_ids  [B, T]        ──►  TinyLLM  ──►   logits  [B, T, vocab_size]
integers 0..299                               decimal numbers, any sign
```

- `B` is the **batch size**: how many separate sequences you process at once. They do not interact; batching exists only because doing many at once is faster.
- `T` is the **sequence length**: how many tokens each sequence has. It can be anything from `1` up to `context_length` (`128`).
- `vocab_size` is `300`, the number of different token ids the tokenizer of chapter 6 can produce.

For every one of the `B × T` positions, the model produces a row of 300 numbers called **logits**. The logit at index `k` of the row for position `t` is the model's score for "the token that follows position `t` is token `k`". A larger logit means "more likely". Logits are not probabilities: they can be negative and they do not add up to 1. Turning them into probabilities is a separate step (softmax, explained in 7.4) that training and inference apply themselves.

Important: the row at position `t` predicts the token at position `t + 1`, using only positions `0..t`. So one call on a sequence of `T` tokens produces `T` predictions at once — "after token 0, what comes next?", "after tokens 0–1, what comes next?", and so on. Training compares all `T` rows of logits with the true next tokens (chapter 8). Inference only uses the last row (chapter 10).

This is real output from the model with its current default configuration, on random ids:

```
input_ids.shape   torch.Size([2, 5])        dtype torch.int64
logits.shape      torch.Size([2, 5, 300])   dtype torch.float32
```

Two sequences of five tokens in, two sequences of five rows of 300 scores out.

#### Tensors and shapes

A **tensor** is PyTorch's array of numbers: every element has the same type, and the elements are arranged in a regular grid. The **shape** lists the grid's size along each dimension.

| Shape | What it looks like | Example in this model |
|---|---|---|
| `[5]` | a list of 5 numbers | the positions `0, 1, 2, 3, 4` |
| `[2, 5]` | a table, 2 rows × 5 columns | `input_ids`: 2 sequences of 5 tokens |
| `[2, 5, 128]` | 2 tables, each 5 rows × 128 columns | one 128-number vector per token |
| `[2, 4, 5, 5]` | 2 × 4 tables, each 5 × 5 | attention scores: per sequence, per head |

Three rules cover almost everything in this chapter:

1. **The last dimension is usually "the vector".** In `[B, T, 128]`, read it as "for each of `B` sequences, for each of `T` positions, a vector of 128 numbers".
2. **Most operations act on the last one or two dimensions and leave the leading ones alone.** A `Linear` layer transforms the last dimension. Matrix multiplication `@` multiplies the last two dimensions. Everything in front is treated as "do the same thing for each".
3. **Reshaping does not change the numbers, only how they are grouped.** `view` regroups; `transpose` swaps two dimensions. Real output:

```
t = torch.tensor([[1,2,3],[4,5,6]])     shape [2, 3]

t.view(3, 2)          tensor([[1, 2],
                              [3, 4],
                              [5, 6]])     same order, regrouped

t.transpose(0, 1)     tensor([[1, 4],
                              [2, 5],
                              [3, 6]])     rows became columns
```

Note the difference: `view` reads the numbers in the same order and cuts them into new rows; `transpose` actually changes which number is neighbour to which. Attention (7.4) uses both, and the difference matters there.

Token ids are integers (`torch.int64`); everything after the embedding is decimal numbers (`torch.float32`).

#### `nn.Module`: how PyTorch builds a model

Every class in `src/model/` except `ModelConfig` is written as `class Something(nn.Module)`. `nn.Module` is PyTorch's base class for "a piece of a neural network". Inheriting from it gives you a fixed pattern with two methods:

- **`__init__`** runs once, when the object is created. It **creates the layers** and stores them on `self`. No data flows here. Think of it as building the machine.
- **`forward`** runs every time data is passed through. It **uses the layers** on an input tensor and returns an output tensor. Think of it as running the machine.

The first line of every `__init__` is `super().__init__()`. That calls `nn.Module`'s own `__init__`, which sets up the internal bookkeeping that the next point depends on. Without it, assigning a layer to `self` raises an error.

**Parameters.** A layer such as `nn.Linear` or `nn.Embedding` owns one or more tensors of numbers that are *not* supplied by you: they start random and are adjusted by training. These are the model's **parameters** (also called weights). "Training a model" means nothing more than changing these numbers; "a checkpoint" is a file containing them. This model has 884,480 of them (7.7).

When you write `self.something = <a layer>` inside a module, `nn.Module` notices and registers that layer as a child. That is how one call, `model.parameters()`, can find every parameter in every nested layer, and how `model.to(device)`, `model.state_dict()` and `model.eval()` reach all of them.

**Why `model(x)` calls `forward`.** You never write `model.forward(x)`. You write `model(x)`. In Python, calling an object like a function runs its `__call__` method; `nn.Module` defines `__call__` to do some housekeeping and then call your `forward`. So `block(x)`, `self.q_proj(x)` and `self.embeddings(input_ids)` are all "run that module's `forward` on this tensor".

**The two layer types that hold almost all the parameters:**

| Layer | Parameters it stores | What `layer(x)` returns |
|---|---|---|
| `nn.Embedding(N, D)` | a table `weight` of shape `[N, D]` | for each integer in `x`, the matching row of the table (7.3) |
| `nn.Linear(I, O)` | a matrix `weight` of shape `[O, I]` and, unless `bias=False`, a vector `bias` of shape `[O]` | `x @ weight.T + bias`: each output number is a weighted sum of the `I` input numbers. Changes the last dimension from `I` to `O` |

Real output confirming that `Linear` only touches the last dimension:

```
lin = torch.nn.Linear(3, 2, bias=False)
lin.weight.shape                 torch.Size([2, 3])
lin(torch.ones(4, 5, 3)).shape   torch.Size([4, 5, 2])
```

#### The model as it is actually built

This is the structure PyTorch prints for `TinyLLM(ModelConfig())` (real output):

```
TinyLLM(
  (embeddings): TokenAndPositionEmbedding(
    (token_embedding): Embedding(300, 128)
    (position_embedding): Embedding(128, 128)
  )
  (blocks): ModuleList(
    (0-3): 4 x TransformerBlock(
      (norm1): LayerNorm((128,), eps=1e-05, elementwise_affine=True, bias=True)
      (attention): CausalSelfAttention(
        (q_proj): Linear(in_features=128, out_features=128, bias=False)
        (k_proj): Linear(in_features=128, out_features=128, bias=False)
        (v_proj): Linear(in_features=128, out_features=128, bias=False)
        (out_proj): Linear(in_features=128, out_features=128, bias=False)
        (dropout): Dropout(p=0.0, inplace=False)
      )
      (norm2): LayerNorm((128,), eps=1e-05, elementwise_affine=True, bias=True)
      (feed_forward): FeedForward(
        (net): Sequential(
          (0): Linear(in_features=128, out_features=512, bias=True)
          (1): GELU(approximate='none')
          (2): Linear(in_features=512, out_features=128, bias=True)
          (3): Dropout(p=0.0, inplace=False)
        )
      )
    )
  )
  (final_norm): LayerNorm((128,), eps=1e-05, elementwise_affine=True, bias=True)
  (lm_head): Linear(in_features=128, out_features=300, bias=False)
)
```

And the same thing as a data-flow diagram, with the shape of the data on every arrow:

```
input_ids                                             [B, T]        integers
    │
    ├── token_embedding   (table 300 × 128)   ──►     [B, T, 128]
    ├── position_embedding(table 128 × 128)   ──►        [T, 128]
    │                 add the two
    ▼
    x                                                 [B, T, 128]
    │
    │   ┌──────────────── TransformerBlock (×4, one after another) ───────────────┐
    │   │                                                                          │
    │   │   x ──┬──► norm1 ──► attention ──┐                                       │
    │   │       │                          ▼                                       │
    │   │       └────────────────────────► + ──► x                 [B, T, 128]     │
    │   │                                                                          │
    │   │   x ──┬──► norm2 ──► feed_forward (128 → 512 → 128) ──┐                  │
    │   │       │                                               ▼                  │
    │   │       └─────────────────────────────────────────────► + ──► x            │
    │   │                                                          [B, T, 128]     │
    │   └──────────────────────────────────────────────────────────────────────────┘
    ▼
 final_norm                                           [B, T, 128]
    ▼
 lm_head  (Linear 128 → 300, no bias)
    ▼
 logits                                               [B, T, 300]
```

Read it top to bottom. Between the embedding and the output head the shape never changes: it is always `[B, T, 128]`. The blocks do not make the data bigger or smaller; they repeatedly *rewrite* each position's 128-number vector, so that by the end it no longer describes "this token" but "what should come after this token, given everything before it".

The sections below follow the same order as the data: config, embeddings, attention, block, whole model.

### 7.2 The configuration

#### `src/model/config.py`

**Why this file exists.** Every other file in `src/model/` needs to know the same handful of sizes. Putting them in one object, passed to every constructor, guarantees the pieces fit together.

**What enters / what leaves.** Nothing enters. It defines one class, `ModelConfig`. Creating one with no arguments, `ModelConfig()`, gives the defaults below.

**How it connects.** `scripts/train.py` creates `ModelConfig()` with the defaults and passes it to `TinyLLM`. The training code saves the six values into every checkpoint under the key `"config"`. Evaluation, inference and serving do the opposite: they read that dictionary from the checkpoint and rebuild the object with `ModelConfig(**checkpoint["config"])`, so a loaded model always has the sizes it was trained with, even if the defaults in this file change later.

**The code, section by section.**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
```

`dataclass` comes from Python's standard library (see the primer in 1). The decorator reads the annotated fields below and writes `__init__`, `__repr__` and `__eq__` for you, so `ModelConfig(d_model=64)` works without you writing a constructor.

`frozen=True` adds one more thing: after the object is created, its fields cannot be reassigned. Real output:

```
>>> cfg = ModelConfig()
>>> cfg.d_model = 5
FrozenInstanceError: cannot assign to field 'd_model'
```

This matters for a model config. The layers are built *from* these numbers at construction time. If you could change `cfg.d_model` afterwards, the config would say one thing while the layers already built had another size, and the config saved into a checkpoint would be a lie. Freezing makes that mistake impossible.

```python
    vocab_size: int = 300
    context_length: int = 128

    d_model: int = 128
    num_heads: int = 4
    num_layers: int = 4

    dropout: float = 0.0
```

Each line is `name: type = default`.

| Field | Default | What it controls | Where it is used |
|---|---|---|---|
| `vocab_size` | `300` | How many different token ids exist. Must equal the tokenizer's vocabulary size (the current tokenizer has exactly 300: 256 bytes + 3 special tokens + 41 merges, chapter 6). | Number of rows in the token embedding table; number of output scores per position in `lm_head`. |
| `context_length` | `128` | The longest sequence the model can accept, in tokens. | Number of rows in the position embedding table. Also read by the data loader, evaluator and generator to cut sequences to this length. |
| `d_model` | `128` | The width of the model: how many numbers represent each token at every stage between the embedding and the output head. | Almost every layer's size. |
| `num_heads` | `4` | How many independent attention patterns each attention layer computes in parallel. Must divide `d_model` evenly. | `CausalSelfAttention`. Each head works with `128 / 4 = 32` numbers. |
| `num_layers` | `4` | How many transformer blocks are stacked. | `TinyLLM.__init__`. |
| `dropout` | `0.0` | The fraction of values randomly set to zero during training as a guard against memorising. `0.0` means "never drop anything": the dropout layers exist in the code but pass data through unchanged. | Two `nn.Dropout` layers per block. |

Two things to notice:

- `vocab_size` is a fixed default here, not read from the tokenizer. `scripts/train.py` uses `ModelConfig()` as is, so the two agree only because both currently say `300`. The serving code does check the match when it loads a checkpoint.
- `d_model` and `context_length` are both `128`. That is a coincidence of the chosen defaults. They are unrelated quantities: one is "numbers per token", the other is "tokens per sequence". Watch for this in the position embedding, whose table is `[128, 128]` — `[context_length, d_model]`, not a square by design.

### 7.3 Embeddings

| | |
|---|---|
| **INPUT** | `input_ids`, shape `[B, T]`, integers. |
| **PROCESS** | Look up one row of a table for each token id; look up one row of a second table for each position `0..T-1`; add them. |
| **OUTPUT** | A tensor of shape `[B, T, 128]`, decimal numbers. |
| **WHY IT EXISTS** | A token id is a label, not a quantity. Id `200` is not "twice" id `100`. Arithmetic on ids is meaningless, so the first step must replace each id with a vector of numbers that training can shape. And because attention has no built-in sense of order, the position has to be written into that vector too. |

#### `src/model/embeddings.py`

**Why this file exists.** It is the model's entry door: it converts integers into the vectors that every later layer works on.

**What enters / what leaves.** The constructor takes a `ModelConfig`. `forward` takes `input_ids` of shape `[B, T]` and returns a tensor of shape `[B, T, d_model]`. It raises `ValueError` if `T` is greater than `context_length`.

**How it connects.** Created and called only by `TinyLLM` (7.6). Its output is the first `x` that enters the stack of transformer blocks.

**The code, section by section.**

```python
import torch
from torch import nn

from src.model.config import ModelConfig
```

`torch` is PyTorch itself: tensors and the functions on them (`torch.arange`, `torch.Tensor`). `nn` is its neural-network sub-package: `nn.Module` and ready-made layers (`nn.Embedding`). `ModelConfig` is imported for the sizes and for the type hint.

```python
class TokenAndPositionEmbedding(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()

        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.d_model,
        )
```

The class is an `nn.Module`, so it follows the build/run pattern from 7.1. `super().__init__()` sets up the module bookkeeping.

**What Python/PyTorch does.** `nn.Embedding(300, 128)` creates one parameter, a table called `weight` of shape `[300, 128]`, filled with random numbers (drawn from a normal distribution with mean 0 and standard deviation 1; the measured standard deviation of a fresh table here was `0.996`). Calling the layer with a tensor of integers returns, for each integer `i`, a copy of row `i`. It is indexing, not arithmetic. Verified: `token_embedding(input_ids)[0, 0]` is exactly equal to `token_embedding.weight[input_ids[0, 0]]`.

**What it means in the LLM.** Each of the 300 tokens gets its own vector of 128 numbers. At the start these vectors are noise. Training moves them so that tokens used in similar ways end up with similar vectors. This table *is* the model's knowledge of what each token is; it holds `300 × 128 = 38,400` parameters.

```python
        self.position_embedding = nn.Embedding(
            config.context_length,
            config.d_model,
        )
```

**What Python/PyTorch does.** A second, separate table of shape `[128, 128]`: `context_length` rows, `d_model` columns. Same kind of layer, but it will be indexed by position numbers instead of token ids.

**What it means in the LLM.** Row `0` is a learned vector meaning "I am the first token of the sequence", row `1` means "I am the second", up to row `127`. These are **learned** position embeddings: nothing in the code tells the model what the vectors should be, only that position `p` always gets row `p`. `128 × 128 = 16,384` parameters. Because the table has exactly 128 rows, position `128` does not exist — that is what physically limits the model to 128 tokens.

```python
    def forward(
        self,
        input_ids: torch.Tensor,
    ) -> torch.Tensor:

        batch_size, sequence_length = input_ids.shape
```

`forward` takes one tensor and returns one tensor (the `-> torch.Tensor` type hint). `input_ids.shape` is `[B, T]`; Python unpacks its two entries into two names. This unpacking is also an implicit check: if `input_ids` had one or three dimensions, the line would fail with "not enough/too many values to unpack". `batch_size` is not used again in this function; `sequence_length` is.

```python
        if sequence_length > self.position_embedding.num_embeddings:
            raise ValueError(
                f"Sequence length {sequence_length} exceeds "
                f"context length "
                f"{self.position_embedding.num_embeddings}"
            )
```

`num_embeddings` is an attribute every `nn.Embedding` has: its number of rows, here `128`. The class did not keep the config, so it asks the table itself how long it is. If `T` is larger, the function stops with a clear message. The three f-strings on consecutive lines are joined by Python into one string. Real output when passing 129 tokens:

```
ValueError: Sequence length 129 exceeds context length 128
```

Without this check PyTorch would fail a few lines later with a less helpful "index out of range" error when looking up row `128`. A sequence of exactly 128 tokens is accepted.

```python
        positions = torch.arange(
            sequence_length,
            device=input_ids.device,
        )
```

**What Python/PyTorch does.** `torch.arange(T)` creates the tensor `[0, 1, 2, …, T-1]`, shape `[T]`, integer type. Real output for `T = 5`: `tensor([0, 1, 2, 3, 4])`, shape `torch.Size([5])`. `device=input_ids.device` creates it on the same device (CPU, or Apple's GPU "mps", or "cuda") as the input. PyTorch refuses to combine tensors that live on different devices, so every tensor created inside `forward` must copy the device of its input.

**What it means in the LLM.** These are the position numbers. They depend only on the length of the sequence, not on its contents: every sequence of 5 tokens has positions `0..4`. That is why this tensor has no batch dimension.

```python
        token_vectors = self.token_embedding(
            input_ids
        )

        position_vectors = self.position_embedding(
            positions
        )
```

Two table lookups. Shapes from a real run with `B = 2`, `T = 5`:

| Line | Input shape | Output shape |
|---|---|---|
| `self.token_embedding(input_ids)` | `[2, 5]` | `[2, 5, 128]` |
| `self.position_embedding(positions)` | `[5]` | `[5, 128]` |

An embedding lookup always appends one dimension of size `d_model` to the shape of the integers it was given.

```python
        return token_vectors + position_vectors
```

**What Python/PyTorch does.** Element-wise addition of a `[2, 5, 128]` tensor and a `[5, 128]` tensor. The shapes differ, so PyTorch applies **broadcasting**: it lines the shapes up from the right (`5, 128` matches `5, 128`), and the missing leading dimension is treated as "repeat for each". The same `[5, 128]` block of position vectors is added to each of the 2 sequences. Result: `[2, 5, 128]` (verified).

**What it means in the LLM.** The vector for one position is now "what token I am" plus "where I am", as a single list of 128 numbers. The two pieces of information are mixed by plain addition into the same 128 slots; there are no separate "token slots" and "position slots". The later layers learn to read both out of the sum.

**Why token embeddings alone are not enough.** Suppose the position table did not exist. Attention (7.4) builds each position's new vector as a weighted average of the vectors it is allowed to see, and the weights depend only on the *contents* of the vectors being compared. Nothing in that calculation uses the index of a position. Take the sequences `"dog bites man today"` and `"man bites dog today"`. In an attention layer, the last position (`today`) would compare itself with the same four vectors in both cases, just listed in a different order, and a weighted average does not care about the order of its terms: it would get exactly the same result for both sentences. (The causal mask leaks a little order information, because position 0 sees one token and position 3 sees four, but that is an accident, not a mechanism the model can rely on.) Adding a different position vector to each slot makes "`dog` at position 0" a different vector from "`dog` at position 2", and that difference is what lets the model learn that order matters.

### 7.4 Attention

| | |
|---|---|
| **INPUT** | `x`, shape `[B, T, 128]`: one vector per position. |
| **PROCESS** | For every position, compute a score against every position, forbid the scores that point at later positions, turn the remaining scores into weights that sum to 1, and replace the position's vector by the weighted average of the others' "value" vectors. Do this 4 times in parallel (4 heads) on 4 slices of 32 numbers. |
| **OUTPUT** | A tensor of the same shape, `[B, T, 128]`. |
| **WHY IT EXISTS** | It is the only place in the whole model where information moves *between positions*. Every other layer treats each position on its own. Without attention, the prediction after `"i love"` could depend only on the token `love`, never on `i`. |

#### The idea before the code

After the embedding, position `t` holds a vector that describes only token `t`. To predict what comes next, the model needs each position to gather information from the positions before it. Attention does that with three roles, all computed from the same input vector:

| Role | Question it answers | Used for |
|---|---|---|
| **Query** `q` | "What am I looking for?" | Compared against every key. |
| **Key** `k` | "What do I contain, as an address?" | Compared against every query. |
| **Value** `v` | "What do I hand over if someone attends to me?" | Averaged, using the weights that the query–key comparison produced. |

The comparison is a **dot product**: multiply two vectors number by number and add the results. `[1, 2] · [3, 4] = 1×3 + 2×4 = 11`. It is large and positive when two vectors point the same way, near zero when they are unrelated, negative when they point opposite ways. So "the query of position `i` dotted with the key of position `j`" is a single number saying how relevant `j` is to `i`.

The whole layer is five steps: make q, k, v → score every pair → mask the future → softmax → average the values.

#### `src/model/attention.py`

**Why this file exists.** It implements causal multi-head self-attention from the basic operations, with nothing hidden inside a library call, so every step can be read.

**What enters / what leaves.** The constructor takes a `ModelConfig` and raises `ValueError` if `d_model` is not divisible by `num_heads`. `forward` takes `x` of shape `[B, T, d_model]` and returns a tensor of the same shape.

**How it connects.** Created and called only by `TransformerBlock` (7.5), which feeds it a normalised copy of `x` and adds its output back onto `x`.

**The code, section by section.**

```python
import math

import torch
from torch import nn

from src.model.config import ModelConfig
```

`math` is Python's standard maths module; this file uses exactly one thing from it, `math.sqrt`. `torch` supplies `torch.triu`, `torch.ones`, `torch.softmax` and the tensor type; `nn` supplies `nn.Module`, `nn.Linear`, `nn.Dropout`.

```python
class CausalSelfAttention(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()

        if config.d_model % config.num_heads != 0:
            raise ValueError(
                "d_model must be divisible by num_heads"
            )
```

The name says what it is: **self**-attention because queries, keys and values all come from the same sequence; **causal** because a position may only use positions at or before itself.

`%` is the remainder operator. `128 % 4` is `0`, so the default config passes. The 128 numbers are about to be cut into `num_heads` equal slices, which is only possible if the division is exact. Real output with `d_model=130`: `ValueError: d_model must be divisible by num_heads`.

```python
        self.num_heads = config.num_heads
        self.head_dim = (
            config.d_model // config.num_heads
        )
```

`//` is integer division: `128 // 4 = 32`. The module remembers two plain integers, `num_heads = 4` and `head_dim = 32`, for use in `forward`. Plain integers stored on `self` are not parameters; they are just settings.

```python
        self.q_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

        self.k_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

        self.v_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )
```

**What Python/PyTorch does.** Three independent `Linear` layers, each mapping 128 numbers to 128 numbers. `bias=False` means each layer has only its weight matrix, shape `[128, 128]`, and computes `x @ weight.T` with nothing added. Each holds `128 × 128 = 16,384` parameters. "proj" is short for projection, the usual name for a linear layer whose job is to re-express a vector.

**What it means in the LLM.** These three matrices are how one input vector becomes three different things. `q_proj` learns to extract "what this position is looking for", `k_proj` learns "what this position offers as a match", `v_proj` learns "what this position passes on". They start random and all three are shaped entirely by training. Note there is one `[128, 128]` matrix per role for all four heads together, not four small matrices; the split into heads happens afterwards by slicing the 128 outputs.

```python
        self.out_proj = nn.Linear(
            config.d_model,
            config.d_model,
            bias=False,
        )

        self.dropout = nn.Dropout(
            config.dropout
        )
```

`out_proj` is a fourth `[128, 128]` matrix, applied at the very end to mix the four heads' results together. So the attention layer has `4 × 16,384 = 65,536` parameters in total.

`nn.Dropout(p)` has no parameters. During training it sets each number it is given to zero with probability `p` and multiplies the survivors by `1 / (1 - p)`; in evaluation mode (`model.eval()`) it does nothing. Here `p = config.dropout = 0.0`, so it does nothing in either mode. It is in the code so that changing one number in the config would turn it on.

```python
    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:

        batch_size, sequence_length, d_model = x.shape
```

Unpacks the three dimensions of the input. In the shape tables below, the real run used `B = 2`, `T = 5`, `d_model = 128`, `num_heads = 4`, `head_dim = 32`.

**Step 1 — queries, keys and values.**

```python
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)
```

**What Python/PyTorch does.** Three calls of a `Linear` layer on the same `x`. `Linear` acts on the last dimension only, so each result is `[2, 5, 128]`, the same shape as `x` (verified).

**What it means in the LLM.** Every position now has a query vector, a key vector and a value vector, each of 128 numbers.

**Step 2 — split into heads.**

```python
        q = q.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)
```

This is two operations chained on one expression. Take them one at a time.

**What Python/PyTorch does.**

| Operation | Shape before | Shape after | What changed |
|---|---|---|---|
| `.view(B, T, 4, 32)` | `[2, 5, 128]` | `[2, 5, 4, 32]` | The last dimension of 128 is cut into 4 consecutive groups of 32: numbers `0–31`, `32–63`, `64–95`, `96–127`. No number moves. |
| `.transpose(1, 2)` | `[2, 5, 4, 32]` | `[2, 4, 5, 32]` | Dimensions 1 and 2 swap places (dimensions are counted from 0). |

After `view` the tensor reads "per sequence, per position, per head, 32 numbers". After `transpose` it reads "per sequence, **per head**, per position, 32 numbers".

Why the swap is needed: the next line uses `@`, which multiplies the **last two** dimensions and treats everything before them as "repeat for each". We want the last two dimensions to be `[positions, numbers]` so that positions get compared with positions. With the head dimension moved up next to the batch dimension, the four heads become four independent copies of the calculation, exactly like the batch.

**What it means in the LLM.** Instead of one attention pattern computed from all 128 numbers, the model computes **four separate patterns**, each from its own 32-number slice of q, k and v. One head may learn to look at the previous token, another at the start of the word, another at the most recent space. A single head has to settle on one set of weights per position; four heads let a position attend to several different things for different reasons at once. The cost is that each head works with shorter vectors (32 instead of 128).

```python
        k = k.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        v = v.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)
```

The same two operations for `k` and `v`. After these lines `q`, `k` and `v` are all `[2, 4, 5, 32]`: `[B, heads, T, head_dim]`.

**Step 3 — the score matrix.**

```python
        scores = (
            q @ k.transpose(-2, -1)
        ) / math.sqrt(self.head_dim)
```

One expression, three operations.

**What Python/PyTorch does.**

| Sub-expression | Shape | Meaning |
|---|---|---|
| `q` | `[2, 4, 5, 32]` | 5 query rows of 32 numbers, per head |
| `k.transpose(-2, -1)` | `[2, 4, 32, 5]` | negative indices count from the end, so this swaps the last two dimensions: the 5 key vectors now stand as columns |
| `q @ k.transpose(-2, -1)` | `[2, 4, 5, 5]` | matrix multiplication of a `5 × 32` by a `32 × 5`, done separately for each of the 2 × 4 leading combinations |
| `… / math.sqrt(self.head_dim)` | `[2, 4, 5, 5]` | every number divided by `√32 = 5.657` |

Matrix multiplication of `[5, 32]` by `[32, 5]` gives `[5, 5]`, and by definition its entry at row `i`, column `j` is the dot product of row `i` of the left matrix with column `j` of the right matrix. Here that is: **query of position `i`** · **key of position `j`**.

**What it means in the LLM.** `scores[b, h, i, j]` is one number: in sequence `b`, according to head `h`, how much position `i` wants to take information from position `j`. Row `i` of the `5 × 5` table is "position `i` looking out at every position"; column `j` is "every position looking at position `j`". All 25 pairs are scored in one multiplication.

**Why divide by the square root of the head dimension.** A dot product of two 32-number vectors is a sum of 32 products, and the more terms you add the more the total swings. Measured here on 10,000 pairs of random vectors with 32 numbers each (each number with standard deviation 1): the dot products had a standard deviation of `5.68`, almost exactly `√32 = 5.657`; after dividing by `√32` it was `1.004`. So the division brings the scores back to roughly "size 1" whatever `head_dim` is.

It matters because of the softmax two steps below. Softmax exaggerates differences: if scores are spread over a wide range, nearly all the weight goes to the single largest one. Real output for one random query against five random keys, `head_dim = 32`:

```
unscaled scores   [-2.0532, -5.3825,  1.5385,  2.3713, -2.3540]
softmax           [ 0.0082,  0.0003,  0.2986,  0.6868,  0.0061]

scaled scores     [-0.3630, -0.9515,  0.2720,  0.4192, -0.4161]
softmax           [ 0.1521,  0.0844,  0.2869,  0.3324,  0.1442]
```

Unscaled, two positions take 98.5% of the attention before the model has learned anything. Scaled, the weights are spread out. An attention layer that starts already locked onto one or two positions learns poorly, because the positions it ignores receive almost no learning signal. The scaling keeps the starting point soft and lets training decide where to sharpen.

**Step 4 — the causal mask.**

```python
        causal_mask = torch.triu(
            torch.ones(
                sequence_length,
                sequence_length,
                device=x.device,
                dtype=torch.bool,
            ),
            diagonal=1,
        )
```

**What Python/PyTorch does.** Inside-out:

- `torch.ones(T, T, device=x.device, dtype=torch.bool)` makes a `T × T` table where every entry is `True` (`dtype=torch.bool` means true/false values instead of numbers; "one" as a boolean is `True`). It is created on the same device as `x`, for the reason given in 7.3.
- `torch.triu(…, diagonal=1)` keeps the **upper triangle** ("tri-u") and sets everything else to `False`. `diagonal=1` means "start one step above the main diagonal", so the diagonal itself is not kept.

Real output for `T = 5`, shape `[5, 5]`:

```
tensor([[False,  True,  True,  True,  True],
        [False, False,  True,  True,  True],
        [False, False, False,  True,  True],
        [False, False, False, False,  True],
        [False, False, False, False, False]])
```

**What it means in the LLM.** Read row `i` as "what must position `i` not look at?". `True` at row `i`, column `j` means `j > i`: position `j` comes *after* position `i`. Row 0 may only see column 0 (itself). Row 2 may see columns 0, 1, 2. The last row may see everything. The diagonal is `False`: a position is always allowed to attend to itself.

The mask is built fresh on every call, sized to the current `T`. It is not a parameter and it is not stored on the module.

```python
        scores = scores.masked_fill(
            causal_mask,
            float("-inf"),
        )
```

**What Python/PyTorch does.** `masked_fill(mask, value)` returns a copy of `scores` in which every entry where `mask` is `True` is replaced by `value`; the others are untouched. `float("-inf")` is negative infinity, a real floating-point value smaller than every other number. The mask is `[5, 5]` and `scores` is `[2, 4, 5, 5]`; broadcasting (7.3) applies the same `5 × 5` mask to every head of every sequence. Shape stays `[2, 4, 5, 5]`.

**What it means in the LLM.** Every "position `i` looks at a later position `j`" score is overwritten with "impossible". The model did compute those scores in step 3; they are simply thrown away here.

**Why a language model must not look ahead.** Recall from 7.1 that the row of logits at position `t` is the model's guess for token `t + 1`, and that training checks all `T` guesses in one call. Token `t + 1` is sitting right there in the input, at position `t + 1`. If position `t` were allowed to attend to it, the model would learn the easiest possible rule — "copy the next token" — get a near-perfect score in training, and learn nothing about language. Then at generation time, when the next token really does not exist yet, it would have nothing to copy. The mask makes training honest: at every position the model sees exactly what it will see when generating, namely the past and nothing else.

This was checked on the real model: two inputs of 6 tokens, identical except for the last token, give identical logits at positions `0–4` and different logits at position `5`. Changing a later token cannot affect an earlier position's output.

**Step 5 — softmax into attention weights.**

```python
        attention_weights = torch.softmax(
            scores,
            dim=-1,
        )
```

**Softmax** turns a list of arbitrary numbers into a list of positive numbers that add up to 1. For each number `z`: compute `e^z` (the exponential, always positive; `e ≈ 2.718`), then divide by the sum of all the `e^z` in the list. Bigger inputs get bigger shares; the gaps are amplified because the exponential grows fast.

Real output:

```
softmax([2.0, 1.0, 0.0])     =  [0.6652, 0.2447, 0.0900]
softmax([2.0, 1.0, -inf])    =  [0.7311, 0.2689, 0.0000]
```

The second line shows what `-inf` does. `e^(-inf)` is exactly `0`. So a masked entry contributes nothing to the sum and receives a share of exactly zero, and the remaining entries share the whole 1 between them. This is why the mask is applied by writing `-inf` into the *scores* before softmax, instead of writing `0` into the weights afterwards: the weights of the allowed positions still add up to 1 on their own.

**What Python/PyTorch does.** `dim=-1` says "apply softmax along the last dimension", that is, separately to each row of each `5 × 5` table. Shape stays `[2, 4, 5, 5]`. Verified: every row sums to `1`.

**What it means in the LLM.** Row `i` is now a recipe: "to build position `i`'s new vector in this head, take this fraction of position 0, this fraction of position 1, …, and zero of anything after `i`". Row 0 is always `[1, 0, 0, 0, 0]`: the first token has only itself to attend to.

```python
        attention_weights = self.dropout(
            attention_weights
        )
```

Passes the weights through the dropout layer created in `__init__`. With `dropout = 0.0`, as configured, the tensor comes out unchanged. If dropout were turned on, then during training random individual weights would be zeroed (the model is forced not to rely on any single connection) and the rest scaled up, so rows would no longer sum to exactly 1 during training; at evaluation and inference it would still do nothing.

**Step 6 — average the values.**

```python
        output = attention_weights @ v
```

**What Python/PyTorch does.** Matrix multiplication of `[2, 4, 5, 5]` by `[2, 4, 5, 32]`. The last two dimensions are `5 × 5` times `5 × 32`, giving `5 × 32`. Result: `[2, 4, 5, 32]` (verified). Row `i` of the result is `weight[i,0] × v[0] + weight[i,1] × v[1] + … + weight[i,4] × v[4]`.

**What it means in the LLM.** This is the moment information moves. Each position's new 32-number vector in this head is a weighted average of the *value* vectors of the positions it is allowed to see, using the weights from step 5. If position 3 puts weight `0.9` on position 1, then position 3's output is almost a copy of what position 1 chose to hand over. Queries and keys decided *where* to look; values are *what* is fetched.

**Step 7 — merge the heads.**

```python
        output = output.transpose(
            1,
            2,
        ).contiguous()

        output = output.view(
            batch_size,
            sequence_length,
            d_model,
        )
```

Step 2 in reverse.

**What Python/PyTorch does.**

| Operation | Shape before | Shape after |
|---|---|---|
| `.transpose(1, 2)` | `[2, 4, 5, 32]` | `[2, 5, 4, 32]` |
| `.contiguous()` | `[2, 5, 4, 32]` | `[2, 5, 4, 32]` |
| `.view(B, T, d_model)` | `[2, 5, 4, 32]` | `[2, 5, 128]` |

`transpose` puts positions back in front of heads: "per sequence, per position, per head, 32 numbers". `view` then glues each position's four 32-number pieces end to end into one 128-number vector.

`.contiguous()` needs a word. `transpose` does not move any numbers in memory; it only changes the bookkeeping PyTorch uses to find them. `view` requires the numbers to be physically laid out in the order of the shape you ask for, and after a `transpose` they are not. `.contiguous()` makes a real copy in the new order. Without it this exact `view` fails; real output:

```
RuntimeError: view size is not compatible with input tensor's size and stride ...
```

In step 2 the order was `view` then `transpose`, so no `.contiguous()` was needed there.

**What it means in the LLM.** The four heads' separate findings are laid side by side again: numbers `0–31` of each position's vector come from head 0, `32–63` from head 1, and so on.

**Step 8 — the output projection.**

```python
        return self.out_proj(output)
```

**What Python/PyTorch does.** One more `Linear` layer, 128 → 128, no bias. Shape stays `[2, 5, 128]` (verified on the whole module: input `[2, 5, 128]`, output `[2, 5, 128]`).

**What it means in the LLM.** After the merge, the four heads still sit in four separate slices. `out_proj` is a learned mix: every one of the 128 output numbers is a weighted sum of all 128 merged numbers, so the heads' results are blended into one vector in the form the rest of the model expects. That vector is what the transformer block adds back onto `x`.

There is no dropout after `out_proj` in this file; the only dropout in attention is the one on the weights.

#### The whole thing by hand: `T = 3`, one head

To see real numbers, shrink everything: `d_model = 2`, `num_heads = 1` (so `head_dim = 2`), one sequence of three positions. To keep the arithmetic followable, the four projection matrices of a real `CausalSelfAttention` were overwritten with the identity matrix, which makes `q = k = v = x` and makes `out_proj` a no-op. Everything else is the real module's code path. (A trained model's matrices are not the identity; this is only to make the mask and the softmax visible.)

The input, one vector of 2 numbers per position:

```
position 0:  [1, 0]
position 1:  [1, 1]
position 2:  [0, 2]
```

**Raw scores `q @ k.transpose(-2, -1)`.** Entry `[i, j]` = (vector `i`) · (vector `j`). For example row 1, column 2: `[1, 1] · [0, 2] = 1×0 + 1×2 = 2`. Real output:

```
tensor([[1., 1., 0.],
        [1., 2., 2.],
        [0., 2., 4.]])
```

**Divide by `√head_dim = √2 = 1.4142`:**

```
tensor([[0.7071, 0.7071, 0.0000],
        [0.7071, 1.4142, 1.4142],
        [0.0000, 1.4142, 2.8284]])
```

**The causal mask for `T = 3`:**

```
tensor([[False,  True,  True],
        [False, False,  True],
        [False, False, False]])
```

**After `masked_fill`:**

```
tensor([[0.7071,   -inf,   -inf],
        [0.7071, 1.4142,   -inf],
        [0.0000, 1.4142, 2.8284]])
```

Position 0 had a score of `0.7071` for position 1; it is gone. Position 1 had `1.4142` for position 2; gone.

**Softmax of each row, by hand.**

| Row | `e^score` for each allowed entry | Sum | Weights |
|---|---|---|---|
| 0 | `e^0.7071 = 2.0281` | `2.0281` | `2.0281 / 2.0281 = 1` |
| 1 | `e^0.7071 = 2.0281`, `e^1.4142 = 4.1133` | `6.1414` | `0.3302`, `0.6698` |
| 2 | `e^0 = 1`, `e^1.4142 = 4.1133`, `e^2.8284 = 16.9188` | `22.0321` | `0.0454`, `0.1867`, `0.7679` |

Real output of `torch.softmax(scores, dim=-1)`:

```
tensor([[1.0000, 0.0000, 0.0000],
        [0.3302, 0.6698, 0.0000],
        [0.0454, 0.1867, 0.7679]])
```

Each row sums to 1. The upper triangle is exactly zero.

**Multiply by the values** (`v` is the input here). Row 1 by hand: `0.3302 × [1, 0] + 0.6698 × [1, 1] = [1.0000, 0.6698]`. Row 2: `0.0454 × [1, 0] + 0.1867 × [1, 1] + 0.7679 × [0, 2] = [0.2321, 1.7225]`. Real output, and the output of calling the module itself on the same input:

```
tensor([[1.0000, 0.0000],
        [1.0000, 0.6698],
        [0.2321, 1.7225]])
```

Read the result: position 0 could only see itself, so it is unchanged. Position 1 became a blend of positions 0 and 1, leaning towards itself. Position 2 became mostly itself with a little of the two earlier positions. No row contains anything from a later position. In the real model the same thing happens with 32-number slices, four heads, and learned matrices deciding what counts as a match.

### 7.5 The transformer block

| | |
|---|---|
| **INPUT** | `x`, shape `[B, T, 128]`. |
| **PROCESS** | Normalise, run attention, add the result onto `x`. Normalise again, run a small two-layer network on each position, add the result onto `x`. |
| **OUTPUT** | `x`, shape `[B, T, 128]`, with each position's vector refined. |
| **WHY IT EXISTS** | Attention alone only moves information around (it is a weighted average). The feed-forward network is where each position *computes* something with what it gathered. A block is one round of "gather, then think". Stacking four of them gives four rounds. |

#### `src/model/transformer.py`

**Why this file exists.** It defines the unit that is repeated `num_layers` times to form the body of the model, and the feed-forward network that unit contains.

**What enters / what leaves.** Two classes, both built from a `ModelConfig`. Both `forward` methods take a tensor `[B, T, d_model]` and return a tensor of the same shape.

**How it connects.** `TransformerBlock` is created four times by `TinyLLM` (7.6). It creates one `CausalSelfAttention` (7.4) and one `FeedForward` (this file).

**The code, section by section.**

```python
import torch
from torch import nn

from src.model.attention import CausalSelfAttention
from src.model.config import ModelConfig
```

Same `torch` and `nn` as before, plus the attention class from 7.4 and the config.

```python
class FeedForward(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()

        hidden_size = 4 * config.d_model
```

`hidden_size` is `4 × 128 = 512`. It is a local variable, used only to build the layers below. The factor 4 is written directly in the code; it is not a config field.

```python
        self.net = nn.Sequential(
            nn.Linear(
                config.d_model,
                hidden_size,
            ),
            nn.GELU(),
            nn.Linear(
                hidden_size,
                config.d_model,
            ),
            nn.Dropout(
                config.dropout
            ),
        )
```

**What Python/PyTorch does.** `nn.Sequential` is a container module: it holds layers in order, and calling it passes the input through the first, the result through the second, and so on. PyTorch numbers the layers `0` to `3`, which is why their parameters appear later under names like `feed_forward.net.0.weight`. The four layers, as printed by PyTorch:

```
Sequential(
  (0): Linear(in_features=128, out_features=512, bias=True)
  (1): GELU(approximate='none')
  (2): Linear(in_features=512, out_features=128, bias=True)
  (3): Dropout(p=0.0, inplace=False)
)
```

| # | Layer | Shape in → out (real run) | Parameters |
|---|---|---|---|
| 0 | `Linear(128, 512)` | `[2, 5, 128]` → `[2, 5, 512]` | weight `[512, 128]` + bias `[512]` |
| 1 | `GELU()` | `[2, 5, 512]` → `[2, 5, 512]` | none |
| 2 | `Linear(512, 128)` | `[2, 5, 512]` → `[2, 5, 128]` | weight `[128, 512]` + bias `[128]` |
| 3 | `Dropout(0.0)` | `[2, 5, 128]` → `[2, 5, 128]` | none; does nothing at `0.0` |

Unlike the attention projections, these two `Linear` layers do not pass `bias=False`, so they keep the default bias vector.

**GELU** is the **activation function**: a fixed formula applied to each number separately. It lets positive numbers through almost unchanged and squashes negative numbers to nearly zero, with a smooth bend in between instead of a sharp corner. Real output:

```
input    [-2.0,    -1.0,     0.0,    1.0,    2.0   ]
GELU     [-0.0455, -0.1587,  0.0000, 0.8413, 1.9545]
```

**What it means in the LLM.** Without an activation between them, two `Linear` layers in a row would be pointless: a weighted sum of weighted sums is just another weighted sum, so the pair could be replaced by one layer. The bend introduced by GELU is what makes the network able to compute things that are not simple weighted sums — "if this feature and that feature are both present, then…".

The shape of the network is expand, bend, compress: 128 numbers are spread across 512 "detectors", each detector either fires or stays near zero, and the 512 results are combined back into 128 numbers. The widening gives the layer room: 512 different conditions can be tested per position.

This network has no interaction between positions. `Linear` and `GELU` act on the last dimension, so position 3's output depends only on position 3's input. All mixing between positions was done by attention just before.

```python
    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        return self.net(x)
```

Runs the four layers in order. Verified: input `[2, 5, 128]`, output `[2, 5, 128]`.

```python
class TransformerBlock(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()

        self.norm1 = nn.LayerNorm(
            config.d_model
        )

        self.attention = CausalSelfAttention(
            config
        )

        self.norm2 = nn.LayerNorm(
            config.d_model
        )

        self.feed_forward = FeedForward(
            config
        )
```

The block owns four sub-modules: two normalisation layers and the two sub-layers they feed. The two `LayerNorm`s are separate objects with separate parameters.

**What Python/PyTorch does: `nn.LayerNorm(128)`.** For each position's vector of 128 numbers, on its own:

1. compute the mean of the 128 numbers and subtract it from each;
2. compute their standard deviation (how spread out they are) and divide each by it (a tiny constant, `eps = 1e-05`, is added inside the square root so the division can never be by zero);
3. multiply each of the 128 numbers by a learned number and add another learned number.

Steps 1–2 leave a vector with mean 0 and standard deviation 1. Step 3 uses the layer's two parameters, `weight` and `bias`, each of shape `[128]`. They start as all ones and all zeros (verified), so a fresh `LayerNorm` does only steps 1–2; training can then rescale each of the 128 slots if that helps. Shape in equals shape out.

Real output on a four-number vector (fresh layer, so only steps 1–2 have an effect):

```
input           [1.0, 2.0, 3.0, 6.0]        mean 3.0, standard deviation 1.8708
LayerNorm       [-1.0690, -0.5345, 0.0000, 1.6036]
```

`(1 − 3) / 1.8708 = −1.069`. And on the real model's data: after multiplying an embedding output by 3 and adding 2, `LayerNorm` still returned a vector with mean `0.000000004` and standard deviation `0.9999998`.

"Layer" in the name means it normalises across the features of one position. It does not look at other positions or other sequences in the batch, so a sequence's result does not depend on what else is in the batch.

**What it means in the LLM.** Every block adds something to `x` (see below), so without control the numbers in `x` could grow or shrink from block to block. A sub-layer that receives inputs of unpredictable size is hard to train: the same weights that work for small inputs misbehave for large ones. `LayerNorm` guarantees that attention and the feed-forward network always receive vectors of the same overall scale, whatever happened before. Only the *pattern* across the 128 numbers reaches the sub-layer, not their absolute size.

```python
    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:

        x = x + self.attention(
            self.norm1(x)
        )
```

This single statement contains three ideas: the order of normalisation, the attention sub-layer, and the residual connection.

**What Python/PyTorch does.** Evaluated inside-out:

1. `self.norm1(x)` — a normalised **copy** of `x`, `[2, 5, 128]`. `x` itself is not modified.
2. `self.attention(…)` — attention is run on that normalised copy, `[2, 5, 128]`.
3. `x + …` — the attention output is added, number by number, to the **original, un-normalised** `x`. This creates a new tensor.
4. `x = …` — the name `x` is pointed at that new tensor. The old tensor is not overwritten in place; the name just moves.

**What it means in the LLM: the order.** Normalisation comes *before* the sub-layer and sits inside the side branch only. This arrangement is called **pre-norm**. The main path `x → x + … → x + …` is never normalised inside a block; `LayerNorm` only prepares the input of each sub-layer. (The alternative, "post-norm", would be `x = norm(x + attention(x))`; this code does not do that.)

**What it means in the LLM: the residual connection.** `x = x + f(x)` instead of `x = f(x)` is called a **residual** or **skip** connection. The sub-layer does not produce the new `x`; it produces a *correction* that is added to the old one.

Picture `x` as a running notepad for each position, 128 numbers wide, that flows straight through the model from the embedding to the output head. Each attention layer and each feed-forward network reads the notepad and writes an addition onto it. Nothing is ever erased by replacement.

Why deep networks need this:

- **Information is not lost.** With `x = f(x)`, anything a layer fails to pass on is gone for all later layers; the token's own identity would have to be re-encoded by every layer. With `x = x + f(x)`, whatever was on the notepad stays unless a layer actively writes its opposite.
- **A layer can start by doing nothing.** At the beginning the weights are random and `f(x)` is noise of modest size. `x + noise` is still mostly `x`. A stack of four `f`s applied one inside the other would scramble the signal; a stack of four additions does not.
- **The learning signal reaches every layer.** Training works by sending a correction signal backwards from the output through every operation (chapter 8). Through a chain of `f(f(f(f(x))))` that signal is multiplied at every step and tends to fade or blow up. Addition passes it back unchanged, so the `+` gives the signal a direct road from the output to every block, however many blocks there are.

```python
        x = x + self.feed_forward(
            self.norm2(x)
        )

        return x
```

The same pattern a second time, with the second normalisation layer and the feed-forward network. Note that the `x` on the right is already the updated one from the previous statement, so the feed-forward network sees what attention just wrote.

The exact order inside one block, as the code has it:

```
a  = norm1(x)
x  = x + attention(a)
b  = norm2(x)
x  = x + feed_forward(b)
```

Verified: a block given `[2, 5, 128]` returns `[2, 5, 128]`.

### 7.6 The whole model

#### `src/model/model.py`

**Why this file exists.** It assembles the pieces of 7.3–7.5 into the one object the rest of the project uses.

**What enters / what leaves.** The constructor takes a `ModelConfig`. `forward` takes `input_ids` of shape `[B, T]` (integers, `T ≤ context_length`) and returns `logits` of shape `[B, T, vocab_size]` (decimal numbers).

**How it connects.** `TinyLLM` is the class imported by training (`src/training/trainer.py`, `src/training/checkpoint.py`), evaluation (`src/evaluation/evaluator.py`), inference (`src/inference/generator.py`), serving (`src/serving/model_manager.py`) and by the scripts that drive them. They all do the same two things with it: build it from a config, and call it on a tensor of ids.

**The code, section by section.**

```python
import torch
from torch import nn

from src.model.config import ModelConfig
from src.model.embeddings import TokenAndPositionEmbedding
from src.model.transformer import TransformerBlock
```

It imports the config, the embedding module and the block. It does not import `CausalSelfAttention` or `FeedForward`: those are reached through `TransformerBlock`.

```python
class TinyLLM(nn.Module):
    def __init__(self, config: ModelConfig):
        super().__init__()

        self.config = config

        self.embeddings = TokenAndPositionEmbedding(
            config
        )
```

`self.config = config` keeps the config object on the model. A dataclass is not an `nn.Module` or a tensor, so this registers no parameters; it is there so that code holding only the model can ask it for its sizes. The generator does exactly that with `model.config.context_length` (chapter 10).

`self.embeddings` is the module from 7.3.

```python
        self.blocks = nn.ModuleList(
            [
                TransformerBlock(config)
                for _ in range(config.num_layers)
            ]
        )
```

**What Python/PyTorch does.** The inner part is a list comprehension (see the primer in 1): `range(4)` yields four values, and for each one a **new** `TransformerBlock(config)` is constructed. The loop variable is named `_`, the Python convention for "I do not use this value". The result is a list of four different block objects, each with its own randomly initialised weights. They share a design, not parameters.

`nn.ModuleList` wraps that list. It behaves like a list (you can loop over it and index it) but it is also an `nn.Module`, so the four blocks get registered as children. This wrapper is essential: a plain Python list stored on `self` is invisible to PyTorch. The blocks' parameters would then be missing from `model.parameters()`, so they would never be trained, never saved in a checkpoint and never moved to the GPU. The index in the list becomes part of each parameter's name: `blocks.0.…`, `blocks.1.…`, and so on.

**What it means in the LLM.** Depth. Each block is one round of "gather from earlier positions, then compute". The first block can only combine raw tokens. The second block combines the *results* of the first, so it can work with small patterns; the third with patterns of patterns. More layers allow more steps of reasoning about the context, at the cost of more parameters and more computation.

```python
        self.final_norm = nn.LayerNorm(
            config.d_model
        )
```

A ninth `LayerNorm` (each of the four blocks has two). It is needed because of the pre-norm order in 7.5: inside the blocks, normalisation is applied only to the sub-layer inputs, never to the main path. After the last block, `x` is the embedding plus eight un-normalised additions. `final_norm` puts it on a controlled scale once, before the scores are computed.

```python
        self.lm_head = nn.Linear(
            config.d_model,
            config.vocab_size,
            bias=False,
        )
```

**What Python/PyTorch does.** A `Linear` layer from 128 numbers to 300 numbers, without bias. Its only parameter is a weight matrix of shape `[300, 128]`: 38,400 numbers.

**What it means in the LLM.** "lm_head" stands for language-model head: the last layer, which turns the model's internal representation into an answer. The matrix has one row of 128 numbers per token in the vocabulary. The score for token `k` is the dot product of the position's final vector with row `k`. In the language of 7.4: the position's final vector is compared with a learned "signature" of each of the 300 tokens, and the logit says how well they match.

**Are the weights tied to the token embedding?** The token embedding table is also `[300, 128]`, one row per token, and some models save parameters by making the two the same tensor ("weight tying"). **This code does not.** `lm_head` is created as an independent `nn.Linear`, nothing assigns one weight to the other, and a direct check confirms it: `model.lm_head.weight is model.embeddings.token_embedding.weight` is `False`. They are two separate tables of 38,400 parameters each, initialised differently and trained separately. One describes a token when it is read; the other describes a token when it is predicted.

```python
    def forward(
        self,
        input_ids: torch.Tensor,
    ) -> torch.Tensor:

        x = self.embeddings(
            input_ids
        )
```

The complete forward pass is four statements. This is the first: ids become vectors. `[2, 5]` → `[2, 5, 128]`.

```python
        for block in self.blocks:
            x = block(x)
```

An ordinary Python `for` loop over the `ModuleList`. Each block receives the previous block's output and its result replaces `x`. The shape is `[2, 5, 128]` before and after every block. This loop is the reason all blocks must keep the shape unchanged.

```python
        x = self.final_norm(x)

        logits = self.lm_head(x)

        return logits
```

Normalise once (`[2, 5, 128]`, unchanged shape), then project the last dimension from 128 to 300.

**The shape of the result.** `[B, T, vocab_size]`. Verified: an input of shape `[2, 5]` returns `torch.Size([2, 5, 300])` with dtype `torch.float32`. `logits[b, t]` is a row of 300 scores for the token that follows position `t` of sequence `b`. No softmax is applied here: the model returns raw logits. These are what training compares with the true next tokens (chapter 8), and what the generator turns into a choice of token (chapter 10).

Whole-model shape trace, all from a real run with `B = 2`, `T = 5`:

| After | Shape |
|---|---|
| `input_ids` | `[2, 5]` |
| `self.embeddings(input_ids)` | `[2, 5, 128]` |
| each of the 4 blocks | `[2, 5, 128]` |
| `self.final_norm(x)` | `[2, 5, 128]` |
| `self.lm_head(x)` | `[2, 5, 300]` |

**What happens if a sequence is longer than `context_length`.** `TinyLLM.forward` contains no length check and no truncation of its own. The first thing it does is call `self.embeddings`, and that module raises (7.3). Real output for an input of shape `[1, 129]`:

```
ValueError: Sequence length 129 exceeds context length 128
```

An input of shape `[1, 128]` works and returns `[1, 128, 300]`. So the model refuses over-long input; it does not silently cut it. Keeping sequences within the limit is the caller's job: the data loader builds training windows of `context_length` tokens (chapter 8), and the generator keeps only the last `model.config.context_length` tokens before each call (chapter 10).

Shorter sequences need no special handling: nothing in the model depends on `T` being 128. The position table is simply read up to row `T − 1` and the mask is built at size `T × T`.

### 7.7 Counting the parameters

The checkpoint metadata records `total_parameters: 884480` and `trainable_parameters: 884480`. That number can be derived by hand from the config (`vocab_size = 300`, `context_length = 128`, `d_model = 128`, `num_heads = 4`, `num_layers = 4`) using three rules:

- `nn.Embedding(N, D)` has `N × D` parameters.
- `nn.Linear(I, O)` has `I × O` weights, plus `O` biases unless `bias=False`.
- `nn.LayerNorm(D)` has `2 × D` parameters (`weight` and `bias`).

`GELU` and `Dropout` have none. `num_heads` does not appear in any count: heads are a way of slicing the same matrices, not extra matrices.

**Embeddings**

| Layer | Calculation | Parameters |
|---|---|---|
| `token_embedding` | `300 × 128` | 38,400 |
| `position_embedding` | `128 × 128` | 16,384 |
| | | **54,784** |

**One transformer block**

| Layer | Calculation | Parameters |
|---|---|---|
| `norm1` | `128 + 128` | 256 |
| `attention.q_proj` | `128 × 128`, no bias | 16,384 |
| `attention.k_proj` | `128 × 128`, no bias | 16,384 |
| `attention.v_proj` | `128 × 128`, no bias | 16,384 |
| `attention.out_proj` | `128 × 128`, no bias | 16,384 |
| `norm2` | `128 + 128` | 256 |
| `feed_forward.net.0` | `128 × 512 + 512` | 66,048 |
| `feed_forward.net.2` | `512 × 128 + 128` | 65,664 |
| | | **197,760** |

Four blocks: `4 × 197,760 = 791,040`.

**After the blocks**

| Layer | Calculation | Parameters |
|---|---|---|
| `final_norm` | `128 + 128` | 256 |
| `lm_head` | `128 × 300`, no bias | 38,400 |

**Total**

```
embeddings      54,784
4 blocks       791,040
final_norm         256
lm_head         38,400
              --------
               884,480
```

That matches the checkpoint. Now the same count taken from the model itself. `model.named_parameters()` yields every parameter tensor with its dotted name; `p.numel()` ("number of elements") is the count of numbers in it, the product of its shape.

```python
from src.model.config import ModelConfig
from src.model.model import TinyLLM

model = TinyLLM(ModelConfig())
total = 0
for name, p in model.named_parameters():
    total += p.numel()
    print(f"{name:45s} {str(tuple(p.shape)):14s} {p.numel():>8,d}")
print("TOTAL", total)
```

Real output (the 12 lines of `blocks.1`, `blocks.2` and `blocks.3` are identical to those of `blocks.0` apart from the index and are left out here):

```
embeddings.token_embedding.weight             (300, 128)       38,400
embeddings.position_embedding.weight          (128, 128)       16,384
blocks.0.norm1.weight                         (128,)              128
blocks.0.norm1.bias                           (128,)              128
blocks.0.attention.q_proj.weight              (128, 128)       16,384
blocks.0.attention.k_proj.weight              (128, 128)       16,384
blocks.0.attention.v_proj.weight              (128, 128)       16,384
blocks.0.attention.out_proj.weight            (128, 128)       16,384
blocks.0.norm2.weight                         (128,)              128
blocks.0.norm2.bias                           (128,)              128
blocks.0.feed_forward.net.0.weight            (512, 128)       65,536
blocks.0.feed_forward.net.0.bias              (512,)              512
blocks.0.feed_forward.net.2.weight            (128, 512)       65,536
blocks.0.feed_forward.net.2.bias              (128,)              128
...
final_norm.weight                             (128,)              128
final_norm.bias                               (128,)              128
lm_head.weight                                (300, 128)       38,400
TOTAL 884480
```

There are 53 parameter tensors in all: `2 + 4 × 12 + 2 + 1`. Grouped by top-level part, also real output:

```
embeddings 54,784
blocks.0 197,760
blocks.1 197,760
blocks.2 197,760
blocks.3 197,760
final_norm 256
lm_head 38,400
```

Things this table shows:

- The names are the attribute names from the code, joined with dots: `blocks.0.attention.q_proj.weight` is `self.blocks[0].attention.q_proj.weight`. A checkpoint stores the tensors under exactly these names, which is why renaming an attribute in `src/model/` makes older checkpoints unloadable.
- A `Linear(128, 512)` weight is stored as `(512, 128)`: `[out, in]`.
- The four blocks hold 791,040 of the 884,480 parameters, about 89%. Inside each block the feed-forward network (131,712) is twice the size of attention (65,536). The two token tables together (76,800) are under 9%.
- `lm_head.weight` and `token_embedding.weight` are listed separately with 38,400 each: the untied tables of 7.6.
- All 884,480 are trainable; the model has no fixed (non-trained) tensors. The causal mask is recomputed on each call and is not stored at all.

#### What I should understand before moving on

- The model is a function from token ids `[B, T]` to logits `[B, T, 300]`. Row `t` of the output is a score for every possible token at position `t + 1`, computed from positions `0..t` only.
- Between the embedding and the output head the data is always `[B, T, 128]`. Blocks do not change the shape; they rewrite the contents by adding to them.
- An embedding is a table lookup. The input vector for a position is its token's row plus its position's row. The position table has 128 rows, and that is what limits the model to 128 tokens: longer input raises `ValueError`.
- Attention is the only place where positions exchange information. Queries and keys produce a `T × T` table of scores; the causal mask writes `-inf` above the diagonal; softmax turns each row into weights that sum to 1 with exact zeros for the future; the weights average the value vectors.
- Heads are made by `view` and `transpose`, not by separate layers: four 32-number slices of the same 128-number projections, processed in parallel and merged back.
- Each block is pre-norm with two residual additions: `x = x + attention(norm1(x))`, then `x = x + feed_forward(norm2(x))`. The feed-forward network is 128 → 512 → GELU → 128 and acts on each position separately.
- `TinyLLM` is: embeddings → 4 blocks → `final_norm` → `lm_head`. The output head is an independent `Linear(128, 300)` without bias; it is not tied to the token embedding.
- The model has 884,480 parameters, about 89% of them in the four blocks. Dropout is present in the code but set to `0.0`, so it currently changes nothing.

#### Self-test

1. You call the model on a tensor of shape `[3, 10]`. What is the shape of the result, and what does the row at `[1, 4]` of the result represent?
2. In `TokenAndPositionEmbedding.forward`, `token_vectors` has shape `[B, T, 128]` and `position_vectors` has shape `[T, 128]`. How can they be added, and why does `position_vectors` not need a batch dimension?
3. In attention, why is `transpose(1, 2)` applied after `view(batch_size, sequence_length, self.num_heads, self.head_dim)`? What would the `@` on the next line compare if it were left out?
4. A row of scaled scores for position 1 of a 3-token sequence is `[0.5, 0.5, 9.0]`. What are the attention weights for that row after the mask and softmax, and why does the `9.0` not matter?
5. Why is the mask applied by putting `-inf` into the scores before softmax, instead of multiplying the weights by zero after softmax?
6. In `x = x + self.attention(self.norm1(x))`, which tensor does attention read, and which tensor is its result added to? What would be lost if the line were `x = self.attention(self.norm1(x))`?
7. Suppose `self.blocks` were a plain Python list instead of an `nn.ModuleList`. The forward pass would still run. What would go wrong?
8. If `d_model` were changed to `256` and everything else kept, how many parameters would `q_proj` in one block have, and how many would `lm_head` have? Why can you not load the existing checkpoint into such a model?

<details><summary>Answers</summary>

1. `[3, 10, 300]`. The row at `[1, 4]` is 300 logits: the second sequence's scores for which token comes at position 5 (the sixth token), computed from that sequence's positions 0–4.
2. By broadcasting: PyTorch aligns shapes from the right and repeats the `[T, 128]` tensor for each of the `B` sequences. Positions depend only on the sequence length, not on the content, so every sequence in the batch uses the same position vectors.
3. `@` multiplies the last two dimensions and treats the leading ones as independent copies. After `view` the shape is `[B, T, heads, 32]`; the transpose makes it `[B, heads, T, 32]` so that the last two dimensions are positions × numbers and each head is handled independently. Without it, `@` would multiply `[heads, 32]` tables per position: it would compare heads with heads inside one position, and positions would never be compared with each other.
4. Position 1 may see positions 0 and 1 only, so the row becomes `[0.5, 0.5, -inf]`. The two allowed scores are equal, so the weights are `[0.5, 0.5, 0]`. The `9.0` belongs to position 2, which is in the future; it is overwritten before softmax and contributes `e^(-inf) = 0`.
5. Softmax makes the weights sum to 1 over whatever it is given. With `-inf` the forbidden entries get exactly zero and the allowed ones sum to 1 by themselves. Zeroing after softmax would leave the allowed weights summing to less than 1 (and to a different amount in each row), because some of the total had been spent on the forbidden entries.
6. Attention reads the normalised copy `norm1(x)`. Its result is added to the original, un-normalised `x`. Without the `x +`, the block's output would be only what attention produced: the position's previous contents (including the token's own embedding) would survive only if attention happened to reproduce them, a randomly initialised stack would scramble the signal layer after layer, and the direct path through the additions that lets every layer be trained would be gone.
7. PyTorch would not register the blocks as children. Their 791,040 parameters would be missing from `model.parameters()` and `model.state_dict()`: they would not be updated in training, not saved in checkpoints, and not moved by `model.to(device)`. Only the embeddings, `final_norm` and `lm_head` would be seen.
8. `q_proj`: `256 × 256 = 65,536`. `lm_head`: `256 × 300 = 76,800`. The checkpoint stores tensors by name and shape (for example `lm_head.weight` as `[300, 128]`); the new model would expect `[300, 256]`, so the shapes do not match. This is why the config is saved inside the checkpoint and the model is rebuilt from it.

</details>

---

## 8. Training

| | |
|---|---|
| **INPUT** | `storage/training/tokenized/train.jsonl` (token ids, one document per line), optionally `storage/training/tokenized/validation.jsonl`, the settings in `configs/training.json`, a freshly built `TinyLLM` with random weights, and — if one exists — the previous checkpoint `artifacts/checkpoints/tiny_model.pt`. |
| **PROCESS** | For every epoch, walk through the training examples one at a time: predict the next token at every position, measure the error with cross-entropy, compute gradients with backpropagation, and let AdamW adjust every parameter. After each configured epoch, optionally measure validation loss, then save a checkpoint. |
| **OUTPUT** | `artifacts/checkpoints/tiny_model.pt` (latest), `artifacts/checkpoints/checkpoint_epoch_<E>_step_<S>.pt` (history), `artifacts/checkpoints/best_tiny_model.pt` (only when validation data exists), and `artifacts/runs/<run_id>/run.json` (a record of the run). |
| **WHY IT EXISTS** | The model from chapter 7 is only a structure filled with random numbers. Training is the only step that puts knowledge of the corpus into those numbers. Everything after this stage (evaluation, inference, serving) loads the checkpoint that this stage writes. |

The stage is five files under `src/training/`:

| File | Lines | Role |
|---|---|---|
| `src/training/config.py` | 31 | Reads `configs/training.json` into a dictionary. |
| `src/training/trainer.py` | 318 | The training loop itself. |
| `src/training/checkpoint.py` | 164 | Saves and loads checkpoint files. |
| `src/training/run.py` | 97 | Writes a `run.json` record for each training run. |
| `src/training/optimizer.py` | 0 | Empty. |

### 8.1 What training is

Chapter 7 built `TinyLLM`: a function that takes token ids and returns, for every position, 300 scores (one per token in the vocabulary) saying how likely each token is to come next. Those scores are computed from 884,480 numbers called **parameters** (also called **weights**). When the model is created, the parameters are random, so the scores are meaningless.

Training turns the random parameters into useful ones by repeating one small cycle:

1. **Show** the model a sequence of tokens from the corpus.
2. **Ask** it to predict, at every position, which token comes next.
3. **Measure** how wrong the predictions are. The measurement is a single number, the **loss**. High loss means the model gave low probability to the tokens that actually came next.
4. **Work out**, for every one of the 884,480 parameters, whether making it slightly bigger or slightly smaller would have reduced the loss. That direction-and-size information is the **gradient**.
5. **Nudge** every parameter a tiny amount in the direction that reduces the loss.

Nothing else happens. The model is never told grammar or facts; it only gets less wrong at next-token prediction, one nudge at a time. Whatever it appears to "know" later is a side effect of having become good at that prediction on your corpus.

Four words describe how much of this cycle has happened. In this codebase they mean exactly this:

| Word | Meaning in this code | Where it lives |
|---|---|---|
| **example** | One pair `(x, y)` of token-id tensors, each at most `context_length` = `128` tokens long. `x` is a slice of a document; `y` is the same slice moved one token to the right, so `y[i]` is the correct answer for "what comes after `x[0..i]`". | produced by `make_training_examples` in `src/dataset/loader.py` (chapter 5) |
| **step** | One run of the cycle above on one example: one forward pass, one loss, one backward pass, one parameter update. Because this trainer feeds one example at a time, one step = one example. | counted in `global_step` |
| **epoch** | One complete pass over every example in `train.jsonl`. | the outer `for epoch in range(...)` loop |
| **tokens_seen** | The running total of next-token targets the model has been scored on: the number of elements in `y`, added up over every step of every epoch. A token that is seen again in a later epoch is counted again. | counted in `tokens_seen` |

Real numbers from the checkpoint that exists today make this concrete. The tokenized training file currently holds one document of 259 token ids. With a context length of 128 it yields 3 examples with 128, 128 and 2 targets (258 targets in total, which is 259 minus 1, because the last token has nothing after it to predict). So:

| Quantity | Value | Arithmetic |
|---|---|---|
| steps per epoch | `3` | 3 examples |
| targets per epoch | `258` | 128 + 128 + 2 |
| epochs completed | `21` | from `configs/training.json` |
| `global_step` | `63` | 21 × 3 |
| `tokens_seen` | `5418` | 21 × 258 |

These are the values stored in `training_stats` inside `artifacts/checkpoints/tiny_model.pt`.

### 8.2 Loading the training settings

#### `src/training/config.py`

**Why this file exists** — The number of epochs, the learning rate and the checkpoint policy should be changeable without editing Python code. This file reads them from `configs/training.json` and hands them to the rest of the program as a plain dictionary.

**What enters / what leaves** — No arguments. It reads one file, `configs/training.json`. It returns a `dict`. It writes nothing. It raises `FileNotFoundError` if the file is missing and `ValueError` if the file is valid JSON but not a JSON object.

**How it connects** — `scripts/train.py` calls `load_training_config()` first thing. The returned dictionary is then passed, whole, to `create_run` (8.5), to `train` (8.3) and from there into every checkpoint (8.4). Chapter 3 explains the JSON file itself; this section covers only how it is loaded and which keys are read.

**The code, section by section**

```python
import json

from paths import PROJECT_DIR


TRAINING_CONFIG_PATH = (
    PROJECT_DIR
    / "configs"
    / "training.json"
)
```

`json` is Python's standard-library module for reading and writing JSON text. `PROJECT_DIR` comes from `paths.py` and is the project folder as a `Path`. The `/` operator joins path pieces (see the primer in 1), so `TRAINING_CONFIG_PATH` is `configs/training.json` inside the project. The parentheses only allow the expression to span several lines. This line runs once, when the module is first imported.

```python
def load_training_config() -> dict:
    if not TRAINING_CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Training config not found: "
            f"{TRAINING_CONFIG_PATH}"
        )
```

`is_file()` returns `True` only when the path exists and is a regular file. If it does not, the function stops with a clear message instead of letting `open` fail with a less helpful one. The two f-strings sit next to each other with no operator between them; Python joins adjacent string literals into one.

```python
    with TRAINING_CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)
```

Opens the file for reading as UTF-8 text and lets `json.load` parse it. JSON objects become Python dictionaries, JSON numbers become `int` or `float`, and `true` becomes `True`. With today's file, `config` is:

```python
{'epochs': 21, 'learning_rate': 0.0003, 'resume': True, 'checkpoint_every_epochs': 1, 'keep_last_checkpoints': 3}
```

```python
    if not isinstance(config, dict):
        raise ValueError(
            "training.json must contain a JSON object"
        )

    return config
```

A JSON file may legally contain a list or a bare number. `isinstance(config, dict)` rejects those, because the rest of the code uses `config[...]` and `config.get(...)`. This is the only validation: the function does not check which keys are present or what type their values have.

**Which keys are read, and by whom**

| Key | Read by | How | If missing |
|---|---|---|---|
| `epochs` | `scripts/train.py` | `training_config["epochs"]` | `KeyError` |
| `learning_rate` | `scripts/train.py` | `training_config["learning_rate"]` | `KeyError` |
| `resume` | `scripts/train.py` | `training_config.get("resume", True)` | treated as `True` |
| `checkpoint_every_epochs` | `train` in `trainer.py` | `training_config.get("checkpoint_every_epochs", 1)` | treated as `1` |
| `keep_last_checkpoints` | `train` in `trainer.py` | `training_config.get("keep_last_checkpoints", 3)` | treated as `3` |

Square brackets demand that a key exists; `.get(key, default)` returns the default when it does not. Any other key you add to the JSON file is ignored by the logic but is still copied into the checkpoint and into `run.json`, because the dictionary is stored whole.

### 8.3 The training loop

#### `src/training/trainer.py`

**Why this file exists** — It contains the one function, `train`, that actually changes the model's parameters. Everything in chapters 4–7 prepared its inputs; everything in chapters 9–11 uses its output.

**What enters / what leaves** — `train` receives the model, its `ModelConfig`, the path of the tokenized training file, the target number of epochs, the learning rate, the path where the latest checkpoint is written, the training-config dictionary, an optional already-loaded checkpoint to resume from, and an optional validation file path. It reads the training file once per epoch (and the validation file at each checkpoint). It writes checkpoint files through `save_checkpoint`. It returns a dictionary of statistics. It prints progress lines to the terminal. The second function, `get_device`, takes nothing and returns the device to compute on.

**How it connects** — `scripts/train.py` calls `get_device` and `train`. `train` pulls examples from `src/dataset/loader.py` (chapter 5), calls the model from `src/model/model.py` (chapter 7), calls `evaluate` from `src/evaluation/evaluator.py` (chapter 9) and `save_checkpoint` from `src/training/checkpoint.py` (8.4). `scripts/evaluate.py` also imports `get_device` from here.

**The code, section by section**

**Imports**

```python
import time
from pathlib import Path

import torch
from torch import nn

from src.dataset.loader import make_training_examples
from src.evaluation.evaluator import evaluate
from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.training.checkpoint import save_checkpoint
```

| Import | What it is | Why this file needs it |
|---|---|---|
| `time` | Standard-library clock functions. | `time.perf_counter()` measures how long training took. |
| `Path` | Object-style file paths (primer in 1). | Only for the type hints of `train_path`, `checkpoint_path`, `validation_path`. |
| `torch` | PyTorch, the tensor and automatic-differentiation library (chapter 7). | Device selection and the optimizer `torch.optim.AdamW`. |
| `nn` | PyTorch's neural-network building blocks. | `nn.CrossEntropyLoss`, the loss function. |
| `make_training_examples` | Generator of `(x, y)` pairs (chapter 5). | The source of training examples. |
| `evaluate` | Loss measurement without learning (chapter 9). | Validation during training. |
| `ModelConfig`, `TinyLLM` | The model's settings and class (chapter 7). | Type hints, plus `config.context_length` and `config.vocab_size`. |
| `save_checkpoint` | Writes checkpoint files (8.4). | Called after epochs. |

**`get_device`**

```python
def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")

    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")
```

A **device** is the piece of hardware that holds the tensors and does the arithmetic. PyTorch supports three that matter here:

| Device string | Hardware | Checked by |
|---|---|---|
| `"cuda"` | An NVIDIA graphics card. | `torch.cuda.is_available()` |
| `"mps"` | The graphics processor in Apple-silicon Macs ("Metal Performance Shaders"). | `torch.backends.mps.is_available()` |
| `"cpu"` | The ordinary processor. Always available. | fallback |

The function tries them from fastest to slowest and returns the first one that exists. `torch.device("mps")` does not move anything; it only creates a small label object that is later given to `.to(...)`. On the machine that produced today's checkpoint the result is `mps` (the run record in `artifacts/runs/` says `"device": "mps"`).

The rule that makes devices matter: every tensor taking part in one operation must be on the same device. The model's parameters and the input tensors therefore both have to be moved to the chosen device, which is exactly what the next lines and the lines inside the loop do.

**The signature of `train`**

```python
def train(
    model: TinyLLM,
    config: ModelConfig,
    train_path: Path,
    epochs: int,
    learning_rate: float,
    checkpoint_path: Path,
    training_config: dict,
    resume_checkpoint: dict | None = None,
    validation_path: Path | None = None,
) -> dict:
```

| Parameter | Meaning |
|---|---|
| `model` | The `TinyLLM` to train. It is modified in place; the caller's variable sees the trained weights afterwards. |
| `config` | The model's settings. Used for `context_length` (how long examples are) and `vocab_size` (to reshape the logits), and passed on to the checkpoint. |
| `train_path` | The tokenized training file. |
| `epochs` | The **total** number of epochs the model should have completed when the function returns — not "how many more". This matters for resume. |
| `learning_rate` | How large each parameter nudge is (explained below). |
| `checkpoint_path` | Where the latest checkpoint goes. History and best files are placed next to it. |
| `training_config` | The whole dictionary from 8.2. Two keys are read from it; the dictionary is also stored in each checkpoint. |
| `resume_checkpoint` | A checkpoint dictionary already loaded from disk, or `None` to start from scratch. |
| `validation_path` | A tokenized validation file, or `None`. |

`dict | None = None` means "a dictionary or `None`, and `None` if the caller does not pass it". The return type is `dict`.

**Device, training mode**

```python

    device = get_device()

    model.to(device)
    model.train()
```

**What Python/PyTorch does** — `model.to(device)` moves every parameter tensor inside the model to the device. For an `nn.Module` this happens in place: the same model object now holds tensors that live on the GPU. `model.train()` sets a flag (`model.training = True`) on the model and all its sub-modules.

**What it means in the LLM/pipeline** — Some layers behave differently while learning than while being used. Dropout (chapter 7) randomly zeroes values only in training mode. `model.train()` switches that behaviour on; `model.eval()` (chapter 9) switches it off. In this project `dropout` is `0.0`, so today the two modes compute exactly the same numbers, but the calls are in the right places for when dropout is raised.

**The optimizer and the loss function**

```python

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
    )

    loss_function = nn.CrossEntropyLoss()
```

These two objects are created once and used on every step.

`model.parameters()` yields every learnable tensor in the model — 53 tensors holding 884,480 numbers in total (token embedding, position embedding, the attention and feed-forward weights of four blocks, the layer norms, and the output layer). Handing them to the optimizer tells it: "these are the numbers you are allowed to change".

An **optimizer** is the rule that turns gradients into parameter changes. The simplest possible rule is

```
new_value = old_value - learning_rate × gradient
```

**AdamW** is a more careful version of that rule. It does three things on top of it:

| Idea | What AdamW does | Why it helps |
|---|---|---|
| **Momentum** | For every parameter it keeps a running average of recent gradients and moves along that average instead of the latest gradient alone. | A single example gives a noisy gradient. Averaging over recent steps smooths the noise and keeps progress going in a consistent direction. |
| **Per-parameter scaling** | For every parameter it also keeps a running average of recent *squared* gradients, and divides the step by the square root of it. | Parameters whose gradients are usually large take proportionally smaller steps; parameters with small gradients take larger ones. Each parameter effectively gets its own step size, and the typical step is roughly `learning_rate` regardless of how large the raw gradients are. |
| **Decoupled weight decay** | Separately from the gradient, on every step each parameter is shrunk a little toward zero: multiplied by `(1 − learning_rate × weight_decay)`. "Decoupled" means this shrinking is applied directly to the parameter and is not mixed into the gradient averages. That separation is the "W" in AdamW. | Keeps weights from growing without limit, which is a mild guard against memorising the training data. |

Which settings does this code pass, and which does it leave alone? It passes exactly two things: the parameters and `lr`. Everything else is PyTorch's default. Reading the optimizer's settings back from an optimizer built the same way gives:

| Setting | Value | Passed by this code? | Meaning |
|---|---|---|---|
| `lr` | `0.0003` | yes, from `training.json` | The learning rate. |
| `betas` | `(0.9, 0.999)` | no, default | How long the two running averages remember. `0.9` for momentum: each new gradient contributes 10 %. `0.999` for the squared-gradient average: each contributes 0.1 %. |
| `eps` | `1e-08` | no, default | A tiny number added to the divisor so the division can never be by zero. |
| `weight_decay` | `0.01` | no, default | The shrink factor described above. With `lr` = `0.0003` each step multiplies each parameter by `1 − 0.000003`. |
| `amsgrad` | `False` | no, default | An optional variant; off. |

Because the parameters are passed as one flat group, the weight decay applies equally to every parameter tensor, including biases, layer-norm weights and both embedding tables.

The **learning rate** is the single most important number here. It sets the size of each nudge. Too large and the updates overshoot, so the loss jumps around or grows; too small and the loss falls so slowly that training appears stuck. `0.0003` is a common, moderate value for AdamW on small transformers. In this code it is constant for the whole of training: there is no warm-up and no decay schedule.

`nn.CrossEntropyLoss()` creates the loss function. It is an object you call like a function: `loss_function(predictions, targets)`. What it computes is explained at the line where it is called.

**Counters and their starting values**

```python

    start_epoch = 0
    global_step = 0
    tokens_seen = 0
    previous_training_seconds = 0.0
    final_loss = None
    validation_loss = None
    best_validation_loss = None
```

These are the values for a brand-new training run. If a checkpoint is being resumed, the next block overwrites every one of them.

| Variable | Meaning |
|---|---|
| `start_epoch` | How many epochs are already done. `0` for a fresh run. |
| `global_step` | Total parameter updates so far, across all epochs and all earlier runs. |
| `tokens_seen` | Total next-token targets scored so far. |
| `previous_training_seconds` | Time spent training in earlier runs, so the total keeps adding up across resumes. |
| `final_loss` | Average training loss of the most recent epoch. `None` until an epoch finishes. |
| `validation_loss` | Most recent validation loss. `None` until one is measured. |
| `best_validation_loss` | Lowest validation loss ever measured. `None` until one is measured. |

**Resume: restoring weights and optimizer state**

```python

    # --------------------------------------------------
    # Resume from checkpoint
    # --------------------------------------------------

    if resume_checkpoint is not None:
        model.load_state_dict(
            resume_checkpoint["model_state_dict"]
        )

        optimizer_state = resume_checkpoint.get(
            "optimizer_state_dict"
        )

        if optimizer_state is not None:
            optimizer.load_state_dict(
                optimizer_state
            )
```

**Resuming** means continuing training from where an earlier run stopped instead of starting again from random weights. `resume_checkpoint` is the dictionary that `load_checkpoint` read from `tiny_model.pt` (8.4 lists its keys).

**What Python/PyTorch does** — `model.load_state_dict(d)` copies every tensor in the dictionary `d` into the model parameter with the same name. If a name is missing or a shape differs, it raises an error. `optimizer.load_state_dict(d)` does the same for the optimizer's internal state. `resume_checkpoint.get("optimizer_state_dict")` returns `None` rather than failing if a checkpoint has no such key, and the `if` then skips the restore.

**What it means in the LLM/pipeline** — Two separate things have to come back for training to continue smoothly:

- The **model weights**: the random numbers the caller just created are replaced by the trained ones.
- The **optimizer state**: AdamW's two running averages for every parameter (momentum and squared gradients) and its internal step count. Without them AdamW would restart its averages from zero and the first steps after a resume would behave differently from the steps before it.

One consequence is worth knowing. The optimizer's saved state also contains its settings, including the learning rate. `optimizer.load_state_dict` restores those too, replacing the `lr` that was passed a few lines earlier. So if you resume from a checkpoint after editing `learning_rate` in `training.json`, the optimizer keeps stepping with the checkpoint's old learning rate. This was checked with a throw-away model: a run saved at `0.0003` and resumed with `learning_rate=0.01` wrote a new checkpoint whose optimizer state still said `lr` = `0.0003`, while its `training_stats["learning_rate"]` said `0.01`.

**Resume: restoring the counters**

```python

        previous_stats = resume_checkpoint.get(
            "training_stats",
            {},
        )

        start_epoch = previous_stats.get(
            "epochs_completed",
            0,
        )

        global_step = previous_stats.get(
            "global_step",
            0,
        )

        tokens_seen = previous_stats.get(
            "tokens_seen",
            0,
        )

        previous_training_seconds = previous_stats.get(
            "training_seconds",
            0.0,
        )

        final_loss = previous_stats.get(
            "final_loss"
        )

        validation_loss = previous_stats.get(
            "validation_loss"
        )

        best_validation_loss = previous_stats.get(
            "best_validation_loss"
        )
```

`training_stats` is the small dictionary of numbers that the previous run stored in the checkpoint. Each counter is read with `.get(key, default)`, so an older checkpoint that lacks a key still loads: missing numeric counters fall back to zero, and the three loss values fall back to `None` (`.get` with one argument returns `None` when the key is absent).

How the start epoch is chosen: `start_epoch` becomes the checkpoint's `epochs_completed`. With today's checkpoint that is `21`. The loop further down begins at `start_epoch + 1`.

Restoring `best_validation_loss` means the "is this the best so far?" comparison continues across runs instead of starting fresh each time.

```python

        print(
            f"Resuming from epoch {start_epoch}, "
            f"step {global_step:,}, "
            f"tokens_seen {tokens_seen:,}"
        )

    print(f"Device: {device}")
```

Progress messages. Inside an f-string, `{global_step:,}` formats a number with thousands separators, so `5418` prints as `5,418`. The first `print` is inside the `if` (it only appears when resuming); the second is back at the function's indentation and always runs.

**Nothing left to do: the early return**

```python

    # Nothing left to train
    if start_epoch >= epochs:
        print(
            f"Training already completed "
            f"{start_epoch}/{epochs} epochs."
        )

        return {
            "epochs_completed": start_epoch,
            "global_step": global_step,
            "tokens_seen": tokens_seen,
            "training_seconds": previous_training_seconds,
            "final_loss": final_loss,
            "validation_loss": validation_loss,
            "best_validation_loss": best_validation_loss,
            "learning_rate": learning_rate,
        }
```

Because `epochs` is a total target, a checkpoint that already reached it leaves nothing to do. That is the situation today: the checkpoint says `epochs_completed` = `21` and `training.json` says `"epochs": 21`. The function prints `Training already completed 21/21 epochs.` and returns the restored numbers without running a single step and without writing any checkpoint. To train further you raise `epochs` in `training.json` (to `30`, say); the next run then performs epochs 22 to 30.

The returned dictionary has the same eight keys as the one returned after real training, so the caller does not need to know which path was taken. `learning_rate` here is the value passed to this call, not one read from the checkpoint.

**Timer and checkpoint policy**

```python

    started_at = time.perf_counter()

    checkpoint_every_epochs = training_config.get(
        "checkpoint_every_epochs",
        1,
    )

    keep_last_checkpoints = training_config.get(
        "keep_last_checkpoints",
        3,
    )

    last_saved_epoch = start_epoch
```

`time.perf_counter()` returns a high-resolution clock reading in seconds. The absolute value means nothing; subtracting two readings gives elapsed time.

`checkpoint_every_epochs` is the **cadence**: save after every N-th epoch. `keep_last_checkpoints` is the **retention**: how many per-epoch history files to keep. Both come from `training.json` with defaults `1` and `3`.

`last_saved_epoch` remembers the last epoch for which a checkpoint was written. It starts at `start_epoch` because, when resuming, that epoch is already on disk. It is used at the very end to decide whether one more save is needed.

**The two loops**

```python

    # --------------------------------------------------
    # Training
    # --------------------------------------------------

    for epoch in range(
        start_epoch + 1,
        epochs + 1,
    ):
        total_loss = 0.0
        steps_this_epoch = 0

        for x, y in make_training_examples(
            path=train_path,
            context_length=config.context_length,
        ):
```

The outer loop runs once per epoch. `range(a, b)` produces `a, a+1, …, b−1`, so `range(start_epoch + 1, epochs + 1)` gives epoch numbers that start at 1 for a fresh run and end at `epochs` inclusive. Resuming from 21 with a target of 30 gives 22, 23, …, 30.

`total_loss` and `steps_this_epoch` are reset at the start of each epoch; they exist only to compute that epoch's average loss.

The inner loop runs once per example. `make_training_examples` (chapter 5, `src/dataset/loader.py`) is a generator: it reads `train.jsonl` one document at a time, cuts each document's token ids into consecutive windows of at most `context_length` + 1 tokens, and for each window yields `x` (all tokens but the last) and `y` (all tokens but the first), both as 1-D tensors of whole numbers. Calling it again at the start of every epoch re-opens the file and yields the same examples in the same order; nothing is shuffled and the whole file is never held in memory.

`for x, y in ...` unpacks each yielded pair into two variables.

**Adding the batch dimension**

```python
            x = x.unsqueeze(0).to(device)
            y = y.unsqueeze(0).to(device)
```

**What Python/PyTorch does** — `x` arrives with shape `[T]`, where `T` is the number of tokens in this example (128 for full windows, fewer for the last window of a document). `unsqueeze(0)` inserts a new dimension of size 1 at position 0, giving shape `[1, T]`. No data is copied or changed; the same numbers are simply viewed as "one row of `T` items". `.to(device)` then copies the tensor to the device the model is on and returns the copy.

A real check with a made-up 5-token example:

```python
x1 = torch.tensor([5, 6, 7, 8, 9])
print(x1.shape, x1.unsqueeze(0).shape)
# torch.Size([5]) torch.Size([1, 5])
```

**What it means in the LLM/pipeline** — The model expects input of shape `[B, T]`: `B` sequences, each `T` tokens long (chapter 7). `B` is the **batch size**, the number of examples processed together in one step. This trainer never groups examples, so it wraps each single example as a batch of one: **the batch size is 1**. Each step's gradient therefore comes from one window of text only.

**Clearing old gradients, then the forward pass**

```python

            optimizer.zero_grad()

            logits = model(x)
```

`optimizer.zero_grad()` is explained together with `backward()` below; for now, it wipes the gradients left over from the previous step.

**What Python/PyTorch does** — `model(x)` calls `TinyLLM.forward` (chapter 7). The input has shape `[1, T]`; the result has shape `[1, T, 300]`. A real check: an input of shape `[1, 128]` produced `torch.Size([1, 128, 300])`.

**What it means in the LLM/pipeline** — This is the **forward pass**: the model's prediction. `logits[0, i]` is a row of 300 raw scores, one per vocabulary token, expressing the model's opinion about which token follows position `i`. Thanks to the causal mask, the scores at position `i` depend only on tokens `0..i`, so one forward pass yields `T` independent next-token predictions — one for every position, not just the last. That is why `y` has the same length as `x`: there is one correct answer per position.

**Computing the loss**

```python

            loss = loss_function(
                logits.reshape(
                    -1,
                    config.vocab_size,
                ),
                y.reshape(-1),
            )
```

**What Python/PyTorch does** — `nn.CrossEntropyLoss` wants its inputs in a specific layout: a 2-D tensor of scores with one row per prediction, `[N, number_of_classes]`, and a 1-D tensor of `N` correct class numbers. The two `reshape` calls rearrange the tensors into that layout without changing any value:

| Tensor | Before | Call | After |
|---|---|---|---|
| `logits` | `[1, T, 300]` | `reshape(-1, config.vocab_size)` | `[T, 300]` |
| `y` | `[1, T]` | `reshape(-1)` | `[T]` |

In `reshape`, `-1` means "work this dimension out from the total number of elements". The batch dimension of size 1 simply disappears. Checked with the 5-token example: logits `[1, 5, 300]` became `[5, 300]` and targets became `[5]`.

After the reshape, row `i` of the logits and element `i` of the targets belong together: 300 scores for position `i`, and the id of the token that really came next.

**What it means in the LLM/pipeline** — **Cross-entropy** is the measurement of "how wrong". For one position it works in three moves:

1. **Softmax.** Turn the 300 raw scores into 300 probabilities that are all positive and add up to 1: raise *e* to each score, then divide each result by the sum of all of them. Higher score, higher probability.
2. **Pick.** Look up the probability the model gave to the token that actually came next. Ignore the other 299.
3. **Negative log.** The loss for this position is `−ln(that probability)`.

The negative logarithm turns "probability of the right answer" into a penalty with the right behaviour:

| Probability given to the correct token | Loss `−ln(p)` |
|---|---|
| `1.0` (certain and right) | `0` |
| `0.5` | `0.69` |
| `0.1` | `2.30` |
| `0.01` | `4.61` |
| close to `0` (confidently wrong) | very large |

Finally the function takes the **mean** of the per-position losses, so the result is one number: the average penalty per predicted token in this example. Averaging is the default behaviour of `nn.CrossEntropyLoss()` when created with no arguments, as it is here.

A hand-computed example with a vocabulary of only 4 tokens and 3 positions:

| Position | Logits | Correct token | Softmax probabilities | Probability of correct | `−ln` |
|---|---|---|---|---|---|
| 0 | `[2, 1, 0, −1]` | `0` | `[0.6439, 0.2369, 0.0871, 0.0321]` | `0.6439` | `0.4402` |
| 1 | `[0, 0, 0, 0]` | `2` | `[0.25, 0.25, 0.25, 0.25]` | `0.25` | `1.3863` |
| 2 | `[0, 3, 0, 0]` | `3` | `[0.0433, 0.8700, 0.0433, 0.0433]` | `0.0433` | `3.1392` |

Position 0 by hand: *e*² = 7.389, *e*¹ = 2.718, *e*⁰ = 1, *e*⁻¹ = 0.368; their sum is 11.475; 7.389 / 11.475 = 0.6439; −ln(0.6439) = 0.4402. Position 1 has no preference at all, so each token gets 1/4 and the loss is ln(4) = 1.3863. Position 2 is confident about token `1` but the answer was token `3`, so it is punished hardest.

Mean: (0.4402 + 1.3863 + 3.1392) / 3 = **1.6552**.

The same numbers given to the real PyTorch function:

```python
logits = torch.tensor([[2.0, 1.0, 0.0, -1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 3.0, 0.0, 0.0]])
targets = torch.tensor([0, 2, 3])
print(nn.CrossEntropyLoss()(logits, targets).item())
# 1.6552300453186035
```

They agree.

**What a loss of ln(300) ≈ 5.70 means.** Position 1 in the table shows the general rule: a model with no preference among `V` tokens gives each a probability of 1/`V`, and its loss is `−ln(1/V) = ln(V)`. For this project's 300-token vocabulary that is ln(300) = **5.70**. This is the loss of pure guessing, and it is the reference point for reading every loss this trainer prints:

- **About 5.7** — the model knows nothing. A freshly created `TinyLLM` scored on random tokens gave 5.83, 5.87 and 5.88 in three trials; slightly above 5.70 because random weights produce slightly uneven scores rather than perfectly equal ones.
- **Below 5.7** — the model has learned something about which tokens follow which.
- **Well above 5.7** — the model is confidently wrong, usually a sign that the learning rate is too high.

The checkpoint that exists today recorded `final_loss` = `2.1077` after 21 epochs.

`loss` itself is a tensor holding a single number (shape `[]`), and it remembers every operation that produced it, all the way back to the parameters. The next line depends on that memory.

**Backward pass and parameter update**

```python

            loss.backward()

            optimizer.step()
```

Together with `optimizer.zero_grad()` three lines earlier, these are the heart of training.

A **gradient** answers this question for a single parameter: "if I increased this number by a tiny amount and kept everything else fixed, how much would the loss change, and in which direction?" A positive gradient means increasing the parameter raises the loss, so the parameter should go down. A negative gradient means the opposite. A large gradient means the loss is sensitive to this parameter; a gradient near zero means the parameter barely mattered for this example. Every parameter tensor has a companion tensor of the same shape, `.grad`, which holds one gradient per number.

**`loss.backward()`**

**What Python/PyTorch does** — While the forward pass ran, PyTorch quietly recorded every arithmetic operation in a graph. `backward()` walks that graph from the loss back to the parameters, applying the chain rule of calculus at each operation, and writes the result into the `.grad` of every parameter. This procedure is **backpropagation**. A real check on a fresh model: `model.lm_head.weight.grad` was `None` before the call and a tensor of shape `[300, 128]` after it, the same shape as the weight itself.

**What it means in the LLM/pipeline** — After this line the program knows, for all 884,480 parameters at once, which direction would have made the predictions on this example a little less wrong. Nothing has changed yet. `backward()` only fills in gradients.

**`optimizer.step()`**

**What Python/PyTorch does** — The optimizer visits every parameter it was given, reads its `.grad`, updates its two running averages, and changes the parameter's values in place according to the AdamW rule described earlier.

**What it means in the LLM/pipeline** — This is the moment the model learns. In the same check, after one `step()` every one of the 38,400 numbers in `lm_head.weight` had changed, and the largest change was `0.00030026` — the learning rate `0.0003` plus a sliver of weight decay. That is what "a nudge" means in practice: on each step each parameter moves by about the learning rate.

**`optimizer.zero_grad()`**

**What Python/PyTorch does** — Clears the `.grad` of every parameter.

**What it means in the LLM/pipeline** — `backward()` does not overwrite gradients; it *adds* to whatever is already there. Without clearing, step 2 would use the gradients of example 1 plus example 2, step 3 the sum of three examples, and so on. Clearing at the start of each step ensures each update is based on the current example only.

So the order inside one step is fixed: clear old gradients → forward pass → loss → backward pass → update.

Repeating that cycle on the same made-up 5-token example five times gave these losses:

```
[5.3527, 4.7081, 4.1008, 3.5429, 3.041]
```

Each step made the model a little less wrong on that example. That falling sequence is training.

**Bookkeeping for the step**

```python

            total_loss += loss.item()

            steps_this_epoch += 1
            global_step += 1

            # Number of next-token targets processed.
            tokens_seen += y.numel()
```

`loss.item()` pulls the single number out of the loss tensor as an ordinary Python `float`. This matters for two reasons: it brings the value from the GPU to normal memory, and it drops the recorded graph of operations, so the running total does not keep every past step's graph alive.

How each counter is incremented, exactly:

| Counter | Increment | Reset? |
|---|---|---|
| `total_loss` | plus this step's loss | to `0.0` at the start of every epoch |
| `steps_this_epoch` | plus 1 | to `0` at the start of every epoch |
| `global_step` | plus 1 | never; carried through resume |
| `tokens_seen` | plus `y.numel()` | never; carried through resume |

`y.numel()` is "number of elements": for `y` of shape `[1, T]` it is `T`. It counts the predictions that were scored in this step, which is why the comment says "next-token targets". With today's data the three steps of an epoch add 128, 128 and 2.

**End of an epoch**

```python

        if steps_this_epoch == 0:
            raise ValueError(
                "No training examples were produced"
            )

        final_loss = (
            total_loss
            / steps_this_epoch
        )

        print(
            f"Epoch {epoch:03d} "
            f"| loss={final_loss:.4f} "
            f"| steps={global_step:,} "
            f"| tokens_seen={tokens_seen:,}"
        )
```

These lines are indented one level less than the previous block: they run after the inner loop has finished, once per epoch.

If the training file is empty, or every document in it has fewer than 2 tokens, the inner loop never runs. The check stops with a clear error instead of dividing by zero on the next line.

`final_loss` is the **per-epoch average loss**: the sum of the step losses divided by the number of steps. Two details about what this number is:

- Each step's loss was measured *before* that step's update, and the model kept changing during the epoch. So it is the average over a moving model, not the loss of the model as it stands at the end of the epoch. For the real checkpoint, the stored `final_loss` is `2.1077`, while evaluating the finished model on the same training file (chapter 9) gives `2.0433`.
- Every step counts equally, whatever its length. With today's data, the 2-token example weighs as much in the average as each 128-token example.

The variable is called `final_loss` because the value from the last epoch is what ends up in the returned statistics and in the checkpoint.

The `print` produces one line per epoch. `{epoch:03d}` pads the epoch number to three digits with zeros; `{final_loss:.4f}` shows four decimal places. A real line from a throw-away run on made-up tokens:

```
Epoch 001 | loss=6.0892 | steps=3 | tokens_seen=258
```

**Is it time to checkpoint?**

```python

        # --------------------------------------------------
        # Checkpoint
        # --------------------------------------------------

        if (
            checkpoint_every_epochs > 0
            and epoch % checkpoint_every_epochs == 0
        ):
```

`%` is the remainder operator. `epoch % checkpoint_every_epochs == 0` is true when the epoch number is an exact multiple of the cadence: with `1`, every epoch; with `5`, epochs 5, 10, 15, …. The first condition, `> 0`, lets you set the cadence to `0` to switch periodic checkpoints off, and also protects the `%` from dividing by zero (`and` does not evaluate its right side when the left side is false).

Everything from here to `last_saved_epoch = epoch` is inside this `if`. In particular, validation only runs on epochs that are checkpointed.

**Validation and the "best" decision**

```python
            # --------------------------------------------------
            # Validation decides the best checkpoint
            # --------------------------------------------------

            is_best = False

            if (
                validation_path is not None
                and validation_path.is_file()
            ):
                result = evaluate(
                    model=model,
                    config=config,
                    dataset_path=validation_path,
                    device=device,
                )

                model.train()
```

**Validation** means measuring the loss on text the model is *not* being trained on. Training loss tells you how well the model fits the examples it keeps seeing; validation loss tells you whether what it learned carries over to new text. When training loss keeps falling but validation loss starts rising, the model is memorising rather than generalising. That is why the "best" checkpoint is chosen by validation loss and not by training loss.

`is_best` starts as `False` and stays `False` unless the code below proves otherwise.

The `if` requires that a validation path was given and that the file exists. `evaluate` (chapter 9) then runs the model over that file without updating any parameter and returns a dictionary with the keys `available`, `loss`, `perplexity` and `steps`.

`evaluate` switches the model into evaluation mode with `model.eval()` and does not switch it back. The `model.train()` immediately after the call restores training mode so the next epoch trains normally.

```python

                if result["available"]:
                    validation_loss = result["loss"]

                    is_best = (
                        best_validation_loss is None
                        or validation_loss
                        < best_validation_loss
                    )

                    if is_best:
                        best_validation_loss = (
                            validation_loss
                        )

                    print(
                        f"Epoch {epoch:03d} "
                        f"| validation_loss="
                        f"{validation_loss:.4f}"
                        f"{' (best)' if is_best else ''}"
                    )
```

`result["available"]` is `True` only when the validation file produced at least one example. In that case:

- `validation_loss` takes the new measurement.
- `is_best` becomes `True` if there was no earlier best (`best_validation_loss is None`) or if the new loss is strictly lower than the earlier best. `or` evaluates its right side only when the left side is false, so `None` is never compared with a number.
- If it is the best, `best_validation_loss` is updated.
- A line is printed. `{' (best)' if is_best else ''}` is a conditional expression inside an f-string: it inserts ` (best)` or nothing.

A real line from a throw-away run that had a small made-up validation file:

```
Epoch 008 | validation_loss=4.6332 (best)
```

**What happens today, with an empty validation file.** `storage/training/tokenized/validation.jsonl` exists but is 0 bytes. Follow the code:

1. `validation_path is not None` → true. `validation_path.is_file()` → true (an empty file is still a file).
2. `evaluate` runs, finds no examples, and returns `{'available': False, 'loss': None, 'perplexity': None, 'steps': 0}`.
3. `model.train()` runs.
4. `if result["available"]` is false, so the whole block above is skipped. Nothing is printed.
5. `validation_loss` and `best_validation_loss` remain `None`, and `is_best` remains `False`.

So today no validation line appears, no best checkpoint is ever written, and both validation numbers in the statistics are `None`. This was confirmed by a throw-away run against an empty validation file: after five epochs the checkpoint folder contained the latest file and history files but no `best_` file.

One more case: if the validation file had examples in an earlier run but yields none now, `validation_loss` is not cleared. It keeps the older value restored from the checkpoint and that older value is written into the new statistics.

**Saving the checkpoint**

```python

            save_checkpoint(
                path=checkpoint_path,
                model=model,
                optimizer=optimizer,
                model_config=config,
                training_config=training_config,
                training_stats={
                    "epochs_completed": epoch,
                    "global_step": global_step,
                    "tokens_seen": tokens_seen,
                    "training_seconds": (
                        previous_training_seconds
                        + time.perf_counter()
                        - started_at
                    ),
                    "final_loss": final_loss,
                    "validation_loss": validation_loss,
                    "best_validation_loss": best_validation_loss,
                    "learning_rate": learning_rate,
                },
                keep_last=keep_last_checkpoints,
                is_best=is_best,
            )

            last_saved_epoch = epoch
```

A **checkpoint** is a file containing everything needed to use the model or continue training it. `save_checkpoint` (8.4) writes it. The statistics dictionary is built on the spot:

| Key | Value at this moment |
|---|---|
| `epochs_completed` | the epoch that just finished |
| `global_step` | total steps so far |
| `tokens_seen` | total targets so far |
| `training_seconds` | time from earlier runs, plus now minus the start of this run. It includes the time spent on validation and on writing earlier checkpoints. |
| `final_loss` | this epoch's average training loss |
| `validation_loss` | latest validation loss, or `None` |
| `best_validation_loss` | lowest validation loss so far, or `None` |
| `learning_rate` | the value passed to `train` |

These are exactly the keys the resume block reads back. `keep_last` and `is_best` tell `save_checkpoint` how many history files to keep and whether to also write the best file. `last_saved_epoch = epoch` records that this epoch is on disk.

Saving after every epoch means that if training is interrupted — the process is killed, the laptop sleeps, the power fails — at most one epoch of work is lost. The next run resumes from the last completed epoch.

**After the last epoch: final statistics**

```python

    # --------------------------------------------------
    # Final stats
    # --------------------------------------------------

    training_seconds = (
        previous_training_seconds
        + time.perf_counter()
        - started_at
    )

    final_stats = {
        "epochs_completed": epochs,
        "global_step": global_step,
        "tokens_seen": tokens_seen,
        "training_seconds": training_seconds,
        "final_loss": final_loss,
        "validation_loss": validation_loss,
        "best_validation_loss": best_validation_loss,
        "learning_rate": learning_rate,
    }
```

Back at the function's own indentation, so this runs once, after the outer loop ends. The dictionary has the same eight keys as the per-epoch one. `epochs_completed` is `epochs` because the loop has now run through its last value.

**The final-save rule and the return value**

```python

    # Save the final state if the last epoch
    # was not already checkpointed.
    if last_saved_epoch != epochs:
        save_checkpoint(
            path=checkpoint_path,
            model=model,
            optimizer=optimizer,
            model_config=config,
            training_config=training_config,
            training_stats=final_stats,
            keep_last=keep_last_checkpoints,
        )

    return final_stats
```

The **final-save rule**: the finished model must always be on disk. If the last epoch was a checkpoint epoch, it already is, `last_saved_epoch == epochs`, and nothing more is written. If it was not — the cadence is `0`, or `epochs` is not a multiple of the cadence (for example 10 epochs with a cadence of 3: saved at 3, 6, 9, but not 10) — one more checkpoint is written here.

This final save does not pass `is_best`, so it uses the default `False`, and it does not run validation. A final-only save therefore never updates the best file.

With today's settings (`checkpoint_every_epochs` = `1`) the last epoch is always saved inside the loop and this block is skipped.

The function returns `final_stats`. For the run that produced today's checkpoint the statistics were:

| Key | Value |
|---|---|
| `epochs_completed` | `21` |
| `global_step` | `63` |
| `tokens_seen` | `5418` |
| `training_seconds` | `10.46` (rounded) |
| `final_loss` | `2.1077` (rounded) |
| `learning_rate` | `0.0003` |

That stored dictionary has six keys, not eight: the checkpoint on disk was written by an earlier version of this file, before the two validation keys were added. The resume block copes with this because it uses `.get`, and the next checkpoint written will contain all eight.

### 8.4 Checkpoints

#### `src/training/checkpoint.py`

**Why this file exists** — The trained parameters live only in memory while the training process runs. This file turns them into files on disk and back, so that training can be resumed and so that evaluation, inference and serving have something to load.

**What enters / what leaves** — `save_checkpoint` receives a path, the model, the optimizer, the model config, the training config, the statistics, a retention count and a best flag; it writes up to three files and deletes old history files; it returns nothing. `load_checkpoint` receives a path and a device and returns the checkpoint dictionary, or `None` when the file does not exist. Three small helpers build the best file's path, copy a file safely, and prune history.

**How it connects** — `train` (8.3) calls `save_checkpoint`. `scripts/train.py` calls `load_checkpoint` to obtain the dictionary it passes to `train` as `resume_checkpoint`. The files written here are what chapters 9, 10 and 11 read.

The three kinds of file, all in `artifacts/checkpoints/`:

| File | Name | Written when | Purpose |
|---|---|---|---|
| **latest** | `tiny_model.pt` | every save | The current state. Resume, evaluation and inference load this one. |
| **best** | `best_tiny_model.pt` | only when a save is flagged `is_best` | The state with the lowest validation loss seen so far. |
| **history** | `checkpoint_epoch_000021_step_000000063.pt` | every save, when `keep_last > 0` | Snapshots of individual epochs. Only the newest `keep_last` are kept. |

**The code, section by section**

**Imports**

```python
import shutil
from pathlib import Path

import torch

from src.model.config import ModelConfig
from src.model.model import TinyLLM
```

`shutil` is the standard-library module for file operations such as copying; it is used for `shutil.copyfile`. `torch` provides `torch.save` and `torch.load`. `ModelConfig` and `TinyLLM` are needed for type hints and for reading the config's fields.

**`save_checkpoint`: signature and folder**

```python
def save_checkpoint(
    path: Path,
    model: TinyLLM,
    optimizer: torch.optim.Optimizer,
    model_config: ModelConfig,
    training_config: dict,
    training_stats: dict,
    keep_last: int = 3,
    is_best: bool = False,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
```

`path` is where the latest file goes. `torch.optim.Optimizer` is the base class of all PyTorch optimizers, so the hint accepts AdamW or any other. `-> None` means the function returns nothing.

`path.parent` is the folder containing the file. `mkdir(parents=True, exist_ok=True)` creates it together with any missing parent folders and does nothing if it already exists.

**What goes into a checkpoint**

```python

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),

        "config": {
            "vocab_size": model_config.vocab_size,
            "context_length": model_config.context_length,
            "d_model": model_config.d_model,
            "num_heads": model_config.num_heads,
            "num_layers": model_config.num_layers,
            "dropout": model_config.dropout,
        },

        "training_config": training_config,
        "training_stats": training_stats,
```

A checkpoint is an ordinary Python dictionary with six keys. The first five:

**`model_state_dict`**

**What Python/PyTorch does** — `model.state_dict()` returns an ordered dictionary that maps each parameter's name to its tensor of values. The names follow the attribute names used when the model was built in chapter 7. For this model there are 53 entries. A few of them, read from the real checkpoint:

| Name | Shape |
|---|---|
| `embeddings.token_embedding.weight` | `[300, 128]` |
| `embeddings.position_embedding.weight` | `[128, 128]` |
| `blocks.0.attention.q_proj.weight` | `[128, 128]` |
| `blocks.0.feed_forward.net.0.weight` | `[512, 128]` |
| `final_norm.weight` | `[128]` |
| `lm_head.weight` | `[300, 128]` |

**What it means in the LLM/pipeline** — This *is* the trained model. The Python class describes the structure; the state dict holds the numbers. A state dict contains no code, so loading always follows the same recipe: build an empty model of the same shape, then copy the numbers in with `load_state_dict`.

**`optimizer_state_dict`** — the optimizer's memory. It has two parts: `state`, holding for each of the 53 parameter tensors a step count and AdamW's two running averages (`exp_avg` for momentum and `exp_avg_sq` for squared gradients, each the same shape as the parameter), and `param_groups`, holding the settings (`lr`, `betas`, `eps`, `weight_decay` and so on). It is needed only for resuming; inference ignores it.

This also explains the file size. 884,480 parameters stored as 4-byte numbers take about 3.5 MB. The optimizer keeps two more tensors of the same size for every parameter, so the total is roughly three times that. The real `tiny_model.pt` is 10,678,515 bytes.

**`config`** — the six architecture settings, copied field by field out of the `ModelConfig` into a plain dictionary. Whoever loads the checkpoint later must build a model of exactly the same shape before the weights will fit; storing the settings inside the file makes the file self-describing. `scripts/evaluate.py` does precisely that with `ModelConfig(**checkpoint["config"])`. The real file contains:

```python
{'vocab_size': 300, 'context_length': 128, 'd_model': 128, 'num_heads': 4, 'num_layers': 4, 'dropout': 0.0}
```

**`training_config`** — the dictionary from `training.json`, stored whole as a record of the settings in force when this checkpoint was written.

**`training_stats`** — the counters and losses built in `train`. The resume block reads `epochs_completed`, `global_step`, `tokens_seen`, `training_seconds`, `final_loss`, `validation_loss` and `best_validation_loss` from here.

```python

        "model_stats": {
            "total_parameters": sum(
                parameter.numel()
                for parameter in model.parameters()
            ),
            "trainable_parameters": sum(
                parameter.numel()
                for parameter in model.parameters()
                if parameter.requires_grad
            ),
        },
    }
```

**`model_stats`** — the sixth key: two counts. `parameter.numel()` is the number of individual numbers in one parameter tensor; the generator expression (primer in 1) feeds those counts to `sum`. The second sum adds the filter `if parameter.requires_grad`, which is `True` for parameters that training is allowed to change. Nothing in this model is frozen, so both are the same. In the real checkpoint:

```python
{'total_parameters': 884480, 'trainable_parameters': 884480}
```

**Writing the latest file safely**

```python

    # --------------------------------------------------
    # Latest checkpoint
    # --------------------------------------------------

    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    torch.save(
        checkpoint,
        temporary_path,
    )

    temporary_path.replace(
        path
    )
```

**What Python/PyTorch does** — `path.suffix` is the file extension, `.pt`. `path.with_suffix(".pt.tmp")` returns the same path with the extension swapped, so `tiny_model.pt` gives `tiny_model.pt.tmp`. `torch.save(obj, file)` serialises the dictionary — tensors as raw bytes, everything else through Python's pickling mechanism — into one file. `Path.replace(target)` renames the temporary file to the real name, overwriting whatever was there.

**What it means in the LLM/pipeline** — This is the write-then-replace pattern introduced in 4.1/4.2, and here it protects the most valuable file in the project. Writing ten megabytes takes a moment. If the process died half-way through writing directly to `tiny_model.pt`, the file would be truncated and unreadable, the previous good checkpoint would already be gone, and every epoch of training would be lost. Writing to a different name first means the real file is untouched until the new one is complete. The rename is a single file-system operation that either happens entirely or not at all (**atomic**), so at every instant `tiny_model.pt` is either the complete old checkpoint or the complete new one.

**The best file**

```python

    # --------------------------------------------------
    # Best checkpoint
    # --------------------------------------------------

    if is_best:
        copy_checkpoint(
            path,
            best_checkpoint_path(path),
        )
```

When the trainer flagged this save as the best so far, the latest file that was just written is copied to the best file's name, replacing the previous best. Since `is_best` can only be `True` after a real validation measurement, and the validation file is empty today, this branch has never run in the current setup and no `best_tiny_model.pt` exists.

**History files**

```python

    # --------------------------------------------------
    # Historical checkpoints
    # --------------------------------------------------

    if keep_last > 0:
        epoch = training_stats["epochs_completed"]
        global_step = training_stats["global_step"]

        copy_checkpoint(
            path,
            path.parent
            / (
                f"checkpoint_epoch_{epoch:06d}"
                f"_step_{global_step:09d}.pt"
            ),
        )

    prune_history(
        path.parent,
        keep_last,
    )
```

If retention is switched on, the latest file is copied once more under a name that records when it was taken. `{epoch:06d}` pads the epoch to six digits and `{global_step:09d}` pads the step to nine, so epoch 21 at step 63 becomes:

```
checkpoint_epoch_000021_step_000000063.pt
```

The zero-padding is not decoration; `prune_history` relies on it, as shown below.

`prune_history` is called on every save, outside the `if`. With `keep_last` = `0` no new history file is written and the prune then removes every history file that exists; this was confirmed in a throw-away folder.

**`best_checkpoint_path`**

```python


def best_checkpoint_path(path: Path) -> Path:
    return path.with_name(
        "best_" + path.name
    )
```

`path.name` is the file name without its folder, `tiny_model.pt`. `with_name` returns the same path with the file name replaced. The result is `best_tiny_model.pt` in the same folder.

**`copy_checkpoint`**

```python


def copy_checkpoint(
    source: Path,
    destination: Path,
) -> None:
    temporary_path = destination.with_suffix(
        destination.suffix + ".tmp"
    )

    shutil.copyfile(
        source,
        temporary_path,
    )

    temporary_path.replace(
        destination
    )
```

The same write-then-replace pattern applied to a copy: `shutil.copyfile` copies the bytes of `source` to a temporary name, and `replace` renames it into place. A best or history file is therefore never seen half-copied. Because it is a byte-for-byte copy of the latest file, a history file contains the same six keys, including the optimizer state, and can be loaded in exactly the same way.

**`prune_history`**

```python


def prune_history(
    checkpoints_dir: Path,
    keep_last: int,
) -> None:
    """
    Keep only the newest historical checkpoints.

    Names are zero-padded, so sorting by name
    is sorting by epoch and step.
    """

    history = sorted(
        checkpoints_dir.glob(
            "checkpoint_epoch_*_step_*.pt"
        )
    )
```

The triple-quoted text is a docstring: documentation attached to the function, not executed.

`glob(pattern)` yields every path in the folder whose name matches the pattern, where `*` stands for any run of characters. The pattern matches history files only; `tiny_model.pt` and `best_tiny_model.pt` do not match and can never be deleted here. `sorted` puts the paths in alphabetical order.

This is where zero-padding matters. Text sorts character by character, so without padding `epoch_10` would sort before `epoch_9`. With fixed-width numbers, alphabetical order and numerical order are the same, and the list runs from oldest to newest.

```python

    excess = max(
        len(history) - max(keep_last, 0),
        0,
    )

    for old_path in history[:excess]:
        old_path.unlink()
```

`excess` is how many files are over the limit. The inner `max(keep_last, 0)` treats a negative setting as zero; the outer `max(..., 0)` stops the result going negative when there are fewer files than the limit. `history[:excess]` is the first `excess` entries of the sorted list — the oldest ones — and `unlink()` deletes a file.

Example with `keep_last` = `3`: after the save at epoch 5 there are five history files, `excess` = 2, and epochs 1 and 2 are deleted. A throw-away five-epoch run left exactly this:

```
checkpoint_epoch_000003_step_000000009.pt
checkpoint_epoch_000004_step_000000012.pt
checkpoint_epoch_000005_step_000000015.pt
tiny_model.pt
```

The real `artifacts/checkpoints/` folder currently looks different: it holds 21 history files, epochs 1 through 21, next to `tiny_model.pt`. They were written by an earlier version of this file that did not prune (the `training_config` stored in the checkpoint has no `keep_last_checkpoints` key). The pruning is not tied to a particular run: it looks at whatever history files are in the folder, so the next save made by the current code will reduce them to the newest three.

**`load_checkpoint`**

```python


def load_checkpoint(
    path: Path,
    device: torch.device,
) -> dict | None:
    if not path.is_file():
        return None

    return torch.load(
        path,
        map_location=device,
    )
```

**What Python/PyTorch does** — If there is no file, the function returns `None` instead of raising an error. Otherwise `torch.load` reads the file and rebuilds the dictionary that `torch.save` wrote, with the same six keys. Each saved tensor remembers which device it was on when saved. `map_location=device` tells PyTorch to place every loaded tensor on the given device instead.

**What it means in the LLM/pipeline** — Returning `None` is what makes the first-ever training run work with the same script as every later one: `None` is exactly the value `train` treats as "start from scratch". `map_location` is what makes a checkpoint portable: a file saved on an Apple GPU (`mps`) could not otherwise be opened on a machine that has only a CPU.

### 8.5 Recording each run

#### `src/training/run.py`

**Why this file exists** — A checkpoint tells you the state of the model. It does not tell you when it was trained, on what hardware, or with which settings each time. This file keeps a small, human-readable record per invocation of the training script, so that experiments can be compared later.

**What enters / what leaves** — `create_run` receives the runs folder, the device name, the checkpoint path, and the model and training config dictionaries; it creates `artifacts/runs/<run_id>/run.json` and returns the run id and the path of that file. `finish_run` receives that path plus the training and model statistics; it rewrites the same file with the results added. `utc_now` returns the current time as text.

**How it connects** — `scripts/train.py` calls `create_run` before training and `finish_run` after it. The admin part of the serving backend (chapter 11) lists the folders under `artifacts/runs/`.

**The code, section by section**

**Imports and the timestamp helper**

```python
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
```

`uuid` generates random unique identifiers. `datetime` and `timezone` are the standard date-and-time classes.

`datetime.now(timezone.utc)` is the current moment expressed in UTC, the time zone that does not depend on where the computer is. `.isoformat()` turns it into standard text such as `2026-10-05T08:25:50.004446+00:00`. `.replace("+00:00", "Z")` swaps the offset for the conventional short form `Z`, which means the same thing. The result, taken from the real run record: `2026-10-05T08:25:50.004446Z`.

**`create_run`: the run id and its folder**

```python


def create_run(
    runs_dir: Path,
    device: str,
    checkpoint_path: Path,
    model_config: dict,
    training_config: dict,
) -> tuple[str, Path]:

    run_id = (
        f"run_"
        f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_"
        f"{uuid.uuid4().hex[:8]}"
    )

    run_dir = runs_dir / run_id

    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )
```

The return type `tuple[str, Path]` means the function returns two values together.

The **run id** is built from three pieces:

| Piece | Code | Example |
|---|---|---|
| fixed prefix | `run_` | `run_` |
| UTC date and time | `{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}` | `20261005T082550Z` |
| 8 random hex characters | `uuid.uuid4().hex[:8]` | `3079d15f` |

Inside an f-string, the text after the colon is a format; for a date, `%Y%m%dT%H%M%SZ` means four-digit year, month, day, a literal `T`, hour, minute, second, a literal `Z`. `uuid.uuid4()` makes a random identifier, `.hex` is its 32 hexadecimal characters, and `[:8]` keeps the first eight. The real run on disk is `run_20261005T082550Z_3079d15f`.

The timestamp makes run folders sort in time order; the random part keeps two runs started in the same second apart.

`mkdir(..., exist_ok=False)` creates the run's folder and, unlike the checkpoint folder earlier, raises an error if it already exists. A run must never silently write into another run's folder.

**`create_run`: the starting record**

```python

    metadata = {
        "run_id": run_id,
        "status": "running",
        "started_at": utc_now(),

        "device": device,

        "checkpoint_path": (
            checkpoint_path.as_posix()
        ),

        "model_config": model_config,
        "training_config": training_config,
    }
```

What is recorded at the start:

| Key | Content |
|---|---|
| `run_id` | the id built above |
| `status` | the text `running` |
| `started_at` | UTC timestamp |
| `device` | `cuda`, `mps` or `cpu` |
| `checkpoint_path` | where this run writes its latest checkpoint. `as_posix()` gives the path as text with forward slashes. The script passes the full path, so the stored value is an absolute path on your machine. |
| `model_config` | the six architecture settings |
| `training_config` | the dictionary from `training.json` |

```python

    path = run_dir / "run.json"

    path.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return run_id, path
```

`json.dumps` turns the dictionary into JSON text. `indent=2` spreads it over several lines so it is easy to read; `ensure_ascii=False` writes non-English characters as themselves rather than as escape codes. `write_text` creates the file and writes the text in one call. The function returns the id and the file's path as a pair.

Writing the record *before* training starts means that a run which crashes still leaves evidence: a `run.json` whose status says `running` and which has no `finished_at`. Nothing in the code later changes such a record.

**`finish_run`**

```python


def finish_run(
    run_path: Path,
    training_stats: dict,
    model_stats: dict,
) -> None:

    metadata = json.loads(
        run_path.read_text(
            encoding="utf-8"
        )
    )

    metadata["status"] = "completed"
    metadata["finished_at"] = utc_now()
    metadata["training_stats"] = training_stats
    metadata["model_stats"] = model_stats
```

Reads the starting record back from disk (`json.loads` parses JSON text into a dictionary), changes `status` to `completed`, and adds three keys:

| Key | Content |
|---|---|
| `finished_at` | UTC timestamp |
| `training_stats` | the dictionary returned by `train` |
| `model_stats` | total and trainable parameter counts |

```python

    temporary_path = run_path.with_suffix(
        ".json.tmp"
    )

    temporary_path.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(
        run_path
    )
```

Write-then-replace again: the updated record goes to `run.json.tmp`, which is then renamed over `run.json`. If the process is interrupted during the write, the original starting record survives intact.

The real record in `artifacts/runs/run_20261005T082550Z_3079d15f/run.json` holds these values (the checkpoint path is omitted here):

| Key | Value |
|---|---|
| `status` | `completed` |
| `started_at` | `2026-10-05T08:25:50.004446Z` |
| `finished_at` | `2026-10-05T08:26:06.937487Z` |
| `device` | `mps` |
| `training_stats.epochs_completed` | `21` |
| `training_stats.global_step` | `63` |
| `training_stats.tokens_seen` | `5418` |
| `training_stats.final_loss` | `2.107672611872355` |
| `model_stats.total_parameters` | `884480` |

### 8.6 The optimizer module

#### `src/training/optimizer.py`

This file exists and is empty: zero bytes, no code. Nothing imports it. The optimizer used in training is created directly inside `train` in `src/training/trainer.py` with `torch.optim.AdamW(...)`, as described in 8.3.

### 8.7 The script that drives training

Training is started with `python -m scripts.train`, which runs `scripts/train.py` (its code is covered in chapter 12). It wires the pieces of this chapter together in this order:

1. **Config** — `load_training_config()` reads `configs/training.json`.
2. **Model** — `ModelConfig()` is created with its default values and a new `TinyLLM` with random weights is built from it. `get_device()` picks the device.
3. **Run record** — `create_run(...)` writes the starting `run.json` and the run id is printed.
4. **Resume** — if the config's `resume` is true (or absent), `load_checkpoint(CHECKPOINT_PATH, device)` returns the latest checkpoint or `None`.
5. **Train** — `train(...)` is called with `epochs` and `learning_rate` from the config, the tokenized `train.jsonl` and `validation.jsonl` paths, and the resume checkpoint.
6. **Finish** — the parameter counts are computed, `finish_run(...)` completes `run.json`, and a short summary is printed.

Two consequences of this order: the run record is created before the resume check, so starting the script when training is already complete still produces a new run folder with status `completed`; and the model is always built from `ModelConfig()` defaults rather than from the checkpoint's stored `config`, so the two must describe the same shape for a resume to succeed.

#### What I should understand before moving on

- Training is one cycle repeated: forward pass → loss → `backward()` → `step()`, with `zero_grad()` first so each update uses only the current example's gradients.
- Cross-entropy at one position is `−ln` of the probability the model gave to the token that really came next; the loss is the mean over positions. Guessing uniformly among 300 tokens gives ln(300) ≈ 5.70.
- `backward()` only computes gradients; `optimizer.step()` is what changes the parameters. AdamW adds momentum, per-parameter step sizes and decoupled weight decay; this code sets only the learning rate and leaves the rest at PyTorch's defaults.
- In this trainer one step is one example (batch size 1), an epoch is one pass over `train.jsonl`, and `tokens_seen` is the cumulative count of scored targets. Today that is 3 steps and 258 targets per epoch.
- `epochs` is a total target. Resuming restores weights, optimizer state and counters, continues at `epochs_completed + 1`, and returns immediately when the target is already met.
- A checkpoint is a dictionary with six keys. The latest file is always written; a history copy is written per save and pruned to the newest `keep_last`; a best copy is written only when validation loss improves.
- With the validation file empty, as it is now, validation never produces a number, `is_best` is never true, and no best file is written.
- Checkpoints and the finished run record are written to a temporary name and then renamed, so an interruption cannot leave a half-written file in place of a good one.

#### Self-test

1. A brand-new `TinyLLM` reports a loss of about 5.8 on its first step. Without running anything, how do you know this is the expected value and not a bug?
2. Suppose you deleted the line `optimizer.zero_grad()`. What would each `optimizer.step()` then be acting on, and why is that wrong?
3. The tokenized training file holds one document of 259 tokens and `context_length` is 128. Explain why an epoch has 3 steps and adds 258, not 259, to `tokens_seen`.
4. `training.json` says `"epochs": 21` and the checkpoint says `epochs_completed` = `21`. You run the training script again. What happens to the model, to the checkpoint files, and what would you change to train nine more epochs?
5. At one position the model assigns probability 0.5 to the correct next token; at another it assigns 0.01. What is the loss at each, and what does the difference tell you about how cross-entropy treats confident mistakes?
6. Why does a checkpoint store the optimizer's state as well as the model's weights, and which later stages do not need it?
7. With `checkpoint_every_epochs` set to `4` and `epochs` set to `10`, at which epochs are checkpoints written, and which of them can be marked best?
8. Why is the checkpoint written to `tiny_model.pt.tmp` first rather than straight to `tiny_model.pt`?

<details><summary>Answers</summary>

1. An untrained model has no real preference among the 300 tokens, so it gives each roughly probability 1/300. The cross-entropy of that is `−ln(1/300) = ln(300) ≈ 5.70`. Random weights make the scores slightly uneven, which pushes the measured value a little above 5.70.
2. `backward()` adds new gradients to the ones already stored. Without clearing, each step would act on the sum of the gradients of every example seen so far, not on the current example's gradient, so the updates would be driven by stale information and grow in size as the sums accumulate.
3. The 259 tokens give 258 next-token targets, because the last token has no successor to predict. Windows of at most 128 targets cover them as 128 + 128 + 2, which is three examples. One example is one step, and `tokens_seen` grows by the number of targets in each.
4. The resume block restores the counters, sees `start_epoch >= epochs`, prints "Training already completed 21/21 epochs." and returns. No step is run and no checkpoint is written. (The script still creates a new run record.) To train nine more epochs, set `"epochs": 30`; the loop then runs epochs 22 to 30.
5. `−ln(0.5) ≈ 0.69` and `−ln(0.01) ≈ 4.61`. The penalty grows much faster than the probability shrinks: giving the truth almost no chance is punished far more heavily than being unsure, which pushes the model away from confident wrong predictions.
6. AdamW keeps two running averages per parameter and a step count. Restoring them lets training continue as if it had never stopped; without them the first steps after a resume would use freshly zeroed averages. Evaluation, inference and serving only run the model forward, so they need the weights and the config but not the optimizer state.
7. Inside the loop at epochs 4 and 8 (the multiples of 4). Epoch 10 is not a multiple, so the final-save rule writes one more checkpoint after the loop. Only the saves at 4 and 8 run validation and can be flagged best; the final save passes no `is_best`.
8. Writing takes time, and a process killed mid-write would leave a truncated, unreadable file where the last good checkpoint used to be. Writing under another name leaves the good file untouched until the new one is complete, and the rename that swaps them happens all at once.

</details>

## 9. Evaluation

| | |
|---|---|
| **INPUT** | A model with trained weights (loaded from `artifacts/checkpoints/tiny_model.pt`), its `ModelConfig`, a device, and a tokenized split file such as `storage/training/tokenized/train.jsonl`, `validation.jsonl` or `test.jsonl`. |
| **PROCESS** | Run the model over every example in the file exactly as training does, compute the cross-entropy loss for each, but compute no gradients and change no parameters. Average the losses and convert the average to perplexity. |
| **OUTPUT** | A dictionary: `available`, `loss`, `perplexity`, `steps`. Nothing is written to disk; the driving script prints the numbers. |
| **WHY IT EXISTS** | The loss printed during training is measured on a model that is changing and on text it is being fitted to. Evaluation measures a fixed model, and — when given text held back from training — is the only way to tell learning from memorising. |

### `src/evaluation/evaluator.py`

**Why this file exists** — It provides one function, `evaluate`, that answers "how good is this model at predicting the next token on this file?" without altering the model.

**What enters / what leaves** — Arguments: the model, its config, the path of a tokenized JSONL file, and the device the model is on. It reads that file once. It returns a dictionary and writes nothing.

**How it connects** — It is called from two places: by `train` in `src/training/trainer.py` at each checkpoint, on the validation file (8.3), and by `scripts/evaluate.py`, on all three splits. It reads examples through `make_training_examples` from `src/dataset/loader.py` (chapter 5) and calls the model from chapter 7.

**The code, section by section**

**Imports**

```python
from pathlib import Path

import math
import torch
from torch import nn

from src.dataset.loader import make_training_examples
from src.model.config import ModelConfig
from src.model.model import TinyLLM
```

`math` is the standard-library maths module, used for `math.exp`. `torch` is needed for the `no_grad` decorator and the `torch.device` type hint; `nn` for `nn.CrossEntropyLoss`. `make_training_examples` is the same example generator the trainer uses. `Path`, `ModelConfig` and `TinyLLM` appear in type hints, and `config` supplies `context_length` and `vocab_size`.

**The decorator and the signature**

```python


@torch.no_grad()
def evaluate(
    model: TinyLLM,
    config: ModelConfig,
    dataset_path: Path,
    device: torch.device,
) -> dict:
```

A line beginning with `@` directly above a function is a **decorator**: it wraps the function so that something extra happens around every call.

**What Python/PyTorch does** — `@torch.no_grad()` switches off PyTorch's recording of operations for the whole duration of each call to `evaluate`, and switches it back on when the function returns. Tensors produced inside do not remember how they were computed. A real check: the output of the model normally reports `requires_grad` = `True`; the same call made under `torch.no_grad()` reports `False`.

**What it means in the LLM/pipeline** — The recording exists only so that `backward()` can compute gradients. Evaluation never calls `backward()`, so recording would only cost memory and time. It is also a safety guarantee: with no gradients, nothing in this function can change the model's parameters.

The function does not move the model to the device; the caller must have done that. `device` is used only to move the input tensors to wherever the model already is.

**Evaluation mode and the accumulators**

```python
    model.eval()

    loss_function = nn.CrossEntropyLoss()

    total_loss = 0.0
    steps = 0
```

`model.eval()` is the counterpart of `model.train()` from 8.3: it sets the model's training flag to `False`, which turns dropout off so that the same input always gives the same output. (With `dropout` at `0.0` this makes no numerical difference today.) Note that `model.eval()` and `torch.no_grad()` are different switches: one changes how certain layers behave, the other stops gradient bookkeeping. Evaluation wants both.

The function leaves the model in evaluation mode when it returns. That is why the trainer calls `model.train()` right after calling `evaluate`.

`loss_function` is the same cross-entropy as in training, so evaluation loss and training loss are directly comparable. `total_loss` and `steps` accumulate the sum of losses and the number of examples.

**The loop**

```python

    for x, y in make_training_examples(
        path=dataset_path,
        context_length=config.context_length,
    ):
        x = x.unsqueeze(0).to(device)
        y = y.unsqueeze(0).to(device)

        logits = model(x)

        loss = loss_function(
            logits.reshape(-1, config.vocab_size),
            y.reshape(-1),
        )

        total_loss += loss.item()
        steps += 1
```

Compare this with the inner loop of `train`. The first half is identical, line for line in meaning: take an example, add the batch dimension so the shapes are `[1, T]`, move to the device, run the forward pass to get logits of shape `[1, T, 300]`, reshape to `[T, 300]` and `[T]`, and compute the mean cross-entropy over the `T` positions.

What is missing is the whole point: there is no `optimizer.zero_grad()`, no `loss.backward()` and no `optimizer.step()`. The model is measured, not taught.

`loss.item()` converts the one-number tensor to a Python `float`, and `steps` counts examples. Here a "step" is one evaluated example; no update happens.

**No examples: the `available: False` result**

```python

    if steps == 0:
        return {
            "available": False,
            "loss": None,
            "perplexity": None,
            "steps": 0,
        }
```

If the file produced no examples, the loop body never ran and `steps` is still `0`. There is nothing to average, and dividing by zero would crash. Instead the function returns a result that says so explicitly: `available` is `False` and the two measurements are `None`. Callers check `available` before using the numbers: the trainer skips the best-checkpoint decision, and the script prints "no evaluation examples".

A file produces no examples when it is empty, or when every document in it has fewer than two tokens (one token gives nothing to predict). The file must exist, though: for a path that does not exist, the loader's attempt to open it raises `FileNotFoundError`.

This is the result for the validation and test splits today. `storage/training/tokenized/validation.jsonl` and `test.jsonl` both exist and are both 0 bytes; the single tokenized document in the corpus is in `train.jsonl`. How documents are assigned to splits is covered in chapter 5. Until the corpus is large enough for documents to land in those two splits, there is no held-out text to measure on.

**Average loss and perplexity**

```python

    average_loss = total_loss / steps

    return {
        "available": True,
        "loss": average_loss,
        "perplexity": math.exp(average_loss),
        "steps": steps,
    }
```

`average_loss` is the sum of the per-example losses divided by the number of examples. As in the trainer, every example counts equally regardless of its length.

**Perplexity**

**What Python/PyTorch does** — `math.exp(v)` returns *e* raised to the power `v`. It is the inverse of the natural logarithm: `math.exp(math.log(n))` gives back `n`.

**What it means in the LLM/pipeline** — **Perplexity** is defined as `exp(loss)`. It is the same information as the loss, converted into a unit that is easier to picture.

Recall from 8.3 that a model choosing uniformly among `N` tokens has a loss of `ln(N)`. Perplexity runs that backwards: `exp(ln(N)) = N`. So:

> A perplexity of `N` means the model is, on average, as uncertain about the next token as if it were choosing uniformly among `N` equally likely tokens.

Lower is better. The scale for this project:

| Loss | Perplexity | Meaning |
|---|---|---|
| `5.70` (= ln 300) | `300` | No knowledge: every one of the 300 vocabulary tokens looks equally likely. The worst a sensible model should do. |
| `2.04` | `7.7` | As uncertain as a choice among about 8 tokens. |
| `0.69` (= ln 2) | `2` | Like a coin flip between two candidates. |
| `0` | `1` | Always certain and always right. The lowest possible value. |

The hand-computed example of 8.3 had a loss of 1.6552 over a 4-token vocabulary; its perplexity is `exp(1.6552)` = 5.23. That is *above* 4, worse than guessing, because one of its three predictions was confidently wrong.

One caution when comparing perplexities: the number is per *token*, so it depends on the tokenizer. A model with a 300-token vocabulary that works almost at the level of bytes and letters cannot be compared directly with a model whose tokens are whole words.

The real numbers. Running `python -m scripts.evaluate` on today's checkpoint prints:

```
train: loss=2.0433, perplexity=7.7162, steps=3
validation: no evaluation examples
test: no evaluation examples
```

`steps=3` is the three training examples from 8.1. The loss of `2.0433` is slightly lower than the `final_loss` of `2.1077` stored by the trainer because this figure measures the finished model, while the trainer's figure averaged over a model that was still improving during its last epoch.

**Why train-set perplexity says nothing about generalisation.** A perplexity of 7.7 looks like a large improvement on 300, but look at what it was measured on: the very 258 targets the model was trained on, each of which it has been shown and corrected on 21 times. A model with 884,480 adjustable numbers can lower its loss on 258 targets simply by storing the answers. A low loss on that text shows that the training loop works — gradients flow, parameters update, the loss falls — and nothing more. It does not show that the model has learned anything that applies to text it has not seen.

**Generalisation** means performing well on new text. The only way to measure it is on text that was kept out of training:

- the **validation** split, consulted during training to pick the best checkpoint and to notice when the model starts memorising (training loss still falling, validation loss rising);
- the **test** split, used once at the end for an honest final number, because any data you have used to make decisions is no longer fully unseen.

Both splits are empty today, so the project currently has no measurement of generalisation at all. The evaluation code is ready for one; the data is not there yet.

**The driving script** — `scripts/evaluate.py` (code in chapter 12) loads `artifacts/checkpoints/tiny_model.pt`, rebuilds the model from the checkpoint's own `config`, loads the weights, moves the model to the device, calls `evaluate` on `train.jsonl`, `validation.jsonl` and `test.jsonl` in turn, and prints one line per split. It saves no file.

#### What I should understand before moving on

- Evaluation is the training loop with the learning removed: same examples, same forward pass, same loss, but no `backward()` and no `step()`.
- `@torch.no_grad()` stops gradient bookkeeping; `model.eval()` switches layers such as dropout to their inference behaviour. They are separate switches and evaluation uses both.
- `evaluate` leaves the model in evaluation mode, so a caller that goes on training must call `model.train()` again.
- Perplexity is `exp(loss)`. A perplexity of `N` means "as uncertain as a uniform choice among `N` tokens". For this vocabulary, 300 is no knowledge and 1 is perfection.
- An empty split returns `available: False` with `None` for loss and perplexity instead of crashing; that is what validation and test return today.
- The 7.7 perplexity measured today is on the training text itself. It proves the machinery works, not that the model generalises.

#### Self-test

1. Evaluation and training both compute a loss on `(x, y)` examples. Name the three calls that training makes and evaluation does not, and say what would be wrong with an evaluation that made them.
2. What does `@torch.no_grad()` change, what does `model.eval()` change, and why is neither one a substitute for the other?
3. A model reports a perplexity of 300 on a 300-token vocabulary. What has it learned? What about a perplexity of 450?
4. Your training perplexity drops from 40 to 5 over ten epochs while validation perplexity goes from 45 to 30 and then climbs to 60. What is happening, and which checkpoint would the trainer have marked as best?
5. Why does `evaluate` return a dictionary with `available: False` for an empty file rather than a loss of `0`?
6. Today's evaluation prints a loss for `train` and nothing useful for `validation` and `test`. What exactly can and cannot be concluded about the model from that output?
7. The trainer stored `final_loss` = `2.1077` for its last epoch, but evaluating the saved model on the same file gives `2.0433`. Both use the same loss function on the same examples. Why do they differ?

<details><summary>Answers</summary>

1. `optimizer.zero_grad()`, `loss.backward()` and `optimizer.step()`. Making them would change the parameters while measuring them: the model would be learning from the evaluation text, so the text would no longer be unseen and the measurement would no longer describe a fixed model.
2. `torch.no_grad()` stops PyTorch from recording operations, so no gradients can be computed; it saves memory and time and guarantees nothing can be updated. `model.eval()` sets the training flag to false so that layers like dropout stop behaving randomly. The first does not alter what the layers compute; the second does not stop gradient recording.
3. A perplexity of 300 equals the vocabulary size, so the model is no better than choosing uniformly at random: it has learned nothing. A perplexity above the vocabulary size means it is worse than random, which happens when it puts high confidence on wrong tokens.
4. The model first learned patterns that carry over to unseen text, then began memorising the training text: training loss kept falling while validation loss rose. The best checkpoint is the one saved at the lowest validation loss — the epoch where validation perplexity was 30 — because `is_best` is true only when validation loss is lower than every earlier value.
5. A loss of `0` would claim perfect prediction, when in fact nothing was measured. There is also nothing to divide by. Returning `available: False` with `None` values lets callers tell "no data" apart from any real result and skip the logic that depends on it.
6. It can be concluded that the training loop functions and that the model fits the text it was trained on far better than random (perplexity about 7.7 against 300). Nothing can be concluded about how it performs on text it has not seen, because there is no held-out text in the validation or test split to measure on.
7. The trainer's figure is the average of losses measured during the epoch, each one taken before that step's update, so it describes a model that was still changing. The evaluator measures the final, fixed model on all examples after every update has been applied, so its figure is slightly lower.

</details>

---

## 10. Inference

| | |
|---|---|
| **INPUT** | A trained `TinyLLM` (weights loaded from a checkpoint), the `Tokenizer`, a prompt string, a token budget `max_new_tokens`, and a `temperature`. |
| **PROCESS** | Encode the prompt to token ids, then repeat: run the model, take the scores for the next token, forbid tokens that would break UTF-8, pick one token, append it. Stop at EOS or when the budget is used up. Decode the ids back to text. |
| **OUTPUT** | One Python string: the prompt followed by the generated continuation. Nothing is written to disk. |
| **WHY IT EXISTS** | Training only produces numbers in a checkpoint file. Inference is the code that turns those numbers into text you can read. |

The whole stage is one file, `src/inference/generator.py` (184 lines). The script that drives it from the command line is `scripts/inference.py` (chapter 12); the server in chapter 11 calls the same `generate()` function.

A note on reading order. In the file, the three UTF-8 helper functions come first (lines 7–85) and `generate()` comes last (lines 88–184). The helpers only make sense once you have seen the loop that calls them, so 10.1 reads the imports and the main loop of `generate()`, and 10.2 reads the helpers and the last few lines of `generate()`. Every block below is labelled with its line numbers so you can find it in the file.

### 10.1 Autoregressive generation

The model does exactly one thing: given a sequence of token ids, it returns a score for every possible *next* token (chapter 7). It never produces a sentence in one go.

Text comes from using that one ability in a loop:

1. Give the model the tokens so far.
2. Read its scores for the next token and choose one.
3. Append the chosen token to the sequence.
4. Go back to step 1 with the longer sequence.

This is called **autoregressive** generation: the model's own output becomes part of its next input. A tiny picture, with made-up tokens:

```text
step 1   input: <BOS> h i            model picks: " "
step 2   input: <BOS> h i " "        model picks: "t"
step 3   input: <BOS> h i " " t      model picks: "h"
...
```

It is the same task the model was trained on (chapter 8: predict token `t+1` from tokens `0..t`), only now there is no correct answer to compare with. Whatever is chosen is kept.

#### `src/inference/generator.py`

**Why this file exists** — It holds the generation loop and the rules that keep the generated bytes decodable as text. It is the only place in the project that turns a trained model into a string.

**What enters / what leaves** — `generate()` receives a model, a tokenizer, a prompt and two numbers, and returns a `str`. It reads no files and writes none. The three helper functions take bytes (and, for one of them, a tensor of scores) and return a `bool` or a new tensor.

**How it connects** — Called by `scripts/inference.py` and by `generate_text()` in `src/serving/server.py` (chapter 11). It calls `Tokenizer.encode`, `Tokenizer.token_to_bytes`, `Tokenizer.tokens_to_bytes` and `Tokenizer.decode` (chapter 6) and the model's forward pass (chapter 7).

**The code, section by section**

Lines 1–4, the imports:

```python
import torch

from src.model.model import TinyLLM
from src.tokenization.tokenizer import Tokenizer
```

- `torch` is PyTorch. This file uses it to build the input tensor, to turn scores into probabilities (`softmax`), and to pick a token (`argmax`, `multinomial`).
- `TinyLLM` and `Tokenizer` are imported only so the function signatures can say what type each argument is. The file never constructs either of them; the caller does.

Lines 88–95, the signature of `generate()`:

```python
@torch.no_grad()
def generate(
    model: TinyLLM,
    tokenizer: Tokenizer,
    prompt: str,
    max_new_tokens: int = 50,
    temperature: float = 1.0,
) -> str:
```

- `@torch.no_grad()` is a decorator: it wraps the whole function. Inside it PyTorch does not record the operations needed to compute gradients (chapter 8 explains gradients). Generation never calls `loss.backward()`, so recording them would only cost memory and time.
- `max_new_tokens` is the upper limit on how many tokens are *added*. The prompt's own tokens do not count against it.
- `temperature` controls how random the choice is. It is explained with numbers below. Note the default here is `1.0`; the server and the script both pass `0.0` explicitly unless told otherwise.

Lines 97–101:

```python

    model.eval()

    device = next(
        model.parameters()
    ).device
```

- `model.eval()` switches the model to evaluation mode. In this model the only layer that behaves differently between training and evaluation is dropout, which is turned off in evaluation mode. (The current configuration has `dropout: 0.0`, so today the call changes nothing in the output, but it is the correct habit.)
- `model.parameters()` is a generator over every weight tensor in the model. `next(...)` takes the first one, and `.device` says where that tensor lives: `cpu`, `mps` (Apple GPU) or `cuda`. All weights of a model live on the same device, so the first one is enough. The function needs this because the input tensor it builds later must be on the same device as the weights, otherwise PyTorch refuses to combine them.

Lines 103–111:

```python
    token_ids = tokenizer.encode(
        prompt,
        add_bos=True,
        add_eos=False,
    )

    current_bytes = tokenizer.tokens_to_bytes(
        token_ids
    )
```

- `encode` turns the prompt into a Python list of token ids. `add_bos=True` puts the BOS id (`256`) at the front, because every training document started with BOS (chapter 6) and the model should see the same shape of input it was trained on. `add_eos=False` because EOS means "the text is finished", and the point here is to continue it.
- `token_ids` is the growing sequence. Everything the loop does is appending to this list.
- `current_bytes` is the same sequence as raw bytes (special tokens contribute nothing). It is kept only for the UTF-8 check in 10.2.

Real values for the prompt `"hi"` with the trained tokenizer:

```text
token_ids     = [256, 104, 105]
current_bytes = b'hi'
```

Lines 113–124, the start of the loop:

```python
    for _ in range(max_new_tokens):
        context = token_ids[
            -model.config.context_length:
        ]

        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=device,
        )

        logits = model(x)
```

`for _ in range(max_new_tokens)` repeats at most `max_new_tokens` times. The name `_` is the Python convention for "I do not use this loop variable".

`context = token_ids[-model.config.context_length:]`

**What Python does** — A slice with a negative start takes the *last* N items of a list. With `context_length = 128`, a list of 500 ids becomes its last 128; a list of 3 ids is returned unchanged (asking for more items than exist is not an error).

**What it means in the LLM** — The model has a learned position vector for positions `0` to `context_length - 1` and nothing beyond that (chapter 7). It cannot be given a longer sequence. So once the text is longer than the window, the oldest tokens are dropped from what the model *sees*. They stay in `token_ids`, so they are still in the final text; the model has simply forgotten them.

`x = torch.tensor([context], dtype=torch.long, device=device)`

- `[context]` wraps the list in another list, so the tensor has two dimensions: shape `[1, T]`, one row of `T` token ids. The model always expects a batch `[B, T]`; here the batch holds a single sequence, so `B = 1`.
- `dtype=torch.long` makes the values 64-bit integers, which is what an embedding lookup requires for its indices.
- `device=device` creates the tensor directly where the model's weights are.

`logits = model(x)` runs the forward pass. The result has shape `[1, T, vocab_size]`: for each of the `T` positions, one score per token in the vocabulary. Checked on the real model with the prompt `"hi"`:

```text
x.shape              -> torch.Size([1, 3])
logits.shape         -> torch.Size([1, 3, 300])
logits[0, -1].shape  -> torch.Size([300])
```

Notice that every pass starts from scratch: the model recomputes all positions of the context on every step, even though only one new token was added. Nothing from the previous step is reused.

Lines 126–136:

```python
        next_token_logits = (
            logits[0, -1]
        )

        next_token_logits = (
            apply_utf8_constraint(
                logits=next_token_logits,
                tokenizer=tokenizer,
                current_bytes=current_bytes,
            )
        )
```

`logits[0, -1]`

**What PyTorch does** — Indexes the first dimension with `0` (the only sequence in the batch) and the second with `-1` (the last position). What remains is a one-dimensional tensor of shape `[vocab_size]`, here `[300]`.

**What it means in the LLM** — The output at position `i` is the model's prediction for the token at position `i + 1`. Positions `0` to `T-2` therefore predict tokens that are already in the sequence. During training all of them were useful, because each one had a correct answer to learn from. During generation only the last position predicts something not yet known, so it is the only row that is read.

The second statement passes those 300 scores through `apply_utf8_constraint`, which returns a copy where some scores have been replaced by negative infinity so those tokens can never be chosen. 10.2 covers it in full. For now, read `next_token_logits` as "the scores, minus the forbidden tokens".

Lines 138–157, choosing the token:

```python
        if temperature <= 0:
            next_token_id = int(
                torch.argmax(
                    next_token_logits
                )
            )

        else:
            probabilities = torch.softmax(
                next_token_logits
                / temperature,
                dim=-1,
            )

            next_token_id = int(
                torch.multinomial(
                    probabilities,
                    num_samples=1,
                )
            )
```

There are two ways to choose.

**Greedy (`temperature <= 0`).** `torch.argmax` returns the index of the largest value. The index *is* the token id, because position `k` of the tensor holds the score of token `k`. `int(...)` converts the one-element tensor into a plain Python integer. Greedy choice is deterministic: the same prompt and the same weights always give the same text. The `<= 0` test also protects the other branch from dividing by zero.

**Sampling (`temperature > 0`).** Two steps.

`torch.softmax(next_token_logits / temperature, dim=-1)`

**What PyTorch does** — Divides every score by `temperature`, then applies softmax (chapter 7): each value becomes `e^value` divided by the sum of all `e^value`, so the results are positive and add up to `1`. `dim=-1` says "normalise along the last dimension", which for a one-dimensional tensor is the only one.

**What it means in the LLM** — The scores become a probability for each possible next token. Dividing by the temperature first changes how far apart the scores are, and that changes the shape of the distribution:

Real numbers for a made-up vector of three scores, `[2.0, 1.0, 0.0]`:

| temperature | scores after dividing | probabilities after softmax |
|---|---|---|
| `0.5` | `[4.0, 2.0, 0.0]` | `[0.867, 0.117, 0.016]` |
| `1.0` | `[2.0, 1.0, 0.0]` | `[0.665, 0.245, 0.090]` |
| `2.0` | `[1.0, 0.5, 0.0]` | `[0.506, 0.307, 0.186]` |

- Below `1`, the gaps between scores grow, so the favourite takes more of the probability. The output becomes more predictable. As the temperature approaches `0` the favourite approaches probability `1`, which is why `0` is treated as greedy.
- At exactly `1`, the probabilities are the ones the model learned.
- Above `1`, the gaps shrink and the distribution flattens. Unlikely tokens are picked more often, so the text is more varied and more error-prone.

Temperature never changes the *order* of the tokens. The highest score stays the most probable at every temperature.

`torch.multinomial(probabilities, num_samples=1)`

**What PyTorch does** — Draws one index at random, where index `k` is drawn with probability `probabilities[k]`. It returns a tensor holding that one index; `int(...)` unwraps it.

**What it means in the LLM** — This is the actual "roll of the dice". Drawing 10,000 times from the middle row of the table above gave the three indices `6617`, `2455` and `928` times, matching `0.665 / 0.245 / 0.090`. A token with probability exactly `0` is never drawn, which is what makes the constraint in 10.2 work for sampling too.

Lines 159–170, the end of the loop body:

```python
        token_ids.append(
            next_token_id
        )

        if next_token_id == tokenizer.eos_id:
            break

        current_bytes += (
            tokenizer.token_to_bytes(
                next_token_id
            )
        )
```

- The chosen token is appended. On the next pass it is part of `context`, which is the "feed the output back in" step.
- If the token is EOS (`257`), `break` leaves the loop immediately. The model learned during training that EOS follows the end of a document, so choosing it is the model's way of saying it is done. EOS is appended to `token_ids` before the `break`; the decode step removes it again.
- Otherwise the token's bytes are added to `current_bytes`, keeping the byte view in step with `token_ids`.

So the loop ends in one of two ways: the model chose EOS, or `max_new_tokens` tokens were added. The remaining lines of the function (172–184) tidy the result and decode it; they depend on the UTF-8 rules, so they are shown at the end of 10.2.

A real run, greedy, with the checkpoint that exists today (a tiny model trained for a few seconds, so the continuation is not meaningful language):

```text
generate(model, tokenizer, "hi", max_new_tokens=12, temperature=0.0)
-> 'hiع، مجياتج '
```

Two things to notice: the returned string starts with the prompt itself, and the output is valid text even though the model works in bytes.

### 10.2 UTF-8 constrained generation

Chapter 6 explains that text is stored as bytes using UTF-8, where an English letter is one byte and an Arabic letter is two, and that this project's tokenizer starts from the 256 possible byte values and adds merged tokens on top. The consequence is that a token is a piece of *bytes*, not a piece of *text*, and one token can be half of a character.

You can see it in the real tokenizer. The word `"مرحبا"` encodes to:

```text
[256, 260, 266, 216, 173, 273, 259]

256 -> b''            (BOS)
260 -> b'\xd9\x85'    م
266 -> b'\xd8\xb1'    ر
216 -> b'\xd8'        first half of ح
173 -> b'\xad'        second half of ح
273 -> b'\xd8\xa8'    ب
259 -> b'\xd8\xa7'    ا
```

Tokens `216` and `173` are each half a letter. If the model emits `216` and then, instead of a valid second half, emits the token for `"a"`, the byte sequence `d8 61` is not UTF-8 and cannot be decoded to text at all. A well-trained model rarely does this; a small or young one does it often. The model has no built-in knowledge of UTF-8; it only has scores.

The fix used here is to check, before choosing, which tokens would keep the byte sequence valid, and to make the others impossible to choose.

The UTF-8 rules that matter are short:

| First byte of a character | Meaning | Must be followed by |
|---|---|---|
| `0x00`–`0x7F` | a complete one-byte character | nothing |
| `0xC2`–`0xDF` | start of a two-byte character | 1 continuation byte |
| `0xE0`–`0xEF` | start of a three-byte character | 2 continuation bytes |
| `0xF0`–`0xF4` | start of a four-byte character | 3 continuation bytes |
| `0x80`–`0xBF` | a continuation byte | only legal after a start byte |

The code does not implement these rules itself. It asks Python to decode the bytes and looks at whether, and how, that fails.

#### `src/inference/generator.py` (continued)

Lines 7–24, `is_valid_utf8_prefix`:

```python
def is_valid_utf8_prefix(
    data: bytes,
) -> bool:
    try:
        data.decode(
            "utf-8",
            errors="strict",
        )

        return True

    except UnicodeDecodeError as error:
        # نسمح فقط إذا sequence صحيحة حتى الآن
        # لكنها تحتاج continuation byte في النهاية.
        return (
            error.reason == "unexpected end of data"
            and error.end == len(data)
        )
```

The question this function answers: *could these bytes be the beginning of valid text?* Not "are they valid text now", but "can they still become valid if the right bytes follow".

- `data.decode("utf-8", errors="strict")` tries to turn the bytes into a string. With `errors="strict"`, Python raises `UnicodeDecodeError` at the first problem instead of substituting a replacement character. The decoded string is thrown away; only success or failure matters.
- If decoding succeeds, the bytes are complete valid text, which is certainly a valid beginning: `return True`.
- If it fails, the `except` block inspects the error object. A `UnicodeDecodeError` carries a `reason` (a short message) and `start`/`end` (the byte positions of the problem).

The comment inside the `except` block is written in Arabic, with the technical terms left in English:

```text
# نسمح فقط إذا sequence صحيحة حتى الآن
# لكنها تحتاج continuation byte في النهاية.
```

Its meaning: "We allow it only if the sequence is correct so far, but it needs a continuation byte at the end."

That is exactly what the two conditions test:

- `error.reason == "unexpected end of data"` — Python uses this reason only when a multi-byte character was started correctly and the data stopped before it was finished. Any other reason (`"invalid start byte"`, `"invalid continuation byte"`) means a byte that can never be right.
- `error.end == len(data)` — the problem reaches the very end of the data, so the unfinished character is the last thing in it and can still be completed by what comes next.

`and` combines them: both must hold. Real results:

| `data` | decode result | `is_valid_utf8_prefix` | `is_complete_utf8` |
|---|---|---|---|
| `b''` | ok | `True` | `True` |
| `b'\xd9\x85'` (م) | ok | `True` | `True` |
| `b'\xd9'` | unexpected end of data, end `1` of `1` | `True` | `False` |
| `b'hi\xd9'` | unexpected end of data, end `3` of `3` | `True` | `False` |
| `b'\xe2\x82'` | unexpected end of data, end `2` of `2` | `True` | `False` |
| `b'\xd9A'` | invalid continuation byte | `False` | `False` |
| `b'\x85'` | invalid start byte | `False` | `False` |

Lines 27–39, `is_complete_utf8`:

```python
def is_complete_utf8(
    data: bytes,
) -> bool:
    try:
        data.decode(
            "utf-8",
            errors="strict",
        )

        return True

    except UnicodeDecodeError:
        return False
```

The stricter question: *are these bytes valid text right now, with no character left half-finished?* Same decode attempt, but any failure at all returns `False`. The last column of the table above shows the difference: `b'\xd9'` is a valid prefix but is not complete.

The two functions are used for two different decisions. "Valid prefix" decides whether a token may be added. "Complete" decides whether generation may stop.

Lines 42–52, the start of `apply_utf8_constraint`:

```python
def apply_utf8_constraint(
    logits: torch.Tensor,
    tokenizer: Tokenizer,
    current_bytes: bytes,
) -> torch.Tensor:

    constrained = logits.clone()

    for token_id in range(
        tokenizer.vocab_size
    ):
```

- `logits` is the `[vocab_size]` tensor of next-token scores from `generate()`. `current_bytes` is everything generated so far, as bytes.
- `logits.clone()` makes an independent copy. The function edits the copy and returns it, so the tensor the caller passed in is not changed.
- The loop visits every token id in the vocabulary, `0` to `299` with the current tokenizer. Each id is one *candidate* for the next token, and the body decides whether that candidate is allowed.

Lines 53–61, the two tokens that are never allowed:

```python
        # BOS should never appear again.
        if token_id == tokenizer.bos_id:
            constrained[token_id] = float("-inf")
            continue

        # PAD is not a generation token.
        if token_id == tokenizer.pad_id:
            constrained[token_id] = float("-inf")
            continue
```

`constrained[token_id] = float("-inf")`

**What Python/PyTorch does** — `float("-inf")` is negative infinity, a real floating-point value that is smaller than every number. The assignment overwrites one score in the tensor with it.

**What it means in the LLM** — That token can no longer be chosen by either method. `argmax` never picks it because every finite score is larger. In sampling, softmax computes `e^(-inf)`, which is exactly `0`, so the token's probability is exactly zero and `multinomial` never draws it. Dividing by the temperature does not rescue it: `-inf / temperature` is still `-inf`. A real check with the middle score masked:

```text
softmax([2.0, -inf, 0.0]) -> [0.8808, 0.0000, 0.1192]
```

The remaining probabilities still add up to `1`: the masked token's share is redistributed over the allowed ones.

The reasons for the two rules:

- **BOS** (`256`) marks the start of a document. It is already at position `0` and has no meaning in the middle of one.
- **PAD** (`258`) is filler for making sequences equal in length; it stands for "nothing here" and is never part of real text (chapter 6).

`continue` skips the rest of the loop body and moves to the next `token_id`.

Lines 63–71, EOS:

```python
        # EOS only allowed when we are not
        # in the middle of a UTF-8 character.
        if token_id == tokenizer.eos_id:
            if not is_complete_utf8(
                current_bytes
            ):
                constrained[token_id] = float("-inf")

            continue
```

EOS (`257`) ends the text. That is fine when the bytes so far are complete text, and wrong when the last character is half-written, because stopping there would leave an undecodable tail. So EOS is masked only when `is_complete_utf8(current_bytes)` is false. When the bytes are complete, EOS keeps whatever score the model gave it. Either way `continue` follows: EOS has no bytes, so the byte test below does not apply to it.

Lines 73–85, every ordinary token:

```python
        candidate_bytes = (
            current_bytes
            + tokenizer.token_to_bytes(
                token_id
            )
        )

        if not is_valid_utf8_prefix(
            candidate_bytes
        ):
            constrained[token_id] = float("-inf")

    return constrained
```

- `tokenizer.token_to_bytes(token_id)` returns the bytes this token stands for: one byte for ids `0`–`255`, two or more for merged tokens.
- `candidate_bytes` is "what the output would be if this token were chosen": everything so far plus this token's bytes. `+` on two `bytes` values joins them into a new one; `current_bytes` itself is not modified.
- If that hypothetical output is not a valid UTF-8 prefix, the token is masked. If it is, the score is left alone.
- After the loop, the edited copy is returned. Scores of allowed tokens are untouched, so the model's preferences among them are exactly as before.

The constraint does not choose anything and does not make the text *sensible*. It only removes choices that are byte-level impossible. There is always at least one allowed token: after a valid prefix, either some continuation byte or some new character is legal.

**A real demonstration.** The letter `م` is the two bytes `d9 85`. Suppose the output so far ends with only the first of them, `b"\xd9"`. Which of the 300 tokens are allowed next? Using all-zero scores so that only the masking shows:

```pycon
>>> "م".encode("utf-8")
b'\xd9\x85'
>>> logits = torch.zeros(tokenizer.vocab_size)
>>> constrained = apply_utf8_constraint(logits, tokenizer, b"\xd9")
>>> allowed = [
...     token_id
...     for token_id in range(tokenizer.vocab_size)
...     if constrained[token_id] != float("-inf")
... ]
>>> len(allowed), tokenizer.vocab_size
(65, 300)
>>> allowed[:3], allowed[-3:]
([128, 129, 130], [190, 191, 283])
>>> tokenizer.token_to_bytes(283)
b'\xae\xd8\xaa'
>>> tokenizer.eos_id in allowed
False
```

Reading the result:

- 65 of 300 tokens survive. 64 of them are the single-byte tokens `128`–`191`, which are exactly the continuation bytes `0x80`–`0xBF`. Any of them completes the character (`d9 80` is `ـ`, `d9 bf` is `ٿ`).
- The 65th is merged token `283`, whose bytes are `ae d8 aa`. It starts with a continuation byte, so `d9 ae` completes one character and `d8 aa` is a whole second one (`ت`). This shows why the test has to be done on real bytes for every token: a merged token can begin in the middle of a character.
- Every ASCII token, every start byte and every other merged token is masked, because each would put a non-continuation byte after `d9`.
- EOS is masked, because `b"\xd9"` is not complete. BOS and PAD are masked as always.

For comparison, when the bytes so far are `b"hi"` (complete), 220 tokens are allowed. The 80 masked ones are the 64 continuation bytes (nothing to continue), the 13 byte values that are never legal in UTF-8 (`0xC0`, `0xC1`, `0xF5`–`0xFF`), token `283` (it starts with a continuation byte), BOS and PAD. EOS is allowed.

**The cost.** `apply_utf8_constraint` runs once per generated token and loops over the whole vocabulary each time, in plain Python. For each candidate it builds a new `bytes` value and decodes all of it, from the first byte of the prompt. Measured on this machine with the 300-token vocabulary: about `0.4` ms per call with 2 bytes of history and about `0.5` ms with 2,000 bytes. That is small today. It grows in proportion to the vocabulary size (a 30,000-token vocabulary means 100 times more candidates per step) and, more slowly, with the length of the text, because the whole history is decoded again for every candidate.

Lines 172–184, the end of `generate()`:

```python
    # The token budget can run out in the middle of a
    # UTF-8 character. Drop the unfinished tail so the
    # strict decode below cannot fail.
    while not is_complete_utf8(
        tokenizer.tokens_to_bytes(token_ids)
    ):
        token_ids.pop()

    return tokenizer.decode(
        token_ids,
        skip_special_tokens=True,
        errors="strict",
    )
```

The constraint guarantees that the bytes are always a valid *prefix*. It cannot guarantee they are *complete* when the loop stops, because the loop can stop for a reason the model has no say in: `max_new_tokens` ran out. If the last token allowed was the first half of a letter, the sequence ends with a dangling start byte.

- `tokenizer.tokens_to_bytes(token_ids)` rebuilds the bytes of the whole sequence (specials contribute nothing).
- While those bytes are not complete UTF-8, `token_ids.pop()` removes the last token and the test runs again. One pop is usually enough; a three- or four-byte character spread over several tokens can need more.
- The loop is certain to end. The prompt came from a Python `str`, so its bytes are complete, and every prefix of a valid-prefix sequence that ends on a character boundary is complete. In the worst case the pops go back to the end of the prompt.

The cost of this cleanup is that the result can contain slightly fewer than `max_new_tokens` new tokens.

`tokenizer.decode(token_ids, skip_special_tokens=True, errors="strict")` then turns the ids into the final string.

- `skip_special_tokens=True` leaves BOS (and EOS, if generation ended with it) out of the text.
- `errors="strict"` means "raise an error if the bytes are not valid UTF-8". It is safe to be strict here because of the two guarantees just built: every added token kept the bytes a valid prefix, and the `while` loop removed any unfinished tail. Together they mean the bytes are complete valid UTF-8, so the strict decode cannot fail. Being strict rather than lenient also means that if one of those guarantees were ever broken by a later change, you would get an error instead of silently corrupted text.

The returned string is the prompt plus the continuation, because `token_ids` has contained the prompt's tokens since the first line.

#### What I should understand before moving on

- The model only scores the next token. Text is produced by choosing one token, appending it, and running the model again on the longer sequence.
- Only `logits[0, -1]` is read, because the last position is the only one predicting a token that is not already known.
- When the sequence is longer than `context_length`, the model sees only the last `context_length` tokens; the older ones remain in the output but no longer influence it.
- `temperature <= 0` means greedy `argmax` and a repeatable result. A positive temperature divides the scores before softmax: below `1` sharpens the distribution, above `1` flattens it, and a token is then drawn at random from it.
- Tokens are pieces of bytes. A token can be half an Arabic letter, so an unconstrained model can produce bytes that are not text.
- Setting a score to `-inf` gives the token probability exactly `0` under softmax and makes it lose every `argmax`, so it cannot be chosen.
- "Valid prefix" (may still become valid) decides which tokens may be added; "complete" (valid now) decides whether EOS is allowed and whether the tail must be trimmed.
- Generation stops at EOS or at `max_new_tokens`; the second case is why a cleanup loop is needed before the strict decode.

#### Self-test

1. The model returns scores of shape `[1, T, vocab_size]`. Why does `generate()` throw away all rows except the last, when training used every row?
2. You generate 300 tokens from a 10-token prompt with `context_length = 128`. On the last step, how many tokens does the model see, and does the prompt still influence the choice?
3. With scores `[2.0, 1.0, 0.0]`, what happens to the probability of the first token as the temperature goes from `2.0` to `0.5`, and why can temperature never make the second token more likely than the first?
4. Why does the code test `temperature <= 0` instead of just letting a temperature of `0` go through the sampling branch?
5. The bytes so far are `b"hi\xd9"`. Is EOS allowed? Is the token for the letter `a` allowed? Explain each using the two helper functions.
6. Why does the constraint have to test merged tokens against the actual bytes, instead of applying a simple rule such as "after a start byte, allow only ids `128`–`191`"?
7. The constraint guarantees a valid prefix after every step. Why can the final byte sequence still be undecodable, and which lines deal with that?
8. A call with `max_new_tokens=50` returns text containing only 49 new tokens and no EOS was produced. What happened?

<details><summary>Answers</summary>

1. Row `i` predicts the token at position `i + 1`. For all rows but the last, that token is already in the sequence. In training those rows are compared with the known answers to compute the loss. In generation there is nothing to learn, and the only unknown token is the one after the last position.
2. It sees 128 tokens: the slice `token_ids[-128:]`. By then the sequence has more than 300 tokens, so the prompt is far outside the window and has no direct influence. It is still in `token_ids` and still appears in the returned text.
3. It rises from about `0.506` to about `0.867`. Dividing all scores by the same positive number keeps their order, and softmax preserves order, so the largest score is the most probable at every temperature; only the size of the gaps changes.
4. Dividing by zero would produce infinities and `nan` values, and a negative temperature would reverse the order of the scores. The limit of lower and lower temperature is "always take the top token", which `argmax` does directly and exactly.
5. EOS is not allowed: `is_complete_utf8(b"hi\xd9")` is `False`, because a two-byte character has been started and not finished. `a` is not allowed: the candidate `b"hi\xd9a"` fails to decode with "invalid continuation byte", which is not "unexpected end of data", so `is_valid_utf8_prefix` returns `False`.
6. A merged token is several bytes and can start with a continuation byte and then go on to further characters, like token `283` (`ae d8 aa`). Whether it is legal depends on all of its bytes in the current position, which no rule based on id ranges captures. Other merged tokens start with a start byte and are illegal there even though their ids are far from the single-byte range.
7. A valid prefix may end with an unfinished character, and the loop can end because the token budget ran out rather than because EOS was chosen. Lines 175–178 pop tokens until the bytes are complete.
8. The 50th token left a multi-byte character unfinished (for example it was a lone start byte). The cleanup loop removed it so the strict decode would succeed.

</details>

## 11. The serving backend

| | |
|---|---|
| **INPUT** | HTTP requests on `http://127.0.0.1:8000`. For generation: a JSON body with a prompt and optional model id, token budget and temperature. On disk: the checkpoints in `artifacts/checkpoints/*.pt`, the tokenizer in `artifacts/tokenizer/tokenizer.json`, and (for the admin endpoints) `artifacts/runs` and the `storage/` directories. |
| **PROCESS** | A long-running process validates each request, finds and loads the requested checkpoint (keeping a few loaded models in memory), runs `generate()` from chapter 10, and turns the result or the failure into an HTTP response. |
| **OUTPUT** | JSON responses: generated text, the list of models, health, and read-only counts about runs and data. It also hands out pre-built static client files. Nothing in this chapter writes to disk. |
| **WHY IT EXISTS** | A script loads the model, answers once and exits. A service loads it once and answers many requests from any program that can speak HTTP. |

Three files: `src/serving/model_manager.py` (414 lines), `src/serving/server.py` (202 lines) and `src/serving/admin.py` (230 lines). The script that starts the service is `scripts/serve.py` (chapter 12).

### 11.1 What serving is

Until now every stage was a script: start, do the work, exit. `scripts/inference.py` spends most of its time loading PyTorch and the checkpoint, generates one answer, and then throws the loaded model away.

**Serving** means the model lives inside a process that does not exit. The process listens on a network port. A *client* (a browser, `curl`, another program) sends a request; the process sends back a response and goes on waiting for the next one. The language they speak is HTTP, and the data inside is JSON.

One real exchange with the running server:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"hi","max_new_tokens":12}'
```

```text
{"model":"tiny_model.pt","text":"hiع، مجياتج "}
```

The vocabulary you need for the three files:

**HTTP method and path.** A request names a method and a path. `GET /health` means "give me something" at `/health`; `POST /generate` means "here is data, do something with it" at `/generate`. `GET` requests carry options in the URL after a `?` (a *query parameter*, e.g. `/models?include_checkpoints=true`); `POST` requests carry a *body*, here JSON.

**FastAPI.** A Python library for writing HTTP services. You create one `FastAPI()` object, conventionally called `app`, and attach your functions to it. FastAPI takes care of parsing requests, calling the right function, and converting what the function returns into a JSON response. FastAPI does not listen on the network itself; a separate program called `uvicorn` does that and passes each request to `app`. `scripts/serve.py` starts `uvicorn` on `127.0.0.1:8000`. The address `127.0.0.1` is the machine itself, so the service is reachable only from the same computer.

**Routes.** A route is the pairing of a method and a path with a Python function. The decorator `@app.get("/health")` placed above a function says: when a `GET /health` request arrives, call this function. If the function returns a `dict`, FastAPI sends it as JSON. A group of routes can be collected on an `APIRouter` and attached to the app later; `admin.py` does this.

**Request and response models (pydantic).** `pydantic` is the library FastAPI uses to describe and check the shape of data. You write a class that inherits from `BaseModel` and list its fields with type hints. When a function parameter has such a class as its type, FastAPI reads the JSON body, checks every field, converts types, and gives the function a ready object. If the body does not fit, the function is never called and the client gets an error that lists what was wrong. `Field(...)` adds limits to a single field: `min_length=1` for strings, `ge=` ("greater than or equal") and `le=` ("less than or equal") for numbers, and `default=` for the value used when the client omits the field.

A real rejection from the running server, for `{"prompt":""}`:

```text
HTTP 422
{"detail":[{"type":"string_too_short","loc":["body","prompt"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
```

**Status codes.** Every HTTP response starts with a three-digit number. The ones this service produces:

| Code | Meaning | Where it comes from here |
|---|---|---|
| `200` | success | any handler that returns normally |
| `307` | temporary redirect: "ask again at this other URL" | `/chat` → `/chat/`, `/admin` → `/admin/` |
| `404` | not found | unknown model id, no models, unknown path |
| `422` | the request body or query failed validation | produced by FastAPI/pydantic automatically |
| `500` | the server failed while handling a valid request | an exception during generation |
| `503` | service unavailable: the request was fine but a needed resource cannot be used right now | a checkpoint or tokenizer that cannot be loaded |

The first digit is the family: `2xx` success, `3xx` redirect, `4xx` the client's mistake, `5xx` the server's problem.

**`HTTPException`.** Inside a route function, `raise HTTPException(status_code=404, detail="...")` stops the function and makes FastAPI send a response with that status code and the body `{"detail": "..."}`. It is how a handler says "this request fails, and here is the code the client should see".

**Threads.** FastAPI runs route functions written with plain `def` (all of the ones in this project) on a pool of worker threads, so two requests can be inside the same function at the same moment. That is why shared state in these files is protected by locks. Locks are explained in 11.2.

### 11.2 The model manager

| | |
|---|---|
| **INPUT** | A checkpoint directory, a tokenizer path, the file name of the default model, a device, and a limit on how many models may be held in memory. Later, model ids supplied by clients. |
| **PROCESS** | List the `.pt` files in the directory, read and cache their metadata, and on request load a checkpoint into a `TinyLLM`, keeping the most recently used models in memory. |
| **OUTPUT** | Lists of metadata dicts, a `Tokenizer`, and loaded `TinyLLM` objects ready for `generate()`. Two exception types for the two ways a request for a model can fail. |
| **WHY IT EXISTS** | So that exactly one object knows where models are, which ones are usable, and which are in memory. The HTTP layer never touches a checkpoint path itself. |

#### `src/serving/model_manager.py`

**Why this file exists** — It is the single owner of model discovery, metadata, loading and caching. Both the public API (`server.py`) and the admin API (`admin.py`) ask it instead of looking at the filesystem.

**What enters / what leaves** — The constructor takes paths and settings and reads nothing. `list_models()` returns a list of dicts. `latest_model_id()` returns a file name or `None`. `tokenizer_for()` returns a `Tokenizer`. `load()` returns a `TinyLLM` in evaluation mode on the serving device. Files read: `artifacts/checkpoints/*.pt` and `artifacts/tokenizer/tokenizer.json`. Files written: none.

**How it connects** — It reads the checkpoints written by training (chapter 8) and the tokenizer written by tokenizer training (chapter 6). `server.py` creates the one `ModelManager` instance at import time and passes it to `create_admin_router` in `admin.py`.

**The code, section by section**

```python
import re
import threading
from collections import OrderedDict
from pathlib import Path

import torch

from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.tokenization.tokenizer import Tokenizer
```

- `re` — regular expressions, used to recognise per-epoch checkpoint file names and to split names into words.
- `threading` — provides the lock that stops two request threads from changing the caches at once.
- `OrderedDict` — a dictionary that remembers the order of its keys and can move a key to the end or remove the first one. It is the data structure behind the loaded-model cache.
- `Path` — filesystem paths (primer in chapter 1).
- `torch` — to read checkpoint files (`torch.load`) and for the `torch.device` type.
- `ModelConfig`, `TinyLLM` — to rebuild a model from the configuration stored in the checkpoint (chapter 7).
- `Tokenizer` — to load the tokenizer and compare its vocabulary size with the model's.

```python
class UnknownModelError(Exception):
    """The requested model id is not a discovered checkpoint."""


class ModelLoadError(Exception):
    """A discovered checkpoint or its tokenizer cannot be used."""
```

Two exception classes with no body other than a docstring. Inheriting from `Exception` is enough to make them raisable and catchable by name. They exist so the caller can tell two situations apart:

- `UnknownModelError` — there is no such model. The client asked for something that does not exist.
- `ModelLoadError` — the model exists but cannot be used (corrupt file, wrong format, tokenizer missing or mismatched). The client's request was reasonable; the server's files are the problem.

`server.py` turns the first into `404` and the second into `503`. Keeping HTTP codes out of this file means the manager could be used by something that is not a web server.

```python
HISTORY_CHECKPOINT_PATTERN = re.compile(
    r"checkpoint_epoch_(\d+)_step_(\d+)"
)
```

Training saves two kinds of file into `artifacts/checkpoints` (chapter 8): the main checkpoint `tiny_model.pt`, and one history file per epoch named like `checkpoint_epoch_000021_step_000000063.pt`. This pattern recognises the second kind.

- `re.compile` turns the pattern text into a reusable pattern object once, when the module is imported.
- The `r"..."` prefix makes a raw string, so backslashes reach the regular-expression engine unchanged.
- `\d+` means "one or more digits". The parentheses make each run of digits a *group* that can be read back later: group 1 is the epoch, group 2 is the step.

```python
def display_name(stem: str) -> str:
    """
    Human-friendly name for a checkpoint file stem.

    tiny_model -> Tiny Model
    checkpoint_epoch_000021_step_000000063
        -> Checkpoint Epoch 21 · Step 63
    jsm_10m -> JSM 10M
    """

    match = HISTORY_CHECKPOINT_PATTERN.fullmatch(stem)

    if match is not None:
        return (
            f"Checkpoint Epoch {int(match.group(1))}"
            f" · Step {int(match.group(2))}"
        )
```

A *stem* is a file name without its extension: the stem of `tiny_model.pt` is `tiny_model`.

- `fullmatch` succeeds only if the *whole* string fits the pattern. It returns a match object, or `None`.
- For a history checkpoint, the two digit groups are read with `match.group(1)` and `match.group(2)`. `int("000021")` is `21`, which drops the zero padding. Two adjacent f-strings inside parentheses are joined by Python into one string.

```python
    words = [
        word.upper()
        if word.lower() == "jsm"
        or any(character.isdigit() for character in word)
        else word.capitalize()
        for word in re.split(r"[_\-\s]+", stem)
        if word
    ]

    return " ".join(words) or stem
```

For every other name, a list comprehension (primer in chapter 1) builds the words. Read it from the bottom:

- `re.split(r"[_\-\s]+", stem)` cuts the stem at every run of underscores, hyphens or whitespace.
- `if word` drops empty pieces (a name starting with `_` produces one).
- Each remaining word becomes all upper case if it is `jsm` in any casing or contains a digit; otherwise only its first letter is capitalised.
- `" ".join(words) or stem` joins the words with spaces. If there were no words at all, the join is an empty string, which Python treats as false, so `or stem` returns the original stem instead.

Real results:

| stem | `display_name(stem)` |
|---|---|
| `tiny_model` | `Tiny Model` |
| `checkpoint_epoch_000021_step_000000063` | `Checkpoint Epoch 21 · Step 63` |
| `jsm_10m` | `JSM 10M` |
| `my-model v2` | `My Model V2` |
| `___` | `___` |

This function only produces a label for people. Nothing looks a model up by its display name.

```python
class ModelManager:
    """
    Single owner of model discovery, metadata, loading and caching.

    Today models are .pt files directly under one checkpoint
    directory. A later registry / publish system only has to
    replace the discovery part of this class.
    """

    def __init__(
        self,
        checkpoints_dir: Path,
        tokenizer_path: Path,
        default_model_id: str,
        device: torch.device,
        max_loaded_models: int = 4,
    ) -> None:
        self.checkpoints_dir = checkpoints_dir
        self.tokenizer_path = tokenizer_path
        self.default_model_id = default_model_id
        self.device = device
        self.max_loaded_models = max_loaded_models
```

The constructor stores its five arguments on `self` and does no work on disk.

- `checkpoints_dir` — the one directory searched for models.
- `tokenizer_path` — the one tokenizer file shared by all models.
- `default_model_id` — the file name that should be treated as "the latest model" when it exists. `server.py` passes `tiny_model.pt`.
- `device` — where loaded models are placed for generation.
- `max_loaded_models` — how many models may stay in memory at once; `4` unless the caller says otherwise, and `server.py` does not.

A **model id** in this project is simply the checkpoint's file name including the extension, for example `tiny_model.pt`.

```python
        self._lock = threading.RLock()

        # model id -> (file signature, metadata or None if unusable)
        self._metadata_cache: dict[
            str, tuple[tuple, dict | None]
        ] = {}

        # model id -> (file signature, loaded model)
        self._loaded: OrderedDict[
            str, tuple[tuple, TinyLLM]
        ] = OrderedDict()

        self._tokenizer: Tokenizer | None = None
```

The leading underscore in a name is the Python convention for "internal; code outside this class should not touch it".

`self._lock = threading.RLock()`

**What Python does** — A lock is an object that only one thread can hold at a time. `with self._lock:` means: wait until no other thread holds the lock, take it, run the indented block, release it (also if the block raises). An `RLock` is a *re-entrant* lock: the thread that already holds it may take it again without waiting for itself.

**What it means here** — Request handlers run on several threads. Without a lock, two requests could both decide a model is not loaded and both load it, or one could be removing a cache entry while another reads it. Every public method of this class does its work inside `with self._lock:`, so only one thread at a time is inside the manager. It has to be the re-entrant kind because the methods call each other while holding it: `load()` calls `tokenizer_for()`, and both take the lock. With an ordinary `threading.Lock` the second `with` would wait forever for the first to finish.

The two caches both store a *file signature* next to the cached value. The signature (defined below) changes when the file changes, which is how the manager notices that a cached value is out of date.

- `_metadata_cache` maps a model id to `(signature, metadata)`. The metadata is a small dict, or `None` meaning "this file was examined and is not usable". Remembering the `None` matters: without it, a corrupt file would be read again on every listing.
- `_loaded` maps a model id to `(signature, model)`. These are the expensive entries: whole models in memory. The key order of the `OrderedDict` records how recently each one was used.
- `_tokenizer` starts as `None` and is filled the first time a tokenizer is needed.

The type hints (`dict[str, tuple[tuple, dict | None]]`) only document these shapes; Python does not enforce them.

```python
    # --------------------------------------------------
    # Discovery
    # --------------------------------------------------

    def _discover(self) -> dict[str, Path]:
        """
        Model id -> path, for checkpoints directly under
        the checkpoint directory.

        Every lookup of a client-supplied id goes through
        this mapping, so an id can never name another path.
        """

        if not self.checkpoints_dir.is_dir():
            return {}

        return {
            path.name: path
            for path in self.checkpoints_dir.glob("*.pt")
            if path.is_file()
            and not path.is_symlink()
        }
```

Discovery answers "which models exist right now?" by looking at the directory every time it is called. Nothing is remembered between calls, so a file added or removed while the server runs is noticed on the next request.

- If the directory does not exist, the answer is an empty dict rather than an error.
- `glob("*.pt")` yields the entries *directly* inside the directory whose names end in `.pt`. It does not look into subdirectories.
- `path.is_file()` drops directories that happen to be named `something.pt`.
- `not path.is_symlink()` drops symbolic links. A symlink is a file-system entry that points at another path; one placed in the checkpoint directory could point anywhere on the machine, so it is not accepted as a model.
- The dict comprehension maps each file name (`path.name`) to its `Path`.

**Why a client-supplied id is only ever looked up in this mapping.** The model id comes from outside, in the JSON body of a request. The dangerous way to use it would be to build a path from it, such as `checkpoints_dir / model_id`. A client could then send `../../something` and make the server open a file outside the checkpoint directory. That attack is called *path traversal*. This class never builds a path from an id. It builds the mapping from what is really in the directory, and then asks whether the id is one of the keys. A string that is not the exact name of a real `.pt` file in that directory is simply absent. A real request against the running server:

```text
POST /generate  {"prompt":"hi","model":"../../paths.py"}

HTTP 404
{"detail":"Unknown model: ../../paths.py"}
```

```python
    @staticmethod
    def _signature(path: Path) -> tuple:
        stat = path.stat()

        return (
            stat.st_mtime_ns,
            stat.st_size,
        )
```

- `@staticmethod` marks a function that lives in the class for tidiness but does not use `self`.
- `path.stat()` asks the operating system for the file's metadata without reading its contents.
- `st_mtime_ns` is the time the file was last modified, in nanoseconds; `st_size` is its size in bytes.

The pair is a cheap "has this file changed?" test. Training replaces a checkpoint file when it saves (chapter 8), which gives it a new modification time, so the signature differs and anything cached for the old file is ignored. It is a practical shortcut, not proof of identical content the way a SHA-256 hash is (4.1), but reading two numbers costs almost nothing while hashing a 10 MB file on every request would not.

```python
    def _read_checkpoint(self, path: Path) -> dict:
        try:
            checkpoint = torch.load(
                path,
                map_location="cpu",
                weights_only=True,
            )

        except Exception as error:
            raise ModelLoadError(
                f"Cannot read checkpoint {path.name}: "
                f"{error}"
            ) from error
```

`torch.load(path, map_location="cpu", weights_only=True)`

**What PyTorch does** — Reads a file written by `torch.save` and rebuilds the Python object stored in it; for this project that is a dict (chapter 8). `map_location="cpu"` places every tensor in main memory regardless of the device it was saved from. `weights_only=True` restricts loading to plain data: tensors, numbers, strings, and containers of those.

**What it means for a server** — `.pt` files use Python's `pickle` format. A pickle is not just data; it is a small program of instructions for rebuilding objects, and those instructions can include "import this function and call it with these arguments". Fully loading a pickle that someone else crafted can therefore run any code they chose, with the server's permissions. A server that loads whatever `.pt` file appears in a directory must not do that. With `weights_only=True`, a file that tries to do anything other than describe plain data is rejected with an error instead of being executed.

`map_location="cpu"` is chosen because this function is also used just to read metadata, and there is no reason to put a model on the GPU for that. `load()` moves the model to the real device later.

Any failure (unreadable file, not a pickle, forbidden content) is caught by `except Exception` and re-raised as `ModelLoadError`. `from error` keeps the original error attached as the cause (primer in chapter 1). The message uses `path.name`, the file name only.

```python
        if (
            not isinstance(checkpoint, dict)
            or not isinstance(
                checkpoint.get("config"), dict
            )
            or not isinstance(
                checkpoint.get("model_state_dict"), dict
            )
        ):
            raise ModelLoadError(
                f"{path.name} is not a JSM checkpoint"
            )

        try:
            ModelConfig(**checkpoint["config"])

        except TypeError as error:
            raise ModelLoadError(
                f"{path.name} has an incompatible "
                f"model config: {error}"
            ) from error

        return checkpoint
```

A file can load without error and still not be one of this project's checkpoints, so its shape is checked:

- the loaded object must be a dict;
- it must have a `"config"` entry that is a dict;
- it must have a `"model_state_dict"` entry that is a dict (the weights by name).

`checkpoint.get("config")` returns `None` when the key is missing, and `None` is not a dict, so one test covers both "missing" and "wrong type". Because the conditions are joined with `or` and evaluated left to right, `.get` is only reached when the first test has confirmed that `checkpoint` is a dict.

Then `ModelConfig(**checkpoint["config"])` tries to build the configuration object. `**` unpacks the dict into keyword arguments. If the stored config has a key that `ModelConfig` does not know, Python raises `TypeError` (for a made-up key: `ModelConfig.__init__() got an unexpected keyword argument 'bogus'`), which becomes a `ModelLoadError`. The object built here is not kept; the line is purely a test. Keys that are *missing* do not cause an error, because every field of `ModelConfig` has a default value.

The real checkpoint contains these top-level keys:

```text
['config', 'model_state_dict', 'model_stats', 'optimizer_state_dict', 'training_config', 'training_stats']
```

```python
    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def _metadata(
        self,
        model_id: str,
        path: Path,
    ) -> dict | None:
        signature = self._signature(path)

        cached = self._metadata_cache.get(model_id)

        if cached is not None and cached[0] == signature:
            return cached[1]
```

`_metadata` returns the description of one model, or `None` if the file is unusable. It starts with the cache check that both caches use:

1. Compute the file's current signature.
2. Look up the cache entry for this id.
3. If there is an entry and its stored signature (`cached[0]`) equals the current one, the file has not changed since it was examined: return the stored result (`cached[1]`), which may be a dict or `None`.

Otherwise the function continues and examines the file.

```python
        try:
            checkpoint = self._read_checkpoint(path)

        except ModelLoadError:
            metadata = None

        else:
            config = checkpoint["config"]

            # Older checkpoints may miss any of these.
            training_stats = (
                checkpoint.get("training_stats") or {}
            )
            model_stats = (
                checkpoint.get("model_stats") or {}
            )
```

- `try / except / else`: the `else` block runs only when the `try` block raised nothing. So a failed read sets `metadata = None`, and a successful read goes on to build the dict.
- `checkpoint.get("training_stats") or {}` yields the stored dict if present, and an empty dict if the key is missing or holds `None`. The following code can then call `.get(...)` on it without checking first.

Reading the whole checkpoint to learn a few numbers is the expensive part of a listing (each file here is about 10 MB and includes the optimizer state), which is the reason the result is cached.

```python
            metadata = {
                "id": model_id,
                "name": path.stem,
                "display_name": display_name(path.stem),
                # "checkpoint" = a per-epoch training snapshot,
                # "model" = something meant to be used.
                "kind": (
                    "checkpoint"
                    if HISTORY_CHECKPOINT_PATTERN.fullmatch(
                        path.stem
                    )
                    else "model"
                ),
                "parameters": model_stats.get(
                    "total_parameters"
                ),
                "trainable_parameters": model_stats.get(
                    "trainable_parameters"
                ),
                "epochs": training_stats.get(
                    "epochs_completed"
                ),
                "global_step": training_stats.get(
                    "global_step"
                ),
                "tokens_seen": training_stats.get(
                    "tokens_seen"
                ),
                "vocab_size": config.get("vocab_size"),
                "context_length": config.get(
                    "context_length"
                ),
            }
```

The metadata dict, field by field:

| Field | Source | Meaning |
|---|---|---|
| `id` | file name | what a client sends back to select this model |
| `name` | file name without `.pt` | the raw name |
| `display_name` | `display_name(stem)` | the label for people |
| `kind` | file name pattern | `"checkpoint"` for a per-epoch history file, `"model"` for anything else |
| `parameters`, `trainable_parameters` | `model_stats` | weight counts (chapter 7) |
| `epochs`, `global_step`, `tokens_seen` | `training_stats` | how much training produced these weights (chapter 8) |
| `vocab_size`, `context_length` | `config` | the model's vocabulary size and window |

Every value from `model_stats`, `training_stats` and `config` is read with `.get(key)`, which returns `None` for a missing key instead of raising. A checkpoint saved by an older version of the training code, before some statistic was recorded, therefore still lists; the missing fields arrive in the JSON as `null`. The comment "Older checkpoints may miss any of these" states that intent.

**The `kind` field.** A training run of 21 epochs leaves 22 files: 21 per-epoch snapshots and `tiny_model.pt`. The snapshots are a record of how training went. They are loadable, but they are not what you want to offer in a model picker. `kind` lets the listing separate the two purely by file name, without a second directory or a registry.

```python
        self._metadata_cache[model_id] = (
            signature,
            metadata,
        )

        return metadata
```

Whatever the outcome, dict or `None`, it is stored with the signature it was computed for, and returned.

```python
    def _mark_unusable(
        self,
        model_id: str,
        signature: tuple,
    ) -> None:
        self._metadata_cache[model_id] = (
            signature,
            None,
        )
```

A one-statement helper that overwrites a cache entry with "unusable". It is needed because `_metadata` only checks that a file *reads* as a checkpoint. A file can pass that test and still fail when `load()` tries to put its weights into a model. When that happens, `load()` calls this so the model also disappears from listings, until the file changes and gets a new signature.

```python
    def list_models(
        self,
        include_checkpoints: bool = False,
    ) -> list[dict]:
        """
        Usable models, latest first.

        Corrupt or incompatible checkpoints are skipped.
        Per-epoch training snapshots are left out unless
        asked for: they are history, not models to offer.
        """

        with self._lock:
            discovered = self._discover()

            for stale_id in (
                set(self._metadata_cache) - set(discovered)
            ):
                del self._metadata_cache[stale_id]
```

The whole method runs under the lock.

- `discovered` is the current id → path mapping.
- `set(self._metadata_cache) - set(discovered)` is set subtraction: ids that have a cache entry but no file any more. Those entries are deleted, so the metadata cache cannot keep growing as history files come and go. (Turning a dict into a set gives the set of its keys.)

```python
            # Newest file first.
            ordered = sorted(
                discovered.items(),
                key=lambda item: item[1].stat().st_mtime_ns,
                reverse=True,
            )
```

`discovered.items()` yields `(model_id, path)` pairs. `sorted` orders them by the value the `key` function returns for each. `lambda item: ...` is a small unnamed function; `item[1]` is the path, and its modification time is the sort key. `reverse=True` puts the largest time, the most recently written file, first.

```python
            models = [
                metadata
                for model_id, path in ordered
                if (
                    metadata := self._metadata(
                        model_id, path
                    )
                )
                is not None
                and (
                    include_checkpoints
                    or metadata["kind"] == "model"
                )
            ]

            if not models:
                return []
```

One list comprehension does the filtering. For each `(model_id, path)`:

- `metadata := self._metadata(model_id, path)` calls `_metadata` and stores the result in `metadata` in the middle of the condition. This is the walrus operator (4.1). It lets the same value be tested and then used as the list item without calling the function twice.
- `is not None` drops unusable files.
- `include_checkpoints or metadata["kind"] == "model"` keeps everything when the caller asked for checkpoints, and only `kind == "model"` otherwise.

**Why per-epoch checkpoints are left out by default.** The default listing is what a client shows to someone choosing a model to talk to. Twenty-one near-identical snapshots would bury the one real model. The parameter exists for the cases where the history itself is the point, such as comparing epoch 1 with epoch 21.

If nothing survives the filter, the method returns an empty list here.

```python
            ids = [model["id"] for model in models]

            latest_id = (
                self.default_model_id
                if self.default_model_id in ids
                else ids[0]
            )
```

**Choosing the latest model.** Exactly one model in the list is flagged as `latest`:

- if the default id (`tiny_model.pt`) is among the listed ids, it is the latest, whatever its file time;
- otherwise the first id is, and because the list is ordered newest-first, that is the most recently written file.

So "latest" here means "the configured default if it is present, else the newest file". The default wins because it is the file training writes as its main result.

```python
            models = [
                {
                    **model,
                    "latest": model["id"] == latest_id,
                }
                for model in models
            ]

            models.sort(
                key=lambda model: not model["latest"]
            )

            return models
```

- `{**model, "latest": ...}` builds a *new* dict containing every entry of `model` plus one more. Making a new dict matters: `model` is the very object stored in `_metadata_cache`, and adding a key to it directly would write the `latest` flag into the cache, where it could be wrong the next time the listing is filtered differently.
- `model["id"] == latest_id` is `True` for one entry and `False` for the rest.
- The final `sort` uses the key `not model["latest"]`: `False` for the latest model, `True` for all others. `False` sorts before `True`, so the latest model moves to the front. Python's sort is *stable*, meaning items with equal keys keep their existing order, so the rest stay newest-first.

Real output of `GET /models` on the running server (default: no history files):

```text
{"models":[{"id":"tiny_model.pt","name":"tiny_model","display_name":"Tiny Model","kind":"model","parameters":884480,"trainable_parameters":884480,"epochs":21,"global_step":63,"tokens_seen":5418,"vocab_size":300,"context_length":128,"latest":true}]}
```

```python
    def latest_model_id(self) -> str | None:
        models = self.list_models()

        return models[0]["id"] if models else None
```

The id of the first entry of the default listing, or `None` when the listing is empty. Because it calls `list_models()` with no argument, per-epoch checkpoints are not candidates: a directory holding only history files has no latest model.

```python
    # --------------------------------------------------
    # Loading
    # --------------------------------------------------

    def tokenizer_for(self, model_id: str) -> Tokenizer:
        """
        Every checkpoint currently shares one tokenizer.

        Callers ask per model, so model-specific tokenizers
        can be added here later without touching them.
        """

        with self._lock:
            if self._tokenizer is None:
                if not self.tokenizer_path.is_file():
                    raise ModelLoadError(
                        f"Tokenizer not found: "
                        f"{self.tokenizer_path}"
                    )

                try:
                    self._tokenizer = Tokenizer.load(
                        self.tokenizer_path
                    )

                except Exception as error:
                    raise ModelLoadError(
                        f"Cannot load tokenizer: {error}"
                    ) from error

            return self._tokenizer
```

**Lazy loading** means "do the work the first time the result is needed, then keep it". `self._tokenizer` starts as `None`. The first call finds `None`, loads the file and stores the object; every later call skips the `if` and returns the stored object.

- The `model_id` parameter is not used in the body. As the docstring says, it is there so callers already ask "the tokenizer for this model", even though today the answer is the same for all of them.
- A missing file and a file that fails to parse both become `ModelLoadError`, so the server reports them the same way as an unusable checkpoint.
- The message for a missing file contains the full `tokenizer_path`.
- Unlike checkpoints, the tokenizer has no signature check. Once loaded it is used until the process ends, even if the file on disk is replaced.

```python
    def load(self, model_id: str) -> TinyLLM:
        """
        Return the loaded model, reading it from disk only
        when it is not cached or its file has changed.
        """

        with self._lock:
            path = self._discover().get(model_id)

            if path is None:
                raise UnknownModelError(model_id)

            signature = self._signature(path)

            cached = self._loaded.get(model_id)

            if cached is not None and cached[0] == signature:
                self._loaded.move_to_end(model_id)

                return cached[1]
```

`load()` is the method that produces a model ready to generate. Step by step:

1. **Take the lock.** Everything below happens with no other thread inside the manager, including the slow read from disk. A second request for a model that is still loading waits and then finds it in the cache.
2. **Resolve the id.** `self._discover().get(model_id)` is the lookup-in-the-mapping described above. `None` means no such file: raise `UnknownModelError`.
3. **Check the cache.** If the model is in `_loaded` with the same signature as the file has now, it is current. `move_to_end(model_id)` marks it as the most recently used, and the cached model (`cached[1]`) is returned. This is the fast path taken by almost every request.

If the model is not cached, or its file has changed since it was loaded, execution continues.

```python
            tokenizer = self.tokenizer_for(model_id)

            try:
                checkpoint = self._read_checkpoint(path)

                config = ModelConfig(
                    **checkpoint["config"]
                )

                if config.vocab_size != tokenizer.vocab_size:
                    raise ModelLoadError(
                        f"{model_id} expects vocab size "
                        f"{config.vocab_size}, tokenizer has "
                        f"{tokenizer.vocab_size}"
                    )
```

4. **Get the tokenizer.** This is where the lock is taken a second time by the same thread. It is called *before* the `try`, on purpose: if the tokenizer is missing, that is not this checkpoint's fault, so the error should pass straight out without marking the checkpoint unusable.
5. **Read and validate the checkpoint** with `_read_checkpoint`, then build the real `ModelConfig`.
6. **Vocab-size check.**

**What Python does** — Compares two integers and raises if they differ.

**What it means in the LLM** — The model's first layer is a table with one row per token id, and its last layer produces one score per token id (chapter 7). Both are sized by `config.vocab_size`. The tokenizer decides which ids exist. If the tokenizer has more ids than the model has rows, encoding a prompt can produce an id the model has no row for. If it has fewer, the model can produce an id the tokenizer cannot turn into bytes. And even when no crash happens, a tokenizer other than the one used in training gives the ids different meanings, so the output would be noise. Equal sizes do not prove it is the same tokenizer, but unequal sizes prove it is not.

```python
                model = TinyLLM(config)

                try:
                    model.load_state_dict(
                        checkpoint["model_state_dict"]
                    )

                except RuntimeError as error:
                    raise ModelLoadError(
                        f"{model_id} does not match the "
                        f"current model architecture: {error}"
                    ) from error

            except ModelLoadError:
                self._mark_unusable(model_id, signature)
                raise
```

7. **Build an empty model.** `TinyLLM(config)` creates the layers with freshly initialised random weights. At this moment it knows nothing.
8. **Fill in the weights.**

**What PyTorch does** — A *state dict* maps the name of every weight tensor (for example `embeddings.token_embedding.weight`) to its values; the real checkpoint has 53 entries. `load_state_dict` copies each saved tensor into the model's tensor of the same name. It insists on an exact fit: if a name is missing, an extra name is present, or a shape differs, it raises `RuntimeError`.

**What it means in the LLM** — This is the moment training's result enters the model. The exact-fit rule is the protection against **architecture mismatch**: if the code in `src/model` has changed since the checkpoint was saved (a layer renamed, added, or resized), the saved weights no longer describe the model the current code builds. The inner `try` turns that `RuntimeError` into a `ModelLoadError` with a message that says so.

9. **Handle any load failure in one place.** The outer `except ModelLoadError` catches all three sources: `_read_checkpoint`, the vocab-size check, and the architecture mismatch. It calls `_mark_unusable` so the model drops out of listings, then a bare `raise` re-raises the same exception unchanged for the caller.

```python
            model.to(self.device)
            model.eval()

            self._loaded[model_id] = (signature, model)
            self._loaded.move_to_end(model_id)

            while len(self._loaded) > self.max_loaded_models:
                self._loaded.popitem(last=False)

            return model
```

10. **`model.to(self.device)`** moves every weight to the serving device (`mps` on this machine). The checkpoint was read onto the CPU; generation should run where it is fastest.
11. **`model.eval()`** puts the model in evaluation mode (10.1). It is done once here so a cached model is always ready.
12. **Store it.** `self._loaded[model_id] = (signature, model)` adds or replaces the entry. If the model was being *re*loaded because its file changed, assigning to an existing key keeps the key's old position, so the following `move_to_end` is what makes it the most recent.
13. **Evict.**

**What Python does** — `popitem(last=False)` removes and returns the *first* item of an `OrderedDict`. A small example: with keys in the order `a, b, c`, `move_to_end("a")` gives `b, c, a`, and `popitem(last=False)` then removes `b`.

**What it means here** — Every use moves a model to the end, so the front of the dict is always the model that has gone longest without being used. Removing from the front until the size is within `max_loaded_models` is a **least-recently-used (LRU)** cache. The limit exists because each loaded model occupies memory on the device, and with 22 loadable files a client could otherwise make the server hold all of them. Removing the entry drops the cache's reference; Python frees the model once nothing else refers to it. A request that is in the middle of generating with that model still holds its own reference, so it finishes normally.

14. **Return the model.**

### 11.3 The server

| | |
|---|---|
| **INPUT** | HTTP requests from clients; the `ModelManager` class; `generate()`; directory constants from `paths.py`. |
| **PROCESS** | Define the request and response shapes, create the one `ModelManager` and the `FastAPI` app, register the routes, translate manager and generation failures into status codes, and attach the admin router and the static client apps. |
| **OUTPUT** | The module-level object `app`, which `uvicorn` serves. |
| **WHY IT EXISTS** | It is the HTTP layer: the only file that knows about methods, paths and status codes. It contains no model logic of its own. |

#### `src/serving/server.py`

**Why this file exists** — It wires the pieces together into a web application. Model handling is delegated to `model_manager.py`, generation to `generator.py`, admin endpoints to `admin.py`.

**What enters / what leaves** — Nothing is passed in: the file is a module that is imported. Importing it runs its top-level statements, which build `app`. It reads no files at import time. At request time it causes checkpoints and the tokenizer to be read (through the manager) and static files to be read from the client build directories.

**How it connects** — `scripts/serve.py` gives `uvicorn` the string `"src.serving.server:app"`, meaning "import the module `src.serving.server` and serve the object named `app`". This file imports from `paths.py`, `src/inference/generator.py`, `src/serving/admin.py`, `src/serving/model_manager.py` and `src/training/trainer.py`.

**The code, section by section**

```python
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
```

- `threading` — for the generation lock.
- `Path` — only as a type hint in `mount_app`.
- `FastAPI`, `HTTPException` — the application class and the "fail with this status code" exception (11.1).
- `HTMLResponse` — tells FastAPI that a route returns an HTML page instead of JSON. `RedirectResponse` — a response that sends the client to another URL.
- `StaticFiles` — a ready-made component that serves the files of a directory over HTTP.
- `BaseModel`, `Field` — pydantic's tools for describing request and response bodies (11.1).

```python
from paths import (
    ADMIN_CONSOLE_BUILD_DIR,
    CHAT_BUILD_DIR,
    CHECKPOINT_PATH,
    CHECKPOINTS_DIR,
    TOKENIZER_PATH,
    WEBSITE_BUILD_DIR,
)
from src.inference.generator import generate
from src.serving.admin import create_admin_router
from src.serving.model_manager import (
    ModelLoadError,
    ModelManager,
    UnknownModelError,
)
from src.training.trainer import get_device
```

- From `paths.py`: three directories where pre-built client apps may exist, the checkpoint directory, the path of the main checkpoint (`artifacts/checkpoints/tiny_model.pt`), and the tokenizer path.
- `generate` — the function from chapter 10.
- `create_admin_router` — builds the admin routes (11.4).
- `ModelManager` and its two exception types (11.2).
- `get_device` — the function from the training code (chapter 8) that returns `cuda` if available, otherwise `mps`, otherwise `cpu`. Serving reuses it so both stages pick a device the same way.

```python
class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    # Omitted -> the latest model.
    model: str | None = None
    max_new_tokens: int = Field(default=50, ge=1, le=2048)
    temperature: float = Field(default=0.0, ge=0.0, le=5.0)
```

The shape of the JSON body that `POST /generate` accepts.

| Field | Type | Required | Rule | Default |
|---|---|---|---|---|
| `prompt` | string | yes | at least 1 character | none |
| `model` | string or `null` | no | none | `None`, meaning "use the latest model" |
| `max_new_tokens` | integer | no | `1` to `2048` inclusive | `50` |
| `temperature` | number | no | `0.0` to `5.0` inclusive | `0.0` |

- `prompt` is required because its `Field` has no `default`.
- The limits are a safety boundary as much as a convenience. `max_new_tokens` decides how many times the model runs, so without `le=2048` a single request could keep the device busy for as long as it liked. `ge=0.0` on the temperature rules out negative values.
- The default temperature is `0.0`, so unless a client asks otherwise the server generates greedily and gives the same answer for the same prompt (10.1).

A real out-of-range request, `{"prompt":"hi","max_new_tokens":5000}`:

```text
HTTP 422
{"detail":[{"type":"less_than_equal","loc":["body","max_new_tokens"],"msg":"Input should be less than or equal to 2048","input":5000,"ctx":{"le":2048}}]}
```

That response was produced entirely by FastAPI and pydantic; no line of this project's handler ran.

```python
class GenerateResponse(BaseModel):
    model: str
    text: str
```

The shape of a successful answer: the id of the model that was actually used, and the text. Returning the id matters when the client left `model` out, because it tells the client which model "the latest" turned out to be.

```python
device = get_device()

model_manager = ModelManager(
    checkpoints_dir=CHECKPOINTS_DIR,
    tokenizer_path=TOKENIZER_PATH,
    default_model_id=CHECKPOINT_PATH.name,
    device=device,
)

# One generation at a time: the models share one device.
generation_lock = threading.Lock()
```

**Module-level setup.** These statements are not inside any function, so they run once, when the module is first imported, which is when `uvicorn` starts. Everything they create lives for the lifetime of the process and is shared by all requests.

- `device` — chosen once.
- `model_manager` — the single `ModelManager`. `CHECKPOINT_PATH.name` is `"tiny_model.pt"`: the manager is told the *file name* of the default model, not a path. `max_loaded_models` is not passed, so it is `4`. No model is loaded here; the constructor only stores settings, so the server starts quickly and the first request that needs a model pays for loading it.
- `generation_lock` — a plain `threading.Lock` (not re-entrant; it is taken in exactly one place and never nested).

**Why one generation runs at a time.** Route handlers run on several threads (11.1), so two `POST /generate` requests can arrive together. All loaded models sit on the same device, and that device has a fixed amount of memory and compute. Two generations running at once would compete for it and both would slow down, and on a GPU the combined memory use could exceed what is available. The lock makes the second request wait until the first has finished. The cost is that requests queue; a long generation delays every generation behind it. Requests that do not generate, such as `/health` and `/models`, do not take this lock and are still answered while a generation is in progress.

```python
app = FastAPI(
    title="JSM API",
    version="0.1.0",
    openapi_url="/api-schema.json",
)
```

The application object.

- `title` and `version` are labels that appear in the generated API description.
- FastAPI automatically builds a machine-readable description of every route and every request/response model, in a standard format called OpenAPI, and serves it as JSON. `openapi_url` sets the path of that document. FastAPI's own default is `/openapi.json`; this project serves it at `/api-schema.json` instead. Checked on the running server: `GET /api-schema.json` returns `200` and begins `{"openapi":"3.1.0","info":{"title":"JSM API","version":"0.1.0"},...`, while `GET /openapi.json` is not served by the API. The interactive documentation page that FastAPI provides at `/docs` reads its data from this URL and responds with `200`. The file does not say why the path was changed.

```python
@app.get("/health")
def health():
    return {
        "status": "ok",
        "device": str(device),
    }
```

`GET /health` is the cheapest possible request: it touches no model and no file. It answers one question, "is the process up and answering?", and also reports the device. `str(device)` turns the `torch.device` object into text such as `"mps"`, because a device object cannot be written as JSON. Real response:

```text
{"status":"ok","device":"mps"}
```

```python
@app.get("/models")
def list_models(
    include_checkpoints: bool = False,
):
    return {
        "models": model_manager.list_models(
            include_checkpoints=include_checkpoints,
        ),
    }
```

`GET /models` returns the manager's listing under the key `"models"`.

A function parameter that is a simple type and is not part of the path is read by FastAPI from the query string. So `include_checkpoints` is `False` for `/models`, and `True` for `/models?include_checkpoints=true`; FastAPI converts the text `true` to the Python value `True`. The value is passed straight to `ModelManager.list_models` (11.2).

On the running server the default listing has one entry (`tiny_model.pt`, shown in 11.2). With `?include_checkpoints=true` it has 22: the same entry first with `"latest":true`, followed by 21 per-epoch snapshots, newest first. The first two, trimmed:

```text
{"id":"tiny_model.pt", ... "kind":"model", ... "epochs":21,"global_step":63, ... "latest":true}
{"id":"checkpoint_epoch_000021_step_000000063.pt", ... "display_name":"Checkpoint Epoch 21 · Step 63","kind":"checkpoint", ... "latest":false}
```

```python
@app.post(
    "/generate",
    response_model=GenerateResponse,
)
def generate_text(
    request: GenerateRequest,
):
    model_id = (
        request.model
        or model_manager.latest_model_id()
    )

    if model_id is None:
        raise HTTPException(
            status_code=404,
            detail="No models found",
        )
```

`POST /generate` is the route the whole project leads up to.

- `response_model=GenerateResponse` declares the shape of a successful response; FastAPI checks the return value against it and documents it in the API description.
- `request: GenerateRequest` makes FastAPI parse and validate the JSON body before the function runs (11.1). Inside the function, `request.prompt`, `request.model` and so on are ordinary, already-checked Python values.
- `request.model or model_manager.latest_model_id()` — `or` returns its left side if that is "truthy", otherwise it evaluates and returns its right side. `None` and the empty string `""` are both falsy, so in either case the manager is asked for the latest model. When the client did name a model, the right side is never evaluated.
- If there is still no id, the checkpoint directory holds no usable model (or only per-epoch snapshots, see `latest_model_id` in 11.2): `404` with `"No models found"`.

```python
    try:
        model = model_manager.load(model_id)
        tokenizer = model_manager.tokenizer_for(model_id)

    except UnknownModelError:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown model: {model_id}",
        )

    except ModelLoadError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )
```

**The error mapping, part one: getting the model.** The manager speaks in its own two exceptions; this is where they are translated into HTTP.

| Raised by the manager | Status | `detail` | Reasoning |
|---|---|---|---|
| `UnknownModelError` | `404` | `Unknown model: <id>` | the thing the client named does not exist |
| `ModelLoadError` | `503` | the manager's message | the request was fine; a file on the server is unusable |

`str(error)` is the message the manager put into the exception, for example the vocab-size or architecture-mismatch text from 11.2. It is sent to the client as written.

The second line, `tokenizer_for(model_id)`, is nearly free at this point: `load()` has already loaded the tokenizer, so this returns the stored object.

A real `404`:

```text
POST /generate  {"prompt":"hi","model":"nope.pt"}

HTTP 404
{"detail":"Unknown model: nope.pt"}
```

```python
    try:
        with generation_lock:
            text = generate(
                model=model,
                tokenizer=tokenizer,
                prompt=request.prompt,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
            )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Generation failed: "
                f"{type(error).__name__}: {error}"
            ),
        )
```

**The generation lock in use.**

**What Python does** — `with generation_lock:` waits until no other thread holds the lock, takes it, runs `generate(...)`, and releases it when the block ends, whether it ended normally or with an exception.

**What it means for the service** — At most one call to `generate()` is running in the process at any moment. Note what is *outside* the lock: finding and loading the model happened earlier, under the manager's own lock. So a request can load its model while another request is generating, and then waits here for its turn.

**The error mapping, part two.** `except Exception` catches anything that goes wrong inside `generate()`, such as the device running out of memory. The client receives `500` with a `detail` naming the exception type (`type(error).__name__`) and its message. Without this block FastAPI would still answer `500`, but with a generic body; this version says what failed.

The two `try` blocks are deliberately separate. A failure to *obtain* a model is `404` or `503`; a failure *while generating* is `500`. An exception raised by `load()` that is neither of the manager's two types is not caught by either block and falls through to FastAPI's generic `500`.

```python
    return GenerateResponse(
        model=model_id,
        text=text,
    )
```

The success path. FastAPI converts the object to JSON, `{"model": "...", "text": "..."}`, with status `200`.

```python
app.include_router(
    create_admin_router(
        model_manager=model_manager,
        device=device,
    )
)
```

**The admin router.** `create_admin_router` (11.4) returns an `APIRouter` holding three routes under `/admin`. `include_router` copies those routes onto `app`. The router is given the *same* `model_manager` and `device` objects created above, so the admin endpoints see the same caches as the public ones and there is still only one manager in the process.

```python
# --------------------------------------------------
# Client apps
# --------------------------------------------------
# The apps are separate static builds under apps/.
# They are clients of the JSON API above and contain
# no model logic. They are mounted after the API
# routes, so an API route always wins.
```

The comment states the boundary. The client apps are folders of ready-made files that a browser downloads. They talk to the JSON routes above like any other client. This course does not cover them; the only thing that matters here is how the server hands the files out.

```python
def mount_app(
    route: str,
    build_dir: Path,
    name: str,
) -> None:
    if build_dir.is_dir():
        if route != "/":
            # "/chat" -> "/chat/", where the mount lives.
            app.add_api_route(
                route,
                lambda: RedirectResponse(route + "/"),
                include_in_schema=False,
            )

        app.mount(
            route,
            StaticFiles(
                directory=build_dir,
                html=True,
            ),
            name=name,
        )

        return
```

`mount_app` attaches one client app at one URL prefix. `route` is the prefix (`"/chat"`), `build_dir` is the directory that should contain the built files, and `name` is a label.

The first half handles the case where the build directory exists:

- **The redirect.** For any prefix other than `/`, a small extra route is registered for the exact path without a trailing slash. `app.add_api_route(path, function)` is the non-decorator way of registering a `GET` route. The function is a `lambda` that returns `RedirectResponse(route + "/")`. So a request for `/chat` is answered with "go to `/chat/`", as the code comment says. Checked on the running server: `GET /chat` returns `307` with the location `/chat/`. `include_in_schema=False` keeps this helper route out of the API description.
- **The mount.** `app.mount(route, StaticFiles(directory=build_dir, html=True), name=name)` hands every path below the prefix to `StaticFiles`, which looks for a matching file in `build_dir` and returns its contents. `html=True` makes a request for a directory return that directory's `index.html`. A *mount* differs from a route: a route matches one path pattern and calls one function, while a mount takes over a whole subtree of paths.
- `return` ends the function; the second half is not reached.

```python
    @app.get(
        route.rstrip("/") + "/",
        response_class=HTMLResponse,
        include_in_schema=False,
        name=name,
    )
    def app_not_built():
        return (
            f"<pre>JSM API is running, but the {name} app "
            f"is not built yet.\n\n"
            f"cd apps\nnpm install\nnpm run build\n\n"
            f"Then restart: python -m scripts.serve</pre>"
        )
```

**The "not built yet" fallback.** If the build directory does not exist, there is nothing to serve. Instead of leaving the URL as a bare `404`, a single route is registered at the prefix that returns a short page explaining the situation and how to build the app.

- `route.rstrip("/") + "/"` normalises the path to end in exactly one slash: `"/chat"` becomes `"/chat/"`, and `"/"` becomes `""` then `"/"`.
- `response_class=HTMLResponse` makes FastAPI send the returned string as an HTML page rather than as a JSON string.
- The decorator is used *inside* a function here. Each call to `mount_app` that reaches this point defines a new `app_not_built` function and registers it; the f-string picks up that call's `name`.
- The message ends with "Then restart", and that is literal: `mount_app` runs once at import time, so the decision between "serve files" and "show this message" is made when the server starts and does not change while it runs.

The API routes are unaffected either way. A server with no client apps built is still a complete JSON API.

```python
# TODO(security): /admin has no authentication on localhost.
# In production it MUST require authentication and
# authorization, like the /admin API routes.
mount_app("/admin", ADMIN_CONSOLE_BUILD_DIR, "admin console")
mount_app("/chat", CHAT_BUILD_DIR, "chat")

# Mounted last: "/" would otherwise shadow everything.
mount_app("/", WEBSITE_BUILD_DIR, "website")
```

Three calls, one per client app. The directories come from `paths.py`:

| Prefix | Constant | Directory (relative to the project) |
|---|---|---|
| `/admin` | `ADMIN_CONSOLE_BUILD_DIR` | `apps/internal/admin_console/web/out` |
| `/chat` | `CHAT_BUILD_DIR` | `apps/public/chat/web/out` |
| `/` | `WEBSITE_BUILD_DIR` | `apps/public/website/web/out` |

The `TODO(security)` comment records a known gap: anyone who can reach the server can open `/admin`. That is acceptable only because the server listens on `127.0.0.1`. The comment says that both the admin pages and the admin API routes must require a login (authentication) and a permission check (authorization) before this is ever exposed beyond the local machine. Neither exists today.

**Why mounts come after API routes.** When a request arrives, the app tries its routes and mounts in the order they were registered and uses the first one that matches. Two consequences:

- The mount at `/admin` matches every path under `/admin/`, including `/admin/overview`. The admin API routes were added by `include_router` earlier in the file, so they are tried first and win. Had the mount been registered first, `/admin/overview` would be looked up as a file.
- The mount at `/` matches every path there is. Registered last, it only receives requests that nothing else claimed. Registered first, it would swallow `/health`, `/models`, `/generate` and the rest, which is what the comment "would otherwise shadow everything" means.

### 11.4 The admin API

| | |
|---|---|
| **INPUT** | The shared `ModelManager` and device; `artifacts/runs/*/run.json`; the directory structure under `storage/`. |
| **PROCESS** | Count directories, files and lines; read the run records; ask the manager for the model list. |
| **OUTPUT** | Three `GET` endpoints under `/admin` that return JSON made of counts and metadata. |
| **WHY IT EXISTS** | To let you see the state of the whole pipeline (how much data is at each stage, which runs happened, which model is current) without opening the filesystem. |

#### `src/serving/admin.py`

**Why this file exists** — It is a read-only window onto the pipeline's outputs for an internal console. It changes nothing and returns no document text and no filesystem paths.

**What enters / what leaves** — `create_admin_router(model_manager, device)` returns an `APIRouter`. The helper functions take a `Path` and return a list or a number. Files read: `run.json` files under `artifacts/runs`, and the three dataset files under `storage/training/dataset` (only to count lines). Directories are listed but their files are not opened. Files written: none.

**How it connects** — `server.py` calls `create_admin_router` once and includes the result in `app`. The data it reports on was produced by every earlier stage: acquisition through dataset building (chapters 4 and 5) and training (chapter 8, which writes `run.json`).

**The code, section by section**

```python
import json
from pathlib import Path

import torch
from fastapi import APIRouter

from paths import (
    BATCHES_DIR,
    EXTRACTED_DIR,
    INSPECTIONS_CATALOG_DIR,
    PROCESSED_DIR,
    PROVENANCE_CATALOG_DIR,
    QUARANTINE_DIR,
    RAW_STORAGE_DIR,
    RUNS_DIR,
    TRAINING_DATA_DIR,
    UPLOADS_DIR,
)
from src.serving.model_manager import ModelManager
```

- `json` — to parse `run.json` files.
- `Path` — for the helpers' parameters and to cut a file name out of a stored path.
- `torch` — used only for the type hint `torch.device` in the factory's signature.
- `APIRouter` — a container for routes that is attached to the app later (11.1).
- Ten directory constants from `paths.py`, one for each place a pipeline stage keeps its output.
- `ModelManager` — for the type hint, and because the overview endpoint calls it.

```python
PROCESSING_STAGES = (
    "cleaned",
    "normalized",
    "filtered",
    "deduplicated",
)

DATASET_SPLITS = (
    "train",
    "validation",
    "test",
)
```

Two tuples of names. `PROCESSING_STAGES` are the four sub-directories of `storage/processed`, one per text-processing stage in pipeline order. `DATASET_SPLITS` are the three dataset files written by dataset building. Both are looped over in the data-summary endpoint.

```python
# --------------------------------------------------
# Read-only filesystem helpers
# --------------------------------------------------
# The Admin Console never sees a filesystem path.
# Everything it shows goes through the functions below.


def visible_entries(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []

    return [
        path
        for path in directory.iterdir()
        if not path.name.startswith(".")
    ]
```

The comment sets the rule for the file: clients receive numbers and names, never paths.

`visible_entries` returns the entries *directly* inside a directory, files and sub-directories alike, leaving out any whose name starts with a dot. Dot-names are hidden files by convention, such as `.DS_Store` on macOS or a `.gitkeep` placeholder; they are not pipeline data and would make the counts wrong. A directory that does not exist yields an empty list, so a stage that has never run counts as zero instead of raising an error.

```python
def count_directories(directory: Path) -> int:
    return sum(
        1
        for path in visible_entries(directory)
        if path.is_dir()
    )
```

How many of the visible entries are directories. `sum(1 for ... if ...)` is a common way to count: the generator expression produces a `1` for each item that passes the test, and `sum` adds them up. Only the top level is counted; nothing inside the sub-directories is looked at.

```python
def count_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0

    return sum(
        1
        for path in directory.rglob("*")
        if path.is_file()
        and not path.name.startswith(".")
    )
```

How many files exist anywhere below a directory. `rglob("*")` is the recursive version of `glob`: it yields every entry at every depth. An entry is counted when it is a file and its own name does not start with a dot. The dot test is applied to the file's name only, so a normal file inside a hidden *directory* is still counted.

```python
def count_lines(path: Path) -> int | None:
    if not path.is_file():
        return None

    with path.open("rb") as file:
        return sum(
            1
            for line in file
            if line.strip()
        )
```

How many non-blank lines a file has.

- If the file does not exist the result is `None`, not `0`. In the JSON that is `null` versus `0`, and they mean different things: "this file has not been created" versus "this file exists and is empty".
- `"rb"` opens the file as bytes. Looping over an open file yields one line at a time, so even a very large file is counted without being held in memory (streaming, chapter 5). Nothing needs to be decoded just to count.
- `line.strip()` removes whitespace, including the line ending; an empty result is falsy, so blank lines are not counted.

The dataset files are JSONL with one document per line (chapter 5), so for them this is a document count.

```python
def read_runs() -> list[dict]:
    """
    Training runs, newest first.

    Unreadable run.json files are skipped.
    """

    runs = []

    for run_dir in visible_entries(RUNS_DIR):
        run_path = run_dir / "run.json"

        if not run_path.is_file():
            continue

        try:
            metadata = json.loads(
                run_path.read_text(encoding="utf-8")
            )

        except (OSError, ValueError):
            continue

        if not isinstance(metadata, dict):
            continue
```

Training creates one directory per run under `artifacts/runs` and writes a `run.json` record into it (chapter 8). `read_runs` collects those records.

For each visible entry of the runs directory:

- build the path of its `run.json`; if there is no such file (including when the entry is itself a file rather than a directory), skip it;
- read and parse it. `OSError` covers "the file could not be read"; `ValueError` covers "the content is not valid JSON" (the JSON parser's own error type is a kind of `ValueError`, and so is a text-decoding error). Either way the run is skipped rather than failing the whole request;
- if the JSON parsed but is not an object (say, a list), skip it.

One damaged record therefore never hides the others.

```python
        checkpoint_path = metadata.get("checkpoint_path")

        runs.append(
            {
                "run_id": metadata.get(
                    "run_id", run_dir.name
                ),
                "status": metadata.get("status"),
                "started_at": metadata.get("started_at"),
                "finished_at": metadata.get("finished_at"),
                "device": metadata.get("device"),
                # File name only: absolute server paths
                # are not part of the API.
                "checkpoint": (
                    Path(checkpoint_path).name
                    if isinstance(checkpoint_path, str)
                    else None
                ),
                "model_config": metadata.get(
                    "model_config"
                ),
                "training_config": metadata.get(
                    "training_config"
                ),
                "training_stats": metadata.get(
                    "training_stats"
                ),
                "model_stats": metadata.get("model_stats"),
            }
        )
```

A new dict is built for each run by picking named fields out of the record. Because the output is assembled field by field, anything else that might be in `run.json` is not passed on.

- `metadata.get("run_id", run_dir.name)` — the second argument to `.get` is the fallback: if the record has no `run_id`, the directory's name is used.
- Every other field uses `.get(key)` and so becomes `None` when absent, the same tolerance for older records as in the model metadata (11.2).
- `model_config`, `training_config`, `training_stats` and `model_stats` are passed through as the nested objects they are.

**Why only the checkpoint file name is returned.** `run.json` stores `checkpoint_path`, the full path where the run saved its checkpoint. A full path reveals the machine's directory layout and the user account name, which a client has no need for and which should not leave the server. `Path(checkpoint_path).name` keeps only the last component: `Path("/a/b/tiny_model.pt").name` is `"tiny_model.pt"`. The response key is also renamed from `checkpoint_path` to `checkpoint`. The file name is still useful, because it is exactly the model id that `/models` and `/generate` use. The `isinstance(..., str)` test guards against a missing or malformed value, which becomes `None`.

```python
    runs.sort(
        key=lambda run: run["started_at"] or "",
        reverse=True,
    )

    return runs
```

The runs are sorted by start time, latest first. The timestamps are text such as `2026-10-05T08:25:50.004446Z`; because the format goes from the largest unit (year) to the smallest with fixed widths, sorting the strings alphabetically is the same as sorting by time. `run["started_at"] or ""` substitutes an empty string for a missing timestamp, so such a run sorts last instead of causing a comparison between `None` and a string.

```python
def create_admin_router(
    model_manager: ModelManager,
    device: torch.device,
) -> APIRouter:
    """
    Read-only JSON API for the internal Admin Console.

    TODO(security): there is no authentication yet because
    this only runs on localhost. In production every /admin
    route (these endpoints and the console pages) MUST
    require authentication and authorization.
    """

    router = APIRouter(
        prefix="/admin",
        tags=["admin"],
    )
```

**The router factory.** This is a function that builds and returns a router, rather than a router created at module level. The reason is the two parameters: the endpoints need the server's `model_manager` and `device`, and `admin.py` must not create its own. `server.py` owns those objects and passes them in. The endpoint functions are defined *inside* this function, so they can use `model_manager` and `device` directly; an inner function keeps access to the variables of the function that defined it (this is called a closure).

- `prefix="/admin"` is put in front of every path registered on the router, so `"/overview"` becomes `/admin/overview`.
- `tags=["admin"]` groups these routes under one heading in the API description.

**The security TODO.** The docstring repeats the note from `server.py`: there is no authentication. All three endpoints answer anyone who can connect. They expose training configuration, run history and data volumes, which is internal information. The docstring states the condition that makes this tolerable (the server only listens on the local machine) and the requirement before that changes (every `/admin` route, both these endpoints and the console pages, must require authentication and authorization). All three endpoints are `GET` and only read, so the exposure is of information, not of the ability to change anything.

```python
    @router.get("/overview")
    def overview():
        models = model_manager.list_models()
        runs = read_runs()

        return {
            "status": "ok",
            "device": str(device),
            "model_count": len(models),
            "latest_model": models[0] if models else None,
            "training_run_count": len(runs),
            "latest_training_run": (
                runs[0] if runs else None
            ),
        }
```

**`GET /admin/overview`** — a one-screen summary.

| Field | Exactly what it is |
|---|---|
| `status` | always the string `"ok"` |
| `device` | the serving device as text |
| `model_count` | the length of the default model listing: usable files of `kind` `"model"`. Per-epoch checkpoints and unusable files are not counted |
| `latest_model` | the first entry of that listing, which `list_models` guarantees is the one flagged `latest`; `None` if there are no models |
| `training_run_count` | the number of run directories with a readable `run.json` |
| `latest_training_run` | the run with the most recent `started_at`; `None` if there are none |

Real response on the running server, trimmed:

```text
{"status":"ok","device":"mps","model_count":1,
 "latest_model":{"id":"tiny_model.pt", ... "latest":true},
 "training_run_count":1,
 "latest_training_run":{"run_id":"run_20261005T082550Z_3079d15f","status":"completed",
   "started_at":"2026-10-05T08:25:50.004446Z","finished_at":"2026-10-05T08:26:06.937487Z",
   "device":"mps","checkpoint":"tiny_model.pt", ... }}
```

Note `model_count` is `1` although the checkpoint directory holds 22 files, and `checkpoint` is a bare file name.

```python
    @router.get("/training/runs")
    def training_runs():
        return {
            "runs": read_runs(),
        }
```

**`GET /admin/training/runs`** — the full list from `read_runs()`, newest first, under the key `"runs"`. The run records are read from disk on every request; there is no cache, so a run that finished a moment ago is visible immediately.

```python
    @router.get("/data/summary")
    def data_summary():
        return {
            "uploads": len(visible_entries(UPLOADS_DIR)),
            "upload_files": count_files(UPLOADS_DIR),
            "incoming_batches": count_directories(
                BATCHES_DIR
            ),
            "inspections": count_directories(
                INSPECTIONS_CATALOG_DIR
            ),
            "quarantined_batches": count_directories(
                QUARANTINE_DIR
            ),
            "provenance_decisions": count_directories(
                PROVENANCE_CATALOG_DIR
            ),
            "raw_batches": count_directories(
                RAW_STORAGE_DIR
            ),
            "extracted_batches": count_directories(
                EXTRACTED_DIR
            ),
```

**`GET /admin/data/summary`** — one number per pipeline location, in pipeline order. Each number is a count of filesystem entries, nothing more. No manifest is opened and no content is read.

| Field | Exactly what is counted |
|---|---|
| `uploads` | visible entries (files *and* directories) directly inside `storage/uploads` |
| `upload_files` | visible files at any depth below `storage/uploads` |
| `incoming_batches` | visible sub-directories of `storage/incoming/batches` |
| `inspections` | visible sub-directories of `storage/catalog/inspections` |
| `quarantined_batches` | visible sub-directories of `storage/quarantine` |
| `provenance_decisions` | visible sub-directories of `storage/catalog/provenance` |
| `raw_batches` | visible sub-directories of `storage/raw` |
| `extracted_batches` | visible sub-directories of `storage/extracted` |

The field names say what a sub-directory *represents* at that stage (a batch, an inspection, a decision; see chapter 4). The code itself only counts directories and trusts that layout.

The first two differ in a way worth seeing. On the running server `uploads` is `19` and `upload_files` is `33`: the uploads directory has 19 things at its top level (13 loose files and 6 folders), and 33 files in total once the folders' contents are included.

```python
            "processed_batches": {
                stage: count_directories(
                    PROCESSED_DIR / stage
                )
                for stage in PROCESSING_STAGES
            },
            "dataset_documents": {
                split: count_lines(
                    TRAINING_DATA_DIR
                    / "dataset"
                    / f"{split}.jsonl"
                )
                for split in DATASET_SPLITS
            },
        }

    return router
```

The last two fields are dict comprehensions, each producing a nested object.

| Field | Exactly what is counted |
|---|---|
| `processed_batches` | for each of `cleaned`, `normalized`, `filtered`, `deduplicated`: visible sub-directories of `storage/processed/<stage>` |
| `dataset_documents` | for each of `train`, `validation`, `test`: non-blank lines of `storage/training/dataset/<split>.jsonl`, or `null` if that file does not exist |

Comparing the four `processed_batches` numbers shows at a glance whether every batch has made it through every processing stage.

The complete real response:

```text
{"uploads":19,"upload_files":33,"incoming_batches":8,"inspections":15,"quarantined_batches":2,
 "provenance_decisions":2,"raw_batches":1,"extracted_batches":1,
 "processed_batches":{"cleaned":1,"normalized":1,"filtered":1,"deduplicated":1},
 "dataset_documents":{"train":1,"validation":0,"test":0}}
```

`"validation":0` and `"test":0` are zeros, not `null`: those two files exist and contain no documents.

`return router` hands the router, now holding its three routes, back to `server.py`.

### 11.5 One request, end to end

The request from 11.1, followed through every function it touches. It names no model, so the server chooses.

```text
POST /generate
{"prompt":"hi","max_new_tokens":12}
```

**1. `uvicorn` and FastAPI.** `uvicorn`, started by `scripts/serve.py`, receives the bytes on port `8000` and passes the request to `app`. FastAPI goes through its routes in registration order and matches `POST /generate` to `generate_text` in `server.py`.

**2. Validation — `GenerateRequest`.** FastAPI parses the body into a `GenerateRequest`. `prompt` is `"hi"` (length 2, passes `min_length=1`). `max_new_tokens` is `12` (within `1`–`2048`). `model` is absent, so `None`. `temperature` is absent, so `0.0`. Had any check failed, the client would get `422` now and nothing below would run.

**3. `generate_text` begins.** It runs on a worker thread. `request.model` is `None`, so the right side of the `or` runs.

**4. `ModelManager.latest_model_id` → `list_models`.** Under the manager's lock: `_discover` lists the 22 `.pt` files. Stale cache entries are removed. The files are sorted newest first. `_metadata` is called for each; for a file seen before with an unchanged `_signature`, the cached dict is returned without reading the file. Per-epoch checkpoints are filtered out (`kind == "checkpoint"`), leaving one entry. The default id `tiny_model.pt` is among the ids, so it is flagged `latest` and sorted to the front. `latest_model_id` returns `"tiny_model.pt"`.

**5. `ModelManager.load("tiny_model.pt")`.** Under the lock: `_discover` again, and the id is found in the mapping. `_signature` is computed.

- *If this model was used before and the file is unchanged:* it is in `_loaded` with a matching signature; `move_to_end` marks it most recent and the model is returned. No disk read.
- *If this is the first use since the server started:* `tokenizer_for` loads `artifacts/tokenizer/tokenizer.json` (once). `_read_checkpoint` runs `torch.load(..., weights_only=True)` and checks the shape. `ModelConfig` is built. The vocab sizes are compared (`300` and `300`). `TinyLLM(config)` is created and `load_state_dict` fills its 53 weight tensors. `model.to(device)` moves it to `mps`, `model.eval()` is set, the model is stored in `_loaded`, and the eviction loop finds 1 entry against a limit of 4 and removes nothing.

**6. `ModelManager.tokenizer_for("tiny_model.pt")`.** Returns the already-loaded tokenizer.

Neither call raised, so both `except` branches in `generate_text` are skipped.

**7. The generation lock.** `with generation_lock:` — if another request is generating, this thread waits here. Then it calls `generate(model, tokenizer, prompt="hi", max_new_tokens=12, temperature=0.0)`.

**8. `generate` in `src/inference/generator.py`.**

- `model.eval()`; the device is read from the model's first parameter.
- `tokenizer.encode("hi", add_bos=True, add_eos=False)` gives `[256, 104, 105]`; `tokens_to_bytes` gives `b"hi"`.
- The loop runs up to 12 times. Each time: slice the last 128 ids; build a `[1, T]` tensor on `mps`; run the model to get `[1, T, 300]` scores; take `logits[0, -1]`; `apply_utf8_constraint` checks all 300 candidates using `is_complete_utf8` (for EOS) and `is_valid_utf8_prefix` (for the rest) and masks the illegal ones; because the temperature is `0.0`, `torch.argmax` picks the highest remaining score; the id is appended; if it is EOS the loop ends, otherwise its bytes are added to `current_bytes`.
- After the loop, the `while not is_complete_utf8(...)` cleanup removes any unfinished character, and `tokenizer.decode(..., errors="strict")` returns the string.

**9. Back in `generate_text`.** The `with` block ends and the generation lock is released. No exception, so the `500` branch is skipped. The function returns `GenerateResponse(model="tiny_model.pt", text=...)`.

**10. The response.** FastAPI checks the object against `response_model`, converts it to JSON and sends status `200`:

```text
{"model":"tiny_model.pt","text":"hiع، مجياتج "}
```

The `model` field tells the client which model "the latest" resolved to. The `text` field starts with the prompt, because `generate()` returns prompt plus continuation (10.1). Sending the same request again returns the same text, since temperature `0.0` is greedy.

The same route with a per-epoch snapshot named explicitly also works, even though that file is hidden from the default listing: `{"prompt":"hi","model":"checkpoint_epoch_000001_step_000000003.pt","max_new_tokens":12}` returns `200` with that id in `model` (and, after one epoch of training, random-looking text). Listing filters by `kind`; `load()` does not.

#### What I should understand before moving on

- Serving keeps the model in a process that stays alive, so the cost of loading is paid once and each request only pays for generation.
- `server.py` knows HTTP and nothing about checkpoints; `model_manager.py` knows checkpoints and nothing about HTTP. The two custom exceptions are the bridge: `UnknownModelError` → `404`, `ModelLoadError` → `503`, and a failure during generation → `500`.
- A model id from a client is never turned into a path. It is looked up among the names of files that really exist in the checkpoint directory, which is what makes path traversal impossible.
- `weights_only=True` exists because a `.pt` file is a pickle, and a pickle can carry code that runs when it is loaded.
- Both caches are keyed by model id and guarded by a file signature (modification time and size). Metadata is cached for every file, including "unusable"; loaded models are kept for at most four ids, least recently used evicted first.
- There are two locks with two jobs. The manager's `RLock` protects the caches and makes loading happen once. The server's `generation_lock` lets only one `generate()` run at a time because all models share one device.
- Pydantic rejects malformed requests with `422` before any project code runs; the `Field` limits are also what bounds how much work one request can demand.
- The admin endpoints are read-only and return counts, names and run metadata, never paths or document text. They have no authentication, which is acceptable only while the server listens on `127.0.0.1`.

#### Self-test

1. A client sends `{"prompt":"hi","model":"../../secret.pt"}`. Describe exactly which line stops this and why no file outside the checkpoint directory is ever opened.
2. You retrain, and training overwrites `tiny_model.pt` while the server is running. Without restarting the server, will the next `/generate` use the old weights or the new ones? Which mechanism decides?
3. Why is the manager's lock an `RLock` while the server's generation lock is a plain `Lock`?
4. `GET /models` shows one model but `GET /models?include_checkpoints=true` shows 22. Can a client still generate with one of the 21 hidden ones? What does that tell you about where the filtering happens?
5. A checkpoint reads fine and shows up in `/models`, but the model code has changed since it was saved. What happens on the first `/generate` that names it, what status code does the client see, and what is different about `/models` afterwards?
6. Five different models are requested one after another, then the first one is requested again. Is it loaded from disk a second time? Explain using the `OrderedDict`.
7. In `/admin/data/summary`, `uploads` is `19` and `upload_files` is `33`. Both look at the same directory. What does each count, and what would make them equal?
8. Why must `mount_app("/", ...)` be the last registration in `server.py`, and what would `GET /health` return if it were the first?

<details><summary>Answers</summary>

1. `path = self._discover().get(model_id)` in `ModelManager.load`. `_discover` builds a dict whose keys are the names of the regular, non-symlink `.pt` files directly inside the checkpoint directory. The client's string is used only as a key into that dict. `"../../secret.pt"` is not the name of any file there, so `.get` returns `None`, `UnknownModelError` is raised and the server answers `404`. The id is never joined to a directory, so it cannot steer a file open.
2. The new ones. `load()` computes the file's current signature (modification time and size) and compares it with the one stored beside the cached model. Overwriting the file changes the signature, the cache entry is treated as out of date, and the checkpoint is read again. (The tokenizer is different: it has no signature check and is not reloaded.)
3. `load()` holds the manager's lock and calls `tokenizer_for()`, which takes the same lock again on the same thread; a plain lock would block forever at that point, while a re-entrant lock allows it. The generation lock is taken in one place only and nothing inside that block tries to take it again, so the simple kind is enough.
4. Yes. `load()` accepts any id present in `_discover()` and never looks at `kind`. The filtering is in `list_models` only, so it is a presentation choice about what to *offer*, not an access rule.
5. `load()` builds a `TinyLLM` from the current code and `load_state_dict` raises `RuntimeError` because names or shapes do not fit. That is converted to `ModelLoadError`, `_mark_unusable` records `None` for that id and signature, and the server responds `503` with the mismatch message. Afterwards `/models` no longer lists it, because its cached metadata is now `None`, until the file changes.
6. Yes, it is loaded again. Each load appends to the end of `_loaded`. After the fifth model there are five entries against a limit of four, so `popitem(last=False)` removes the front one, which is the first model, the least recently used. Requesting it again finds no cache entry.
7. `uploads` counts visible entries at the top level of `storage/uploads`, where a folder counts as one. `upload_files` counts visible files at every depth. They are equal when the directory contains only loose files and no folders (or when folders happen to hold exactly one file each).
8. Routes and mounts are tried in registration order and the first match wins. A mount at `/` matches every path. Registered first, it would receive `GET /health` and look for a file called `health` in the website's build directory; finding none, the client would get `404` instead of the health JSON.

</details>

---

## 12. Scripts — what each command runs

| | |
|---|---|
| **INPUT** | A command you type in the project directory, such as `python -m scripts.cleaning`, plus whatever the previous command left on disk under `storage/` or `artifacts/`. Four scripts also read command-line arguments. |
| **PROCESS** | Each file under `scripts/` imports a few functions from `src/`, decides which directories and files to loop over, calls those functions, writes the results to the next directory, and prints one line per thing it handled. |
| **OUTPUT** | Files in the next stage's directory (see the table below) and progress lines in the terminal. Three scripts (`evaluate`, `inference`, `model_stats`) only print; `provenance` only prints; `serve` starts a web server. |
| **WHY IT EXISTS** | The functions in `src/` take values and return values; most of them do not know where anything lives. Something has to say "read from here, write to there, in this order". That is the job of these eighteen files, and they are the only files you run directly. |

**Why entry points are kept apart from logic.** A function such as `clean_text(text)` (4.6) receives a string and returns a string. It never opens a file. That makes it easy to reason about and to reuse: the same function could clean a string that came from a web request. The decision "clean every `.txt` under `storage/extracted/` and write it under `storage/processed/cleaned/`" is a different kind of decision — it is about *this* project's folders — so it lives in `scripts/cleaning.py`. The rule of thumb across the project: `src/` answers "how is one thing transformed?", `scripts/` answers "which things, from where, to where?". The rule is not perfectly followed: several scripts contain real logic (choosing which inspection is the latest, deduplicating across batches, counting training steps), and some `src/` functions do know their own output directory (`acquire_batch`, `ingest_artifact`, `write_rights_decision`). Both cases are pointed out below.

**How a script is started.** Every command has the form `python -m scripts.<name>`. The `-m` flag tells Python to find the module `scripts.<name>` and run it as the main program, which makes the `if __name__ == "__main__":` block at the bottom execute (see the primer in 1). It also puts the current directory on Python's import path, and that is why all of these commands must be typed **from the project directory** (the one that contains `paths.py`): every script begins with `from paths import ...` and `from src... import ...`, and those imports only resolve when the current directory is the project root. There is no `scripts/__init__.py` and no `src/__init__.py`; Python treats a directory without one as a "namespace package", which is enough for `-m` to work.

**Where the paths come from.** No script spells out a directory as a string from the project root. They import constants from `paths.py`, which builds everything from `PROJECT_DIR = Path(__file__).resolve().parent`. The constants used in this chapter are:

| Constant | Directory or file (relative to the project) |
|---|---|
| `UPLOADS_DIR` | `storage/uploads` |
| `BATCHES_DIR` | `storage/incoming/batches` |
| `QUARANTINE_DIR` | `storage/quarantine` |
| `INSPECTIONS_CATALOG_DIR` | `storage/catalog/inspections` |
| `PROVENANCE_CATALOG_DIR` | `storage/catalog/provenance` |
| `RAW_STORAGE_DIR` | `storage/raw` |
| `EXTRACTED_DIR` | `storage/extracted` |
| `PROCESSED_DIR` | `storage/processed` |
| `TRAINING_DATA_DIR` | `storage/training` |
| `TOKENIZER_PATH` | `artifacts/tokenizer/tokenizer.json` |
| `CHECKPOINT_PATH` | `artifacts/checkpoints/tiny_model.pt` |
| `RUNS_DIR` | `artifacts/runs` |

Four stage directories are *not* in `paths.py`; the scripts build them themselves by joining a name onto `PROCESSED_DIR` or `TRAINING_DATA_DIR`: `cleaned`, `normalized`, `filtered`, `deduplicated`, `dataset`, `tokenized`. Each of those names is typed in two or more scripts (for example `PROCESSED_DIR / "cleaned"` appears in both `cleaning.py` and `normalization.py`), so the link between "what stage N writes" and "what stage N+1 reads" is held together only by the two strings being identical.

**All commands, in run order.** `<batch>` stands for a batch id such as `my-source-20260101T120000Z-0a1b2c3d`, `<doc>` for a document id such as `doc_0123…cdef` (the prefix `doc_` followed by 32 hexadecimal characters).

| # | Command | Reads | Writes |
|---|---|---|---|
| 1 | `python -m scripts.acquisition` | `storage/uploads/` (folders, loose files, optional `origin.json`); existing `storage/incoming/batches/*/source.json` | `storage/incoming/batches/<batch>/objects/<nnnnnnnn>-<name>`, `source.json`, `source.json.sha256` |
| 2 | `python -m scripts.inspection [batch_id] [--latest] [--policy FILE]` | `configs/inspection.json`; `storage/incoming/batches/<batch>/`; existing inspection and quarantine records | `storage/catalog/inspections/inspection_<stamp>_<hex>/manifest.json` + `.sha256`; when anything is not accepted, `storage/quarantine/<batch>/inspection_<…>/quarantine.json` + `.sha256` |
| 3 | `python -m scripts.provenance` | `storage/catalog/inspections/*/manifest.json`; `storage/incoming/batches/<batch>/source.json`; `storage/catalog/provenance/*/manifest.json` | nothing (prints `ALLOW` / `BLOCK` / `SKIP`) |
| 4 | `python -m scripts.provenance_review <batch-id> <allowed\|denied\|review_required> <basis>` | its three arguments | `storage/catalog/provenance/provenance_<stamp>_<hex8>/manifest.json` + `.sha256` |
| 5 | `python -m scripts.ingestion` | the same three places as command 3, plus the accepted files in `storage/incoming/batches/<batch>/objects/` | `storage/raw/<batch>/objects/<doc>-<nnnnnnnn>-<name>`, `storage/raw/<batch>/manifest.json` + `.sha256` |
| 6 | `python -m scripts.extraction` | `storage/raw/<batch>/manifest.json` and the files it lists | `storage/extracted/<batch>/<doc>.txt` |
| 7 | `python -m scripts.cleaning` | `storage/extracted/<batch>/*.txt` | `storage/processed/cleaned/<batch>/<doc>.txt` |
| 8 | `python -m scripts.normalization` | `storage/processed/cleaned/<batch>/*.txt` | `storage/processed/normalized/<batch>/<doc>.txt` |
| 9 | `python -m scripts.filtering` | `storage/processed/normalized/<batch>/*.txt` | `storage/processed/filtered/<batch>/<doc>.txt` (accepted documents only) |
| 10 | `python -m scripts.deduplication` | `storage/processed/filtered/<batch>/*.txt` | `storage/processed/deduplicated/<batch>/<doc>.txt` (first copy of each text only) |
| 11 | `python -m scripts.dataset_building` | `storage/processed/deduplicated/<batch>/*.txt` | `storage/training/dataset/train.jsonl`, `validation.jsonl`, `test.jsonl` |
| 12 | `python -m scripts.tokenizer_training` | `storage/training/dataset/train.jsonl` | `artifacts/tokenizer/tokenizer.json` |
| 13 | `python -m scripts.tokenize_dataset` | `artifacts/tokenizer/tokenizer.json`; `storage/training/dataset/{train,validation,test}.jsonl` | `storage/training/tokenized/{train,validation,test}.jsonl` |
| 14 | `python -m scripts.train` | `configs/training.json`; `storage/training/tokenized/train.jsonl` and `validation.jsonl`; `artifacts/checkpoints/tiny_model.pt` if it exists | `artifacts/checkpoints/tiny_model.pt`, `checkpoint_epoch_<e>_step_<s>.pt`, possibly `best_tiny_model.pt`; `artifacts/runs/run_<stamp>_<hex8>/run.json` |
| 15 | `python -m scripts.evaluate` | `artifacts/checkpoints/tiny_model.pt`; `storage/training/tokenized/{train,validation,test}.jsonl` | nothing (prints loss and perplexity) |
| 16 | `python -m scripts.inference [prompt words…]` | `artifacts/checkpoints/tiny_model.pt`; `artifacts/tokenizer/tokenizer.json` | nothing (prints generated text) |
| 17 | `python -m scripts.model_stats` | the checkpoint, the tokenizer, `storage/training/tokenized/train.jsonl` | nothing (prints a statistics table) |
| 18 | `python -m scripts.serve` | `artifacts/checkpoints/`, the tokenizer, built web apps under `apps/` | nothing on disk (serves HTTP on `127.0.0.1:8000` until stopped) |

The directory `scripts/` contains exactly these eighteen `.py` files, the author's notes file `scripts/README.md` (checked in 12.19), and Python's own `__pycache__/` folder.

A pattern to notice before reading the individual files: commands 6–11 are *file-in, file-out* loops with the same skeleton (list batch folders → make the matching output folder → loop over `*.txt` → transform → write → print). Once you have read `cleaning.py` closely, the next three differ by a handful of lines, and those lines are where the attention should go.

---

### 12.1 `python -m scripts.acquisition`

#### `scripts/acquisition.py`

**Command.** No arguments.

```
python -m scripts.acquisition
```

**Why this file exists.** It turns "whatever is sitting in `storage/uploads/`" into immutable, hashed batches — once per distinct set of files. The copying and manifest writing are library code (4.1); what the script adds is the *loop over sources* and the *"have I already taken this?"* check.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/uploads/` must exist and contain at least one non-hidden file. Nothing earlier in the pipeline produces it — you put files there. |
| Reads | Every file under `storage/uploads/`; each existing `storage/incoming/batches/*/source.json`. |
| Writes | For each new source, one new directory `storage/incoming/batches/<batch>/` containing `objects/<nnnnnnnn>-<original name>` (one per file), `source.json`, `source.json.sha256`. |
| Prints | `Acquired: <source name> -> <batch id>` or `Skipped already acquired source: <source name>`, one line per source. |

**How it connects.** First command of the pipeline. Its batches are what `scripts.inspection` (12.2) inspects next.

**The code, section by section.**

```python
from paths import UPLOADS_DIR, BATCHES_DIR

from src.corpus_factory.acquisition.intake import read_uploads
from src.corpus_factory.acquisition.batch import acquire_batch
from src.corpus_factory.acquisition.discovery import existing_fingerprints
from src.corpus_factory.acquisition.hashing import sha256_file
```

Two path constants and four library functions, all explained in 4.1:

- `read_uploads(root)` returns a list of `IntakeSource` objects. Each sub-folder of `uploads/` that contains files becomes one source (its `name` is the folder name, its `origin` is the parsed `origin.json` if one exists, otherwise `{}`); files lying directly in `uploads/` are grouped into one extra source named `unattributed`.
- `existing_fingerprints(batches_dir)` reads every already-written `source.json` and returns a set of `(platform, sorted hashes)` tuples.
- `sha256_file(path)` returns the SHA-256 hex digest of one file, read in chunks.
- `acquire_batch(source)` creates the batch directory, copies each file while hashing it, and writes `source.json` plus its checksum; it returns the batch directory.

```python
if __name__ == "__main__":
    sources = read_uploads(UPLOADS_DIR)

    if not sources:
        raise ValueError(f"No files found under {UPLOADS_DIR}")

    existing = existing_fingerprints(BATCHES_DIR)
```

`read_uploads` itself raises `ValueError("Uploads directory not found: …")` when the directory is missing. The script adds a second guard: an existing but empty uploads directory gives an empty list, and `if not sources` turns that into an error too. So "nothing to do" is treated as a mistake here, not as a quiet success — unlike most later scripts.

`existing` is computed **once**, before the loop. It is the script's memory of what has been acquired in previous runs.

```python
    for source in sources:
        platform = source.origin.get(
            "platform",
            source.name,
        )

        current_hashes = tuple(
            sorted(
                sha256_file(path)
                for path in source.files
            )
        )

        fingerprint = (
            platform,
            current_hashes,
        )
```

For each source the script builds a **fingerprint**: a tuple of two things.

- `platform` — `source.origin.get("platform", source.name)`: the `platform` value from `origin.json` if there is one, otherwise the folder name. `dict.get(key, default)` returns the default instead of raising when the key is absent.
- `current_hashes` — the SHA-256 of every file in the source, sorted, frozen into a tuple.

**What Python does.** `sha256_file(path) for path in source.files` is a generator expression (primer in 1) producing one hex string per file; `sorted(...)` puts them in alphabetical order; `tuple(...)` makes the result immutable so it can be stored in a set and compared with `==`. Sorting matters: without it, the same files listed in a different order would look like a different source.

**What it means in the pipeline.** The fingerprint is the identity of "this set of content from this origin". File names and dates play no part. Rename a file without changing its bytes and the fingerprint is unchanged; change one byte, or add or remove one file, and it is a different fingerprint. `existing_fingerprints` builds the same shape from disk (`source.platform` and the `sha256` of each artifact in `source.json`), so the two can be compared directly.

Note the cost: every file is read once here to compute the fingerprint, and — if the source is new — read a second time inside `acquire_batch`, which hashes while it copies.

```python
        if fingerprint in existing:
            print(
                f"Skipped already acquired source: "
                f"{source.name}"
            )
            continue

        batch_dir = acquire_batch(source)

        print(
            f"Acquired: {source.name} -> "
            f"{batch_dir.name}"
        )
```

`fingerprint in existing` is a set membership test. If the fingerprint is already there, the script prints the "Skipped" line and `continue` jumps to the next source. Otherwise `acquire_batch(source)` does the real work and the script prints the source name and the new batch directory's name (`batch_dir.name` is the last path component, i.e. the batch id).

**Running it twice.** Safe. A second run with unchanged uploads prints only "Skipped" lines and writes nothing. If you add one file to an already-acquired folder, the fingerprint of that folder changes, so the **whole folder** is acquired again as a new batch; the old batch stays, and both now contain copies of the old files. (Exact-duplicate documents are removed much later, in 12.10.) Inside a batch, files are created in exclusive mode (`"xb"`, 4.1) and the batch directory is made with `exist_ok=False`, so nothing existing can be overwritten.

Two smaller points that follow from the code: `existing` is not updated inside the loop, so the check only protects against *earlier runs*, not against two identical sources in the same run (they would need the same `platform` and the same files to collide); and if the script is interrupted while copying, the half-written batch directory has no `source.json`, so it leaves no fingerprint, and the next run acquires the source again into a fresh batch while the incomplete directory stays on disk.

**Empty or missing input.** Missing `storage/uploads/` → `ValueError` from `read_uploads`. Present but empty (or only hidden files) → `ValueError: No files found under …` from the script. A missing `storage/incoming/batches/` is fine: `existing_fingerprints` returns an empty set and `acquire_batch` creates the directory.

---

### 12.2 `python -m scripts.inspection`

#### `scripts/inspection.py`

**Command.** This is the only script that uses `argparse`, Python's standard argument parser. This is its real help text:

```
usage: inspection.py [-h] [--latest] [--policy POLICY] [batch_id]

Inspect pending batches, or explicitly re-inspect one batch.

positional arguments:
  batch_id

options:
  -h, --help       show this help message and exit
  --latest         re-inspect the most recently acquired batch
  --policy POLICY
```

| Invocation | Meaning |
|---|---|
| `python -m scripts.inspection` | Inspect every batch that does not yet have a valid inspection record under the current policy ("pending" batches). |
| `python -m scripts.inspection my-source-20260101T120000Z-0a1b2c3d` | Inspect exactly that batch again, whether or not it was inspected before. |
| `python -m scripts.inspection --latest` | Inspect again the batch whose directory was modified most recently. |
| `… --policy some/other.json` | Use a different policy file instead of `configs/inspection.json`. Can be combined with any of the above. |

**Why this file exists.** The inspector (4.2) inspects *one* batch and returns a result object. Deciding *which* batches to inspect, writing the report, and writing the quarantine record are three separate library calls that someone has to chain together; this file does that, and it holds the "which batches?" logic.

**What enters / what leaves.**

| | |
|---|---|
| Needs | Batches from 12.1; `configs/inspection.json`. |
| Reads | The policy file; each selected batch (its `source.json`, checksum and objects); for the default mode, all existing inspection records and the quarantine records they point to. |
| Writes | Per inspected batch: `storage/catalog/inspections/inspection_<stamp>_<hex>/manifest.json` and `manifest.json.sha256`. If any artifact is not accepted, or the batch itself is invalid: `storage/quarantine/<batch>/inspection_<…>/quarantine.json` and `.sha256`. The batch itself is never modified or moved. |
| Prints | Per batch: `<batch>: accepted=… quarantined=… rejected=…`, then indented lines for batch-level errors, the report path, and the quarantine path if one was written. Or one line: `No pending batches. …`. |

**How it connects.** Reads what acquisition wrote. Its `manifest.json` records are what `scripts.provenance` (12.3) lists and what `scripts.ingestion` (12.5) uses to decide which files to copy.

**The code, section by section.**

```python
"""Inspect pending batches, or explicitly re-inspect one batch."""
import argparse

from paths import BATCHES_DIR
from src.corpus_factory.inspection.config import INSPECTION_CONFIG_PATH, load_inspection_config
from src.corpus_factory.inspection.inspector import inspect_batch
from src.corpus_factory.inspection.quarantine import quarantine_batch
from src.corpus_factory.inspection.report import completed_batches, write_inspection_report
```

Line 1 is a *docstring*: a string placed first in a file. Python stores it in the variable `__doc__`, and line 12 reuses it as the help text — that is the "Inspect pending batches…" sentence in the output above.

The imports, each explained in 4.2:

- `INSPECTION_CONFIG_PATH` is `configs/inspection.json`; `load_inspection_config(path)` reads and validates it and returns a dict (it raises `ValueError` if the file is unreadable or any setting is wrong).
- `inspect_batch(batch_dir, policy)` verifies the batch manifest, runs every check on every artifact, and returns an `InspectionResult`.
- `write_inspection_report(batch_dir, result)` publishes the result as a new, checksummed record directory and returns the path of its `manifest.json`.
- `quarantine_batch(batch_dir, result, inspection_id)` writes a record that *references* the non-accepted artifacts (it copies nothing) and returns its path, or `None` when there is nothing to quarantine.
- `completed_batches(policy)` returns the set of batch paths that already have a trustworthy inspection record made with exactly this policy.

```python
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch_id', nargs='?')
    parser.add_argument('--latest', action='store_true', help='re-inspect the most recently acquired batch')
    parser.add_argument('--policy', type=type(INSPECTION_CONFIG_PATH), default=INSPECTION_CONFIG_PATH)
    args = parser.parse_args()
    if args.batch_id and args.latest:
        parser.error('choose a batch ID or --latest')
```

Unlike the other scripts, the work is wrapped in a function `main()` so that it can `return` an exit code.

- `parser.add_argument('batch_id', nargs='?')` — a positional argument; `nargs='?'` means "zero or one", so it is optional and is `None` when omitted.
- `--latest` with `action='store_true'` — a flag with no value; `args.latest` is `True` if it was typed, else `False`.
- `--policy` with `type=type(INSPECTION_CONFIG_PATH)` — `type(x)` returns the class of `x`. `INSPECTION_CONFIG_PATH` is a `Path` object (on macOS its concrete class is `PosixPath`), so this tells argparse "convert the typed string into the same kind of path object". The default is the standard policy file.
- `parser.parse_args()` reads `sys.argv` for you and returns an object with attributes `batch_id`, `latest`, `policy`.
- Giving both a batch id and `--latest` is contradictory; `parser.error(...)` prints the usage line and the message and exits with status 2.

```python
    policy = load_inspection_config(args.policy)
    batches = sorted(p for p in BATCHES_DIR.glob('*') if p.is_dir() or p.is_symlink())
```

The policy is loaded before anything else, so a broken policy file stops the run before any batch is touched.

`BATCHES_DIR.glob('*')` lists every entry directly inside `storage/incoming/batches/`. The generator keeps entries that are directories **or symbolic links**, and `sorted` orders them by path. A symbolic link is kept in the list rather than silently ignored, so a link sitting where a batch should be is handed to the inspector like any other entry instead of going unnoticed. Plain files (such as a `.gitkeep`) are dropped. If the batches directory does not exist, `glob` simply yields nothing.

```python
    if args.batch_id:
        if '/' in args.batch_id or '\\' in args.batch_id or args.batch_id in {'.', '..'}:
            parser.error('batch_id must be a directory name')
        batches = [p for p in batches if p.name == args.batch_id]
        if not batches:
            parser.error('batch not found')
    elif args.latest:
        batches = sorted(batches, key=lambda p: (p.lstat().st_mtime_ns, p.name))[-1:]
    else:
        completed = completed_batches(policy)
        batches = [p for p in batches if str(p.absolute()) not in completed]
```

Three mutually exclusive ways to narrow `batches`:

1. **A batch id was given.** First it is checked to be a plain name: no `/`, no `\`, and not `.` or `..`. This stops an argument such as `../../somewhere` from pointing outside the batches directory. Then the list is filtered to the entry with that name; if none matches, `parser.error('batch not found')`.
2. **`--latest`.** The list is re-sorted by `(p.lstat().st_mtime_ns, p.name)` and sliced with `[-1:]`. `lstat()` returns file-system information about the entry itself (without following a symlink); `st_mtime_ns` is its last-modified time in nanoseconds. Sorting by a tuple sorts by the first element and uses the second to break ties. `[-1:]` is "a list containing only the last element" — and, unlike `[-1]`, it gives an empty list instead of an error when there are no batches.
3. **Neither.** `completed_batches(policy)` returns absolute batch paths as strings; the list comprehension keeps batches whose `str(p.absolute())` is *not* in that set. This is the script's skip logic.

**What it means in the pipeline.** "Completed" is strict (4.2): the stored record's checksum must verify, it must have been produced by the current inspector version, and the policy stored inside it must equal the policy loaded now. So if you edit `configs/inspection.json`, every batch becomes pending again and the next plain run re-inspects all of them. That is intended: a decision made under old rules is not a decision under the new ones.

```python
    if not batches:
        print('No pending batches. Acquire uploads first, or select a batch to re-inspect.')
    for batch_dir in batches:
        result = inspect_batch(batch_dir, policy)
        report = write_inspection_report(batch_dir, result)
        quarantine = quarantine_batch(batch_dir, result, report.parent.name)
        summary = result.summary
        print(f'{batch_dir.name}: accepted={summary["accepted"]} quarantined={summary["quarantined"]} rejected={summary["rejected"]}')
        for error in result.errors:
            print(f'  batch quarantine: {error}')
        print(f'  report: {report}')
        if quarantine:
            print(f'  quarantine: {quarantine}')
    return 0
```

If the list is empty the script says so. It does not stop there with an error — the `for` loop simply runs zero times and `main` returns `0`.

For each batch, three calls in a fixed order:

1. `inspect_batch(batch_dir, policy)` → `result`.
2. `write_inspection_report(batch_dir, result)` → `report`, the path `…/inspections/<inspection_id>/manifest.json`.
3. `quarantine_batch(batch_dir, result, report.parent.name)`. `report.parent` is the record directory and `.name` its last component, so `report.parent.name` *is* the inspection id. Passing it on ties the quarantine record to the exact report that caused it.

`result.summary` is a dict computed by the result object; the script prints three of its counts. Inside the f-string, `summary["accepted"]` uses double quotes because the f-string itself is delimited by single quotes. `result.errors` holds batch-level problems (for example a manifest whose checksum does not match), printed one per line. `if quarantine:` is true only when a path was returned.

The printed paths are whatever the library returned, which are absolute paths.

```python
if __name__ == '__main__':
    raise SystemExit(main())
```

`raise SystemExit(n)` ends the program with exit status `n`. `main()` returns `0` (success) on every normal path — including when artifacts were quarantined or rejected. A quarantine is a *result*, not a failure of the command. Only argument errors (status 2) and uncaught exceptions (status 1) give a non-zero status.

**Running it twice.** The plain command is idempotent: batches with a valid record are skipped, so a second run prints `No pending batches. …`. With a batch id or `--latest` it always inspects again and **adds** a new record directory (and possibly a new quarantine record); old records are never overwritten — `publish_record` refuses an existing destination and builds each record in a temporary directory that is renamed into place (4.2). Later stages pick the newest record (see 12.5).

**Empty or missing input.** No batches, or no batches directory → the "No pending batches" line, exit 0. Missing or invalid policy file → `ValueError` with a traceback before any work. A batch directory with no usable `source.json` is not a crash: the inspector returns a result whose batch-level check is "quarantined", and both a report and a quarantine record are written for it.

---

### 12.3 `python -m scripts.provenance`

#### `scripts/provenance.py`

**Command.** No arguments.

```
python -m scripts.provenance
```

**Why this file exists.** It is a *status report*: for every inspected batch, may its content be used for training right now? It changes nothing. You run it to see which batches still need a decision, record a decision with 12.4, and run it again to confirm.

**What enters / what leaves.**

| | |
|---|---|
| Needs | Inspection records from 12.2 and the batches from 12.1. |
| Reads | `storage/catalog/inspections/*/manifest.json`; `storage/incoming/batches/<batch>/source.json`; through the gate, every `storage/catalog/provenance/*/manifest.json` and its checksum. |
| Writes | Nothing. The file contains no write call, and neither does the gate module it uses. |
| Prints | `Inspection manifests: <n>`, then one `ALLOW:`, `BLOCK:` or `SKIP:` line per inspection manifest. |

**How it connects.** Sits between inspection and ingestion as a look-before-you-leap command. `scripts.ingestion` (12.5) calls the same gate function and obeys it.

**The code, section by section.**

```python
import json

from paths import (
    BATCHES_DIR,
    INSPECTIONS_CATALOG_DIR,
)
from src.corpus_factory.provenance.gate import evaluate_training_rights
```

`json` is the standard library module for reading JSON text into Python dicts and lists. `evaluate_training_rights(source_manifest, batch_id)` (4.3) returns a small `RightsDecision` object with `allowed` (True/False), `status`, and `reason`. It looks for the newest checksum-valid provenance decision for that batch; if there is one, that decision rules; if there is none, the answer is always "not allowed", with the reason taken from the `license.training_use` field of `source.json`.

```python
def load_inspection_manifests() -> list[dict]:
    manifests = []

    if not INSPECTIONS_CATALOG_DIR.exists():
        return manifests

    for manifest_path in sorted(
        INSPECTIONS_CATALOG_DIR.glob("*/manifest.json")
    ):
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        manifests.append(manifest)

    return manifests
```

A helper that loads every inspection record.

- If the catalog directory does not exist yet, it returns the empty list immediately.
- `INSPECTIONS_CATALOG_DIR.glob("*/manifest.json")` matches a file called `manifest.json` exactly one directory level down — one per inspection record. `sorted` gives a stable order; because record directory names start with `inspection_<timestamp>`, that order is chronological.
- `manifest_path.read_text(encoding="utf-8")` returns the file's content as one string; `json.loads` parses it into a dict.

It returns **all** records, not the latest per batch. A batch that has been inspected three times appears three times, and the main block below prints three lines for it.

```python
def get_batch_id(inspection: dict) -> str | None:
    incoming_batch = inspection.get("incoming_batch", {})

    if isinstance(incoming_batch, dict):
        batch_id = incoming_batch.get("batch_id")

        if batch_id:
            return batch_id

    return inspection.get("batch_id")
```

Finds the batch id inside an inspection record, defensively. It first looks for a field `incoming_batch` that is a dict containing `batch_id`; if that does not produce a value, it falls back to the top-level `batch_id` field. The records written by the current inspector (4.2) store `incoming_batch` as a *string* (the batch's absolute path) and have a top-level `batch_id`, so with today's records the `isinstance(incoming_batch, dict)` branch is never taken and the last line supplies the answer. The dict branch only matters for records in some other, older layout. The return type `str | None` says the function may find nothing.

```python
if __name__ == "__main__":
    inspections = load_inspection_manifests()

    print(f"Inspection manifests: {len(inspections)}")

    for inspection in inspections:
        batch_id = get_batch_id(inspection)

        if not batch_id:
            print("SKIP: inspection has no batch_id")
            continue

        batch_dir = BATCHES_DIR / batch_id
        source_path = batch_dir / "source.json"

        if not source_path.is_file():
            print(f"SKIP: {batch_id} — source.json missing")
            continue
```

For each inspection record: get the batch id (skip with a message if there is none), build the path of that batch's `source.json`, and skip with a message if the file is not there (for example, the batch directory was deleted after it was inspected). `is_file()` is false both when the path is missing and when it is a directory.

```python
        source_manifest = json.loads(
            source_path.read_text(encoding="utf-8")
        )

        decision = evaluate_training_rights(
            source_manifest,
            batch_id,
        )

        if decision.allowed:
            print(
                f"ALLOW: {batch_id} — {decision.reason}"
            )
        else:
            print(
                f"BLOCK: {batch_id} — {decision.reason}"
            )
```

The source manifest is parsed and handed to the gate together with the batch id. The script then prints `ALLOW` or `BLOCK` with the gate's own reason text — for example `BLOCK: <batch> — training use status: review_required` for a batch nobody has reviewed (acquisition always writes `review_required` into `source.json`), or `ALLOW: <batch> — approved by provenance: owned_data` after a review with basis `owned_data`.

**Running it twice.** Always safe; it only reads. The output changes only when records on disk change.

**Empty or missing input.** No inspections directory or no records → prints `Inspection manifests: 0` and ends. An inspection record that is not valid JSON would raise an exception (nothing catches `json.JSONDecodeError` here). Note that this script does not look at the inspection *outcome* at all: a batch whose every file was rejected still gets an `ALLOW`/`BLOCK` line, because the question asked here is only about rights.

---

### 12.4 `python -m scripts.provenance_review`

#### `scripts/provenance_review.py`

**Command.** Exactly three arguments, read directly from `sys.argv`:

| Position | Name | Meaning |
|---|---|---|
| 1 | `batch-id` | The batch the decision is about (the directory name under `storage/incoming/batches/`). |
| 2 | training use | One of `allowed`, `denied`, `review_required`. |
| 3 | `basis` | Free text: *why* — for example `owned_data`. If it contains spaces it must be quoted so the shell passes it as one argument. |

```
python -m scripts.provenance_review my-source-20260101T120000Z-0a1b2c3d allowed owned_data
```

**Why this file exists.** A human decides whether a batch may be used for training; this is how that decision gets written down in a form the gate can verify.

**What enters / what leaves.**

| | |
|---|---|
| Needs | Nothing on disk. (In practice: a batch id copied from the output of 12.1–12.3.) |
| Writes | A new directory `storage/catalog/provenance/provenance_<YYYYMMDDTHHMMSSZ>_<hex8>/` with `manifest.json` and `manifest.json.sha256`. |
| Prints | `Created provenance decision:` and the absolute path of the new `manifest.json`. |

**How it connects.** Its record is what makes the gate answer "allowed" in 12.3 and 12.5.

**The code, section by section.**

```python
import sys

from src.corpus_factory.provenance.decision import write_rights_decision
```

`sys` gives access to `sys.argv`, the list of words on the command line. `write_rights_decision(batch_id, training_use, basis)` (4.3) validates `training_use`, creates the decision directory, writes the manifest and its SHA-256 checksum, and returns the manifest path.

```python
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage:\n"
            "python -m scripts.provenance_review "
            "<batch-id> <allowed|denied|review_required> <basis>"
        )
```

`sys.argv[0]` is the script's own path, so three real arguments make a list of length **4**. Any other count stops the program: `raise SystemExit("some text")` prints the text to the terminal and exits with status 1. The three string literals are adjacent, and Python joins adjacent string literals into one, so the message is the two-line usage text.

```python
    batch_id = sys.argv[1]
    training_use = sys.argv[2]
    basis = sys.argv[3]

    manifest_path = write_rights_decision(
        batch_id=batch_id,
        training_use=training_use,
        basis=basis,
    )

    print(f"Created provenance decision:")
    print(manifest_path)
```

The three arguments are given names and passed by keyword. Line 24 has an `f` prefix but no `{}` inside — it is an ordinary string; the prefix does nothing there.

**Logic that is *not* here.** The script does not check the second argument; `write_rights_decision` does, and raises `ValueError: Invalid training_use: …` (a traceback, not the tidy usage message) for anything outside the three allowed words. Neither the script nor the library checks that the batch id **exists**. A mistyped id produces a perfectly valid decision record for a batch that is not there; nothing complains, and the real batch stays blocked. Run 12.3 afterwards to confirm the effect.

**Running it twice.** Each run *appends* a new decision directory with a new timestamp and random suffix (the directory is created with `exist_ok=False`, so it can never land on an existing one). Decisions are never edited. The gate uses the one with the latest `created_at` for the batch, so to change your mind you simply record a new decision — for example `denied` after an earlier `allowed`.

**Empty or missing input.** Wrong number of arguments → usage text, exit status 1, nothing written.

---

### 12.5 `python -m scripts.ingestion`

#### `scripts/ingestion.py`

**Command.** No arguments.

```
python -m scripts.ingestion
```

**Why this file exists.** This is where three earlier results are combined into one action. A file is copied into `storage/raw/` only if (a) the *latest* inspection of its batch accepted that file, and (b) the provenance gate allows its batch. The copying is library code (4.4); the selection is entirely in this script.

**What enters / what leaves.**

| | |
|---|---|
| Needs | Inspection records (12.2), the batches themselves (12.1), and an `allowed` provenance decision (12.4) for each batch you want ingested. |
| Reads | `storage/catalog/inspections/*/manifest.json`; `storage/incoming/batches/<batch>/source.json`; provenance decisions (through the gate); the accepted files under `storage/incoming/batches/<batch>/objects/`. |
| Writes | `storage/raw/<batch>/objects/<doc>-<nnnnnnnn>-<original name>` for each accepted file; `storage/raw/<batch>/manifest.json` and `manifest.json.sha256`. |
| Prints | Per batch one of: `SKIP: <batch> — source manifest missing`, `BLOCK: <batch> — <reason>`, `SKIP: <batch> — no accepted artifacts`, or `INGESTED: <batch> (<n> documents)` followed by `  manifest: <path>`. |

**How it connects.** Consumes inspection + provenance + batches. The `manifest.json` it leaves in each raw batch directory is the list `scripts.extraction` (12.6) works from.

**The code, section by section.**

```python
import json
from pathlib import Path

from paths import (
    BATCHES_DIR,
    INSPECTIONS_CATALOG_DIR,
)

from src.corpus_factory.ingestion.ingest import (
    ingest_artifact,
    write_ingestion_manifest,
)
from src.corpus_factory.provenance.gate import evaluate_training_rights
```

`Path` is needed for one line below (`Path(incoming_batch).name`). From 4.4: `ingest_artifact(source_path, batch_id, artifact_id, sha256)` invents a new document id (`doc_` + 32 random hex characters), copies the file into `storage/raw/<batch>/objects/` under a name that starts with that id, and returns a dict describing the document; `write_ingestion_manifest(batch_id, documents)` writes the list of those dicts as `manifest.json` with a checksum file and returns its path. `evaluate_training_rights` is the same gate as in 12.3.

```python
def load_latest_inspections() -> dict[str, dict]:
    latest = {}

    for manifest_path in sorted(
        INSPECTIONS_CATALOG_DIR.glob("*/manifest.json")
    ):
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        incoming_batch = manifest.get("incoming_batch")

        if isinstance(incoming_batch, dict):
            batch_id = incoming_batch.get("batch_id")

        elif isinstance(incoming_batch, str):
            batch_id = Path(incoming_batch).name

        else:
            batch_id = manifest.get("batch_id")

        if batch_id:
            latest[batch_id] = manifest

    return latest
```

**What Python does.** The function walks the inspection records in sorted order and stores each one in a dict under its batch id: `latest[batch_id] = manifest`. Assigning to a key that already exists **replaces** the old value. So when a batch has several records, each later one overwrites the earlier one, and after the loop the dict holds exactly one record per batch — the last one in sorted order.

**What it means in the pipeline.** Record directories are named `inspection_<UTC timestamp>_<random>`, and timestamps written as `YYYYMMDDTHHMMSS…` sort alphabetically in the same order as chronologically. "Last in sorted order" is therefore "most recent inspection". That is the whole mechanism behind the function's name, and it is why re-inspecting a batch (12.2) changes what ingestion will do: only the newest verdict counts.

The batch id is found in three ways, tried in order: `incoming_batch` is a dict → take its `batch_id`; `incoming_batch` is a string → treat it as a path and take its last component with `Path(...).name`; otherwise → the top-level `batch_id`. With today's inspection records the **second** branch is the one that runs, because the inspector stores `incoming_batch` as the batch's path. (Compare 12.3, whose helper has no string branch and reaches the same id through the top-level field instead. Two helpers, two routes, same answer for current records.)

Unlike `load_inspection_manifests` in 12.3, this function does not first check that the directory exists. It does not need to: `glob` on a missing directory yields nothing.

This function reads the inspection records as plain JSON. It does not verify their `.sha256` files, and it does not look at the record's `batch_status` or `next_stage` fields; what it relies on, further down, is each artifact's own `decision`.

```python
if __name__ == "__main__":
    inspections = load_latest_inspections()

    for batch_id, inspection in inspections.items():
        batch_dir = BATCHES_DIR / batch_id
        source_path = batch_dir / "source.json"

        if not source_path.is_file():
            print(f"SKIP: {batch_id} — source manifest missing")
            continue

        source_manifest = json.loads(
            source_path.read_text(encoding="utf-8")
        )
```

`inspections.items()` yields `(key, value)` pairs, here `(batch_id, inspection)`. For each batch the script locates `source.json`; if the batch directory or its manifest has gone, it prints a `SKIP` line and moves on. Otherwise it parses the manifest — the gate needs it for the fallback reason text.

```python
        rights = evaluate_training_rights(
            source_manifest,
            batch_id,
        )

        if not rights.allowed:
            print(f"BLOCK: {batch_id} — {rights.reason}")
            continue
```

**The rights gate.** If the gate does not allow the batch, nothing of it is copied and the reason is printed. For a batch nobody has reviewed, this is the line you will see: `BLOCK: <batch> — training use status: review_required`.

```python
        documents = []

        for artifact in inspection.get("artifacts", []):
            decision = artifact.get("decision")

            if decision != "accepted_for_ingestion":
                continue

            artifact_id = artifact["artifact_id"]
            relative_path = artifact["stored_relative_path"]
            sha256 = artifact["sha256"]

            incoming_file = batch_dir / relative_path

            document = ingest_artifact(
                source_path=incoming_file,
                batch_id=batch_id,
                artifact_id=artifact_id,
                sha256=sha256,
            )

            documents.append(document)
```

**The inspection gate, per file.** `inspection.get("artifacts", [])` is the list of per-file results in the inspection record (an empty list if the key is missing). Each has a `decision`; only the exact string `accepted_for_ingestion` passes. Quarantined and rejected files are skipped silently — they were already reported by 12.2.

For an accepted file the script reads three fields from the inspection record: the artifact id, the path of the file relative to the batch directory (such as `objects/00000001-notes.txt`), and the SHA-256 the inspector computed. `batch_dir / relative_path` gives the real location of the file in `storage/incoming/`. `ingest_artifact` copies it and the returned dict is appended to `documents`.

The square-bracket lookups (`artifact["artifact_id"]`) raise `KeyError` if a field is missing, where `.get` would return `None`. That is a deliberate difference in strictness: a record without these fields is unusable, so crashing is the honest outcome.

The `sha256` passed along is the one recorded at inspection time. It is carried into the raw manifest as information; the file is not hashed again during the copy.

```python
        if not documents:
            print(f"SKIP: {batch_id} — no accepted artifacts")
            continue

        manifest_path = write_ingestion_manifest(
            batch_id=batch_id,
            documents=documents,
        )

        print(
            f"INGESTED: {batch_id} "
            f"({len(documents)} documents)"
        )
        print(f"  manifest: {manifest_path}")
```

If no file of the batch was accepted, no manifest is written — the batch simply does not appear in `storage/raw/`. Otherwise one manifest is written for the batch, listing every document just copied, and the script prints the count and the manifest path.

**Running it twice.** This is the one stage where a second run is **not** a no-op, and it is worth understanding exactly what happens:

- `ingest_artifact` makes a *new random document id on every call*. A second run therefore copies every accepted file again, under new names, next to the first copies in `storage/raw/<batch>/objects/`.
- `write_ingestion_manifest` uses `write_bytes`, which overwrites. The new `manifest.json` lists **only the new** document ids. The first run's copies are still on disk but no manifest mentions them any more.
- Downstream, extraction (12.6) follows the manifest, so it produces `<new doc>.txt` files — but it does not delete the `<old doc>.txt` files from the first run, and the stages after it loop over every `*.txt` they find. Old and new copies of the same text both travel down the pipeline until deduplication (12.10) keeps one of each identical pair.

Nothing breaks, and the final dataset contains each text once, but the intermediate directories accumulate stale files. There is no "already ingested" check comparable to the fingerprint in 12.1.

**Empty or missing input.** No inspection records → the dict is empty, the loop does not run, and the script prints **nothing at all**. All batches blocked → only `BLOCK` lines; `storage/raw/` is unchanged.

---

### 12.6 `python -m scripts.extraction`

#### `scripts/extraction.py`

**Command.** No arguments.

```
python -m scripts.extraction
```

**Why this file exists.** Raw files can be of several types; later stages want plain text in a predictable place, one file per document, named by document id. This script walks the raw manifests and produces exactly that.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/raw/` with batch directories written by 12.5. |
| Reads | `storage/raw/<batch>/manifest.json` and each file it lists. |
| Writes | `storage/extracted/<batch>/<doc>.txt`. |
| Prints | `EXTRACTED: <stored file name> -> <doc>.txt` or `SKIP: <stored file name> — <reason>`. |

**How it connects.** Follows ingestion; feeds `scripts.cleaning` (12.7). From here on, a document is identified by the file name `<doc>.txt` inside a folder named after its batch, and that pair is preserved unchanged through every stage up to dataset building.

**The code, section by section.**

```python
import json
from pathlib import Path

from paths import RAW_STORAGE_DIR, EXTRACTED_DIR
from src.corpus_factory.extraction.extractor import extract_text
```

`extract_text(file_path)` (4.5) returns the file's content as a string when the extension is `.txt` or `.md`, and raises `ValueError("Unsupported extraction type: …")` for anything else. The `Path` import on line 2 is not used anywhere in this file.

```python
if __name__ == "__main__":
    batch_dirs = sorted(
        path
        for path in RAW_STORAGE_DIR.iterdir()
        if path.is_dir()
    )
```

`RAW_STORAGE_DIR.iterdir()` yields every entry directly inside `storage/raw/`. The generator keeps directories only (this is what drops a stray file such as `.gitkeep`), and `sorted` fixes the order. Each directory is one batch.

```python
    for batch_dir in batch_dirs:
        manifest_path = batch_dir / "manifest.json"

        if not manifest_path.is_file():
            continue

        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )

        output_batch_dir = EXTRACTED_DIR / batch_dir.name
        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
```

A batch directory without `manifest.json` is skipped silently — the manifest is the list of work, and without it there is nothing to do. With it, the script parses the JSON and creates the matching output directory `storage/extracted/<batch>/`.

`mkdir(parents=True, exist_ok=True)` is the form every remaining script uses: `parents=True` also creates missing parent directories (so `storage/extracted/` itself need not exist), and `exist_ok=True` means "do not complain if it is already there". Together they make the call safe to repeat.

```python
        for document in manifest.get("documents", []):
            document_id = document["document_id"]

            source_file = (
                batch_dir
                / document["stored_relative_path"]
            )

            try:
                text = extract_text(source_file)

            except ValueError as error:
                print(
                    f"SKIP: {source_file.name} — {error}"
                )
                continue
```

For each document in the manifest, the source file is `storage/raw/<batch>/` joined with the `stored_relative_path` that ingestion recorded.

`try` / `except ValueError` catches the "unsupported type" error and turns it into a printed `SKIP` line; `continue` moves to the next document. So a PDF that passed inspection and was ingested does not stop the run — it just produces no text. (The allowed-extension list in the inspection policy is much longer than the two types extraction can read today.)

One consequence worth knowing: in Python, the error raised when bytes are not valid UTF-8 (`UnicodeDecodeError`) is itself a kind of `ValueError`. So a `.txt` file in some other encoding is also caught here and reported as `SKIP` with the decoder's message, rather than crashing the script. A file that is listed in the manifest but missing on disk is a different error type (`FileNotFoundError`) and is **not** caught.

```python
            output_path = (
                output_batch_dir
                / f"{document_id}.txt"
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"EXTRACTED: {source_file.name}"
                f" -> {output_path.name}"
            )
```

The output file name is built from the document id only — the original file name is left behind in the raw manifest. `write_text(text, encoding="utf-8")` creates the file or replaces its content, then the script prints both names.

**Running it twice.** Safe. The same document ids produce the same output files, which are overwritten with identical text. It does not remove anything: if a document id is no longer in the manifest (see "Running it twice" in 12.5), its old `.txt` stays in `storage/extracted/`.

**Empty or missing input.** `storage/raw/` missing → `FileNotFoundError` from `iterdir()`. Present but with no batch directories → nothing happens, nothing printed. An output directory is created for every batch that has a manifest, even if every document in it is skipped.

---

### 12.7 `python -m scripts.cleaning`

#### `scripts/cleaning.py`

**Command.** No arguments.

```
python -m scripts.cleaning
```

**Why this file exists.** It applies `clean_text` to every extracted document and stores the result as the first of four "processed" stages. It is also the template for the next three scripts.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/extracted/<batch>/*.txt` from 12.6. |
| Writes | `storage/processed/cleaned/<batch>/<doc>.txt` — same batch folder name, same file name. |
| Prints | `CLEANED: <doc>.txt -> <full output path>` per file. |

**How it connects.** Follows extraction; feeds `scripts.normalization` (12.8).

**The code, section by section.**

```python
from pathlib import Path

from paths import EXTRACTED_DIR, PROCESSED_DIR
from src.corpus_factory.preprocessing.cleaning import clean_text


CLEANED_DIR = PROCESSED_DIR / "cleaned"
```

`clean_text(text)` (4.6) converts Windows and old-Mac line endings to `\n`, strips trailing whitespace from each line, and removes blank lines at the very start and end; it returns the new string. `CLEANED_DIR` is defined here, at module level, by joining `"cleaned"` onto `PROCESSED_DIR`. The `Path` import is unused.

```python
if __name__ == "__main__":
    for batch_dir in sorted(
        path
        for path in EXTRACTED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = CLEANED_DIR / batch_dir.name

        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
```

The outer loop: every directory directly inside `storage/extracted/`, in sorted order. Here the generator expression is written straight inside `sorted(...)` inside the `for` line, instead of being stored in a variable first as in 12.6 — the meaning is identical. For each batch the mirror directory under `cleaned/` is created.

```python
        for source_file in sorted(
            batch_dir.glob("*.txt")
        ):
            text = source_file.read_text(
                encoding="utf-8"
            )

            cleaned = clean_text(text)

            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                cleaned,
                encoding="utf-8",
            )

            print(
                f"CLEANED: {source_file.name}"
                f" -> {output_path}"
            )
```

The inner loop: `batch_dir.glob("*.txt")` matches files in that batch folder whose names end in `.txt` (not in sub-folders). For each one: read the whole file into a string, pass it through `clean_text`, build the output path with the **same file name**, write, print.

This is a one-to-one stage: every input file produces exactly one output file, even if cleaning leaves it empty. Deciding that a document is not worth keeping is the filter's job, two stages later.

**Running it twice.** Safe; outputs are overwritten with the same content. Like every stage in this group, it never deletes: an output file whose input has disappeared stays where it is.

**Empty or missing input.** `storage/extracted/` missing → `FileNotFoundError` from `iterdir()`. No batch folders → silent, nothing written. A batch folder with no `.txt` files → an empty output folder is created.

---

### 12.8 `python -m scripts.normalization`

#### `scripts/normalization.py`

**Command.** No arguments.

```
python -m scripts.normalization
```

**Why this file exists.** Same loop as cleaning, one stage further on, applying `normalize_text`.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/processed/cleaned/<batch>/*.txt` from 12.7. |
| Writes | `storage/processed/normalized/<batch>/<doc>.txt`. |
| Prints | `NORMALIZED: <doc>.txt -> <full output path>` per file. |

**How it connects.** Follows cleaning; feeds `scripts.filtering` (12.9).

**The code, section by section.**

```python
from paths import PROCESSED_DIR
from src.corpus_factory.preprocessing.normalization import normalize_text


CLEANED_DIR = PROCESSED_DIR / "cleaned"
NORMALIZED_DIR = PROCESSED_DIR / "normalized"
```

`normalize_text(text)` (4.6) applies Unicode NFC normalization — characters that can be written either as one code point or as a base letter plus a combining mark are brought to one canonical form — and changes nothing else. Two stage directories are defined: the one this script reads, and the one it writes. `CLEANED_DIR` here is a second, independent definition of the same path that `cleaning.py` defines; the two scripts agree only because both type the string `"cleaned"`.

```python
if __name__ == "__main__":
    for batch_dir in sorted(
        path
        for path in CLEANED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = NORMALIZED_DIR / batch_dir.name

        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
```

```python
        for source_file in sorted(
            batch_dir.glob("*.txt")
        ):
            text = source_file.read_text(
                encoding="utf-8"
            )

            normalized = normalize_text(text)

            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                normalized,
                encoding="utf-8",
            )

            print(
                f"NORMALIZED: {source_file.name}"
                f" -> {output_path}"
            )
```

Line for line the same structure as 12.7, with `CLEANED_DIR` as the source, `NORMALIZED_DIR` as the destination, and `normalize_text` as the transformation. Again one output per input.

**Running it twice.** Safe; overwrites with identical content.

**Empty or missing input.** `storage/processed/cleaned/` does not exist until 12.7 has run at least once; running this first gives `FileNotFoundError`.

---

### 12.9 `python -m scripts.filtering`

#### `scripts/filtering.py`

**Command.** No arguments.

```
python -m scripts.filtering
```

**Why this file exists.** First stage that can *drop* a document. The rule lives in `filter_text`; the script turns the verdict into "copy this file forward" or "do not".

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/processed/normalized/<batch>/*.txt` from 12.8. |
| Writes | `storage/processed/filtered/<batch>/<doc>.txt` for accepted documents only. |
| Prints | `ACCEPTED: <doc>.txt -> <full output path>` or `FILTERED OUT: <doc>.txt — <reason>`. |

**How it connects.** Follows normalization; feeds `scripts.deduplication` (12.10).

**The code, section by section.**

```python
from paths import PROCESSED_DIR
from src.corpus_factory.preprocessing.filtering import filter_text


NORMALIZED_DIR = PROCESSED_DIR / "normalized"
FILTERED_DIR = PROCESSED_DIR / "filtered"
```

`filter_text(text)` (4.6) returns a `FilterResult` with two fields: `accepted` (bool) and `reason` (a short string). Today it rejects a text that is only whitespace (`empty_document`) or shorter than 20 characters (`too_short`), and accepts everything else.

```python
if __name__ == "__main__":
    for batch_dir in sorted(
        path
        for path in NORMALIZED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = FILTERED_DIR / batch_dir.name

        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
```

```python
        for source_file in sorted(
            batch_dir.glob("*.txt")
        ):
            text = source_file.read_text(
                encoding="utf-8"
            )

            result = filter_text(text)

            if not result.accepted:
                print(
                    f"FILTERED OUT: {source_file.name}"
                    f" — {result.reason}"
                )
                continue
```

Same two loops. The difference starts at `result = filter_text(text)`: when `result.accepted` is false the script prints the reason and `continue` skips the rest of the loop body — so the write below never happens for that file.

```python
            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"ACCEPTED: {source_file.name}"
                f" -> {output_path}"
            )
```

For an accepted document the script writes `text` — the **unchanged** input. Filtering transforms nothing; an accepted file in `filtered/` is byte-for-byte the text that was in `normalized/`.

**Running it twice.** Safe for accepted files (overwritten with the same text). But "not written" is not the same as "removed": if a document was accepted in an earlier run and is rejected now (because the text or the rule changed), its old copy **remains** in `storage/processed/filtered/` and continues down the pipeline. The script only ever adds or overwrites.

**Empty or missing input.** Missing `normalized/` → `FileNotFoundError`. If every document is rejected, the batch's output folder exists but is empty.

---

### 12.10 `python -m scripts.deduplication`

#### `scripts/deduplication.py`

**Command.** No arguments.

```
python -m scripts.deduplication
```

**Why this file exists.** Keeps one copy of each distinct text. The library contributes only a one-line hash function; the deduplication *algorithm* — remember what has been seen, across all batches — is this script.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/processed/filtered/<batch>/*.txt` from 12.9. |
| Writes | `storage/processed/deduplicated/<batch>/<doc>.txt` for the first occurrence of each text. |
| Prints | `UNIQUE: <doc>.txt -> <full output path>` or `DUPLICATE: <doc>.txt`. |

**How it connects.** Last of the four preprocessing stages; feeds `scripts.dataset_building` (12.11).

**The code, section by section.**

```python
from paths import PROCESSED_DIR
from src.corpus_factory.preprocessing.deduplication import text_sha256


FILTERED_DIR = PROCESSED_DIR / "filtered"
DEDUPED_DIR = PROCESSED_DIR / "deduplicated"
```

`text_sha256(text)` (4.6) encodes the string as UTF-8 and returns its SHA-256 hex digest (hashing is explained in 4.1). Two texts get the same digest exactly when they are character-for-character identical.

```python
if __name__ == "__main__":
    seen_hashes = set()

    for batch_dir in sorted(
        path
        for path in FILTERED_DIR.iterdir()
        if path.is_dir()
    ):
        output_batch_dir = DEDUPED_DIR / batch_dir.name

        output_batch_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
```

`seen_hashes = set()` is created **before** the batch loop and is never reset. That placement is the important decision in this file: the memory spans all batches, so a text in batch B that already appeared in batch A is recognised as a duplicate.

```python
        for source_file in sorted(
            batch_dir.glob("*.txt")
        ):
            text = source_file.read_text(
                encoding="utf-8"
            )

            digest = text_sha256(text)

            if digest in seen_hashes:
                print(
                    f"DUPLICATE: {source_file.name}"
                )
                continue

            seen_hashes.add(digest)
```

**What Python does.** For each file: compute the digest; test `digest in seen_hashes` (a set answers this in constant time, however many digests it holds); if present, print `DUPLICATE` and skip; if not, `add` it.

**What it means in the pipeline.** A set of 64-character digests stands in for "all the texts seen so far" without keeping the texts in memory. The first file to arrive with a given text wins, and "first" is decided by the two `sorted` calls: batches in alphabetical order of batch id, then files in alphabetical order of name. Because batch ids start with the source name, not the date, "first" means alphabetically first, not oldest.

This is **exact** deduplication. One different character — an extra space inside a line, a different digit — gives a different digest and both documents are kept. It works as well as it does only because cleaning and normalization run first and remove the invisible differences (line endings, trailing spaces, Unicode forms) that would otherwise make identical-looking texts hash differently.

```python
            output_path = (
                output_batch_dir
                / source_file.name
            )

            output_path.write_text(
                text,
                encoding="utf-8",
            )

            print(
                f"UNIQUE: {source_file.name}"
                f" -> {output_path}"
            )
```

A unique document is written unchanged under the same name, as in filtering.

**Running it twice.** Each run starts with an empty `seen_hashes`, reads the same inputs in the same order, and reaches the same verdicts, so the same files are rewritten. As with filtering, nothing is deleted: a file written as `UNIQUE` in an earlier run stays in `deduplicated/` even if a later run would call it `DUPLICATE` (which can happen when a new batch that sorts earlier now contains the same text).

**Empty or missing input.** Missing `filtered/` → `FileNotFoundError`. Empty → silent.

---

### 12.11 `python -m scripts.dataset_building`

#### `scripts/dataset_building.py`

**Command.** No arguments.

```
python -m scripts.dataset_building
```

**Why this file exists.** Up to here the corpus is a set of small files in folders. Training wants three files — train, validation, test — each a stream of records. This script decides the split for every document and writes the three JSONL files. The split *rule* is in `src/dataset/builder.py`; collecting the documents, opening the files and routing each record are done here.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/processed/deduplicated/<batch>/*.txt` from 12.10. |
| Writes | `storage/training/dataset/train.jsonl`, `validation.jsonl`, `test.jsonl`. One line per document: a JSON object with `document_id`, `batch_id`, `text`. |
| Prints | `TRAIN: <doc>`, `VALIDATION: <doc>` or `TEST: <doc>` per document. |

**How it connects.** Ends the corpus half of the pipeline. `train.jsonl` feeds `scripts.tokenizer_training` (12.12); all three feed `scripts.tokenize_dataset` (12.13).

**The code, section by section.**

```python
import json
from pathlib import Path

from paths import PROCESSED_DIR, TRAINING_DATA_DIR
from src.dataset.builder import assign_splits


DEDUPED_DIR = PROCESSED_DIR / "deduplicated"
DATASET_DIR = TRAINING_DATA_DIR / "dataset"
```

`assign_splits(document_ids)` (5) takes a list of ids and returns a dict `{document_id: "train" | "validation" | "test"}`. Each id is hashed and the hash decides the split (about 90 / 5 / 5), so a given document always lands in the same split; and if that would leave *no* document in train — likely with a very small corpus — it puts every document in train instead. `json` is used to write the records. `Path` is imported and not used.

```python
if __name__ == "__main__":
    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents = [
        (batch_dir.name, source_file)
        for batch_dir in sorted(
            path
            for path in DEDUPED_DIR.iterdir()
            if path.is_dir()
        )
        for source_file in sorted(
            batch_dir.glob("*.txt")
        )
    ]
```

The output directory is created first. Then **one list** of every document in the corpus is built.

**What Python does.** This is a list comprehension with two `for` clauses. Read it as two nested loops: for each batch directory (sorted), for each `.txt` file in it (sorted), produce the tuple `(batch_dir.name, source_file)`. The result looks like `[("batch-a", Path(".../doc_1.txt")), ("batch-a", Path(".../doc_2.txt")), ("batch-b", Path(".../doc_3.txt"))]`. Only names and paths are held; no text has been read yet.

**What it means in the pipeline.** Every earlier stage streamed: handle one file, forget it. This stage needs the complete list of ids *before* writing anything, because the "is train empty?" rule in `assign_splits` cannot be answered one document at a time.

```python
    splits = assign_splits(
        [
            source_file.stem
            for _, source_file in documents
        ]
    )
```

`source_file.stem` is the file name without its extension: `doc_0123….txt` → `doc_0123…`, i.e. the document id. The comprehension `for _, source_file in documents` unpacks each tuple and ignores the batch name (`_` is the conventional name for "a value I do not need"). `splits` now maps every document id to its split.

```python
    output_files = {
        "train": DATASET_DIR / "train.jsonl",
        "validation": DATASET_DIR / "validation.jsonl",
        "test": DATASET_DIR / "test.jsonl",
    }

    handles = {
        split: path.open(
            "w",
            encoding="utf-8",
        )
        for split, path in output_files.items()
    }
```

Two dicts with the same three keys. `output_files` maps a split name to a path. `handles` is built from it with a dict comprehension: for each `(split, path)` pair it calls `path.open("w", encoding="utf-8")` and stores the open file object. After these lines, three files are open for writing at once.

**What Python does.** Mode `"w"` creates the file if it is missing and **empties it** if it exists. This happens at the moment of opening, before any document has been read.

**What it means in the pipeline.** Every run rebuilds the three dataset files from scratch from whatever is in `deduplicated/` right now. Nothing is appended to an earlier dataset. The files are not opened with `with` because there are three of them, chosen by key; the `try`/`finally` below does the job `with` would do.

```python
    try:
        for batch_id, source_file in documents:
            document_id = source_file.stem

            text = source_file.read_text(
                encoding="utf-8"
            )

            split = splits[document_id]

            record = {
                "document_id": document_id,
                "batch_id": batch_id,
                "text": text,
            }

            handles[split].write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )
```

The main loop. For each `(batch_id, source_file)`:

1. `document_id` is the stem again; `text` is the whole file.
2. `split = splits[document_id]` looks up the decision made earlier.
3. `record` is a dict with exactly three keys.
4. `handles[split]` picks the right open file; `json.dumps(record, ensure_ascii=False) + "\n"` turns the dict into **one line** of text.

**What Python does.** `json.dumps` produces a JSON string. Any newline inside `text` is written as the two characters `\n`, so the whole record — however many lines the document had — stays on a single physical line. `ensure_ascii=False` writes non-ASCII characters as themselves: Arabic letters stay readable in the file instead of becoming `م`-style escapes. The `+ "\n"` ends the line.

**What it means in the pipeline.** One line = one document is the JSONL format (5). It lets every later reader go through the dataset line by line without loading it all. A record looks like this (made-up values):

```
{"document_id": "doc_0123…cdef", "batch_id": "my-source-20260101T120000Z-0a1b2c3d", "text": "i love coffee\nsecond line"}
```

Keeping `batch_id` in each record means you can still trace a training document back to its source batch.

```python
            print(
                f"{split.upper()}: "
                f"{document_id}"
            )

    finally:
        for handle in handles.values():
            handle.close()
```

`split.upper()` prints the split name in capitals. The `finally` block runs whether the loop finished or an exception interrupted it, and closes all three files; closing is what guarantees the last buffered lines actually reach the disk.

**Running it twice.** Safe and repeatable: same inputs → same three files, fully rewritten. Because the split is computed from the document id alone, a document keeps its split from run to run. There is one exception that follows from the fallback rule: with a tiny corpus where everything was forced into train, adding documents later can make the fallback unnecessary, at which point some documents that were in train move to validation or test.

Remember where document ids come from: ingestion (12.5) invents them at random. Re-ingesting a batch gives the same texts new ids, and therefore possibly different splits.

**Empty or missing input.** `storage/processed/deduplicated/` missing → `FileNotFoundError` while building `documents`; this happens *before* the files are opened, so an existing dataset is left intact. Directory present but containing no documents → `assign_splits([])` returns `{}`, the three files are opened (and so emptied), the loop does not run, nothing is printed. You are left with three empty files, and the next command fails with a clear message (12.12).

---

### 12.12 `python -m scripts.tokenizer_training`

#### `scripts/tokenizer_training.py`

**Command.** No arguments.

```
python -m scripts.tokenizer_training
```

**Why this file exists.** Learns the BPE merge table from the training text and saves it. The algorithm is library code (6); the script supplies the text source, the vocabulary size, and the save location.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `storage/training/dataset/train.jsonl` from 12.11, with at least one non-empty text. |
| Writes | `artifacts/tokenizer/tokenizer.json`. |
| Prints | One line per learned merge (`merge <id>: (<left>, <right>) frequency=<n>` — printed by `train_bpe`, not by the script), a blank line, `Vocab size: <n>`, `Saved: <path>`. |

**How it connects.** First command of the model half. The tokenizer file is needed by `scripts.tokenize_dataset` (12.13), `scripts.inference` (12.16), `scripts.model_stats` (12.17) and the server (12.18).

**The code, section by section.**

```python
from paths import (
    TRAINING_DATA_DIR,
    TOKENIZER_PATH,
)
from src.dataset.loader import load_texts
from src.tokenization.bpe import train_bpe
from src.tokenization.tokenizer import Tokenizer


TRAIN_PATH = (
    TRAINING_DATA_DIR
    / "dataset"
    / "train.jsonl"
)
```

- `load_texts(path)` (5) is a generator that yields the `text` field of each record in a JSONL file, one at a time.
- `train_bpe(texts, target_vocab_size)` (6) turns each text into bytes, repeatedly merges the most frequent adjacent pair into a new token id, and returns a `BPEModel` holding the list of merges.
- `Tokenizer(model)` (6) wraps that model with `encode`, `decode`, `save`, `load`.

`TRAIN_PATH` points at the **train** split only. The tokenizer never sees validation or test text; if it did, a little information about the held-out data would leak into the vocabulary the model is built on.

```python
if __name__ == "__main__":
    texts = load_texts(TRAIN_PATH)

    model = train_bpe(
        texts=texts,
        target_vocab_size=300,
    )
```

`texts` is a generator: at this point no line of the file has been read. Reading starts inside `train_bpe` when it loops over `texts`.

`target_vocab_size=300` is a **literal in this script**. It is the single place that decides how large the vocabulary may get. Token ids `0`–`255` are the raw bytes and `256`–`258` are BOS, EOS and PAD (6), so the first merge gets id `259` and a target of `300` allows at most `300 − 259 = 41` merges. Training can stop earlier — when no pair occurs at least twice — in which case the vocabulary is smaller than 300.

The number 300 appears independently in one other place: `ModelConfig.vocab_size` defaults to `300` (7), and `scripts.train` builds the model from those defaults without looking at the tokenizer file. The two values match today. Nothing in the code ties them together.

```python
    tokenizer = Tokenizer(model)

    tokenizer.save(
        TOKENIZER_PATH
    )

    print()
    print(f"Vocab size: {tokenizer.vocab_size}")
    print(f"Saved: {TOKENIZER_PATH}")
```

`tokenizer.save(TOKENIZER_PATH)` creates `artifacts/tokenizer/` if necessary and writes the JSON file. `print()` with no argument prints an empty line, separating the merge log from the two summary lines. `tokenizer.vocab_size` is `259 + number of merges`.

**Running it twice.** It overwrites `tokenizer.json`. With the same `train.jsonl` the result is the same file. With a **changed** `train.jsonl` the merges can differ, and that has consequences beyond this file: token id `270`, say, would now stand for a different byte sequence. Everything that was produced with the old tokenizer — the tokenized dataset and every saved checkpoint — silently stops matching. After retraining the tokenizer you must re-run 12.13 and train a model from the beginning rather than resume.

**Empty or missing input.** Missing `train.jsonl` → `FileNotFoundError` (raised when `train_bpe` starts reading). An empty `train.jsonl`, or one whose texts are all empty strings → `ValueError: Cannot train tokenizer on an empty corpus`. In both cases no tokenizer file is written and an existing one is left as it was.

---

### 12.13 `python -m scripts.tokenize_dataset`

#### `scripts/tokenize_dataset.py`

**Command.** No arguments.

```
python -m scripts.tokenize_dataset
```

**Why this file exists.** Encoding text into token ids is the slowest part of preparing data (each document is passed over once per merge). Doing it once and storing the ids means training, evaluation and statistics can all read numbers directly.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `artifacts/tokenizer/tokenizer.json` (12.12) and the three files in `storage/training/dataset/` (12.11). |
| Writes | `storage/training/tokenized/train.jsonl`, `validation.jsonl`, `test.jsonl`. One line per document: `document_id`, `batch_id`, `input_ids`, `num_tokens`. The text itself is not copied. |
| Prints | Per split: `<split>: documents=<n>, tokens=<n>`. |

**How it connects.** Feeds `scripts.train` (12.14), `scripts.evaluate` (12.15) and `scripts.model_stats` (12.17).

**The code, section by section.**

```python
import json

from paths import TRAINING_DATA_DIR, TOKENIZER_PATH
from src.dataset.loader import load_jsonl
from src.tokenization.tokenizer import Tokenizer


DATASET_DIR = TRAINING_DATA_DIR / "dataset"
TOKENIZED_DIR = TRAINING_DATA_DIR / "tokenized"
```

`load_jsonl(path)` (5) is a generator yielding one parsed record (a dict) per non-empty line, and raising `ValueError` with the line number if a line is not valid JSON. `Tokenizer.load(path)` (6) rebuilds a tokenizer from the saved merge list.

```python
if __name__ == "__main__":
    tokenizer = Tokenizer.load(TOKENIZER_PATH)

    TOKENIZED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
```

The tokenizer is loaded once, before the loop — if the file is missing the script stops here, before touching any output. Then the output directory is created.

```python
    for split in (
        "train",
        "validation",
        "test",
    ):
        input_path = DATASET_DIR / f"{split}.jsonl"
        output_path = TOKENIZED_DIR / f"{split}.jsonl"

        document_count = 0
        token_count = 0
```

The loop variable `split` takes the three names in turn. The f-strings build matching input and output paths, so `dataset/train.jsonl` becomes `tokenized/train.jsonl`, and so on. Two counters are reset for each split.

```python
        with output_path.open(
            "w",
            encoding="utf-8",
        ) as output_file:

            for record in load_jsonl(input_path):
                text = record["text"]

                token_ids = tokenizer.encode(
                    text,
                    add_bos=True,
                    add_eos=True,
                )
```

The output file is opened with `"w"` inside a `with` block (emptied if it exists, closed automatically at the end of the block). Then records are streamed from the input.

`tokenizer.encode(text, add_bos=True, add_eos=True)` returns a list of integers.

**What Python does.** The text is turned into its UTF-8 bytes, the learned merges are applied in order, then id `256` is inserted at the front and id `257` appended at the end.

**What it means for the model.** Every stored document is framed as `[BOS] … [EOS]`. This is where the model's notion of "a document starts here" and "a document ends here" is put into the data. Because of the EOS at the end of every training sequence, the model can learn to predict EOS, and generation (10) can stop when it does. The script decides this framing, not the tokenizer: `encode` adds neither marker unless asked.

A tiny real example with the tokenizer currently saved in this project (the middle ids depend on the learned merges; with no applicable merges they are simply the bytes of the text):

```
tokenizer.encode("hello", add_bos=True, add_eos=True)
-> [256, 104, 101, 108, 108, 111, 257]
```

```python
                tokenized_record = {
                    "document_id": record["document_id"],
                    "batch_id": record["batch_id"],
                    "input_ids": token_ids,
                    "num_tokens": len(token_ids),
                }

                output_file.write(
                    json.dumps(
                        tokenized_record,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                document_count += 1
                token_count += len(token_ids)
```

A new record is built with the two identifying fields copied over, the id list, and its length. The `text` field is deliberately left out — the tokenized file is purely numeric. `record["document_id"]` and `record["batch_id"]` use square brackets, so a dataset line missing either field raises `KeyError`.

`json.dumps` writes a Python list of integers as a JSON array, e.g. `"input_ids": [256, 104, 101, 108, 108, 111, 257]`. The counters add one document and `len(token_ids)` tokens. Note that `num_tokens` and the printed `tokens=` total **include** the BOS and EOS of every document.

```python
        print(
            f"{split}: "
            f"documents={document_count}, "
            f"tokens={token_count}"
        )
```

This `print` is indented at the level of the `for split` loop, outside the `with` block: it runs once per split, after that split's output file has been closed.

**Running it twice.** Safe; the three files are rewritten from scratch. It must be re-run whenever either input changes — a rebuilt dataset *or* a retrained tokenizer.

**Empty or missing input.** An empty input split (normal for validation and test on a tiny corpus) gives an empty output file and the line `validation: documents=0, tokens=0`. A **missing** input split is handled less gracefully because of the order of operations: the output file is opened — and emptied — first, and only then does `load_jsonl` try to open the input and fail with `FileNotFoundError`. The script stops there, leaving that split's tokenized file empty and any later splits unprocessed.

---

### 12.14 `python -m scripts.train`

#### `scripts/train.py`

**Command.** No arguments. All settings come from `configs/training.json`.

```
python -m scripts.train
```

**Why this file exists.** The training loop itself is `train()` in `src/training/trainer.py` (8). This script is the assembly around it: load the settings, build an untrained model, open a run record, fetch a checkpoint to resume from if there is one, call `train`, close the run record, and print a summary. The *order* of those steps is decided here and has visible consequences.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `configs/training.json` with at least `epochs` and `learning_rate`; `storage/training/tokenized/train.jsonl` (12.13) with at least one document of two or more tokens. `validation.jsonl` is optional. |
| Reads | The config; the tokenized train and validation files; `artifacts/checkpoints/tiny_model.pt` if present and `resume` is not `false`. It does **not** read `tokenizer.json`. |
| Writes | `artifacts/runs/run_<YYYYMMDDTHHMMSSZ>_<hex8>/run.json` (always, even when no training happens). Through `train`: `artifacts/checkpoints/tiny_model.pt`, history copies `checkpoint_epoch_<6 digits>_step_<9 digits>.pt`, and `best_tiny_model.pt` whenever a validation loss improves. |
| Prints | `Run: <run id>`; from `train`: an optional `Resuming from epoch …` line, `Device: …`, one `Epoch NNN \| loss=… \| steps=… \| tokens_seen=…` line per epoch (plus a validation line when validation examples exist), or `Training already completed N/N epochs.`; then the script's summary: checkpoint path, epochs completed, global steps, tokens seen, run metadata path. |

**How it connects.** Consumes the tokenized dataset. Its checkpoint is what `scripts.evaluate`, `scripts.inference`, `scripts.model_stats` and the server load.

**The code, section by section.**

```python
from paths import (
    TRAINING_DATA_DIR,
    CHECKPOINT_PATH,
    RUNS_DIR,
)

from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.training.checkpoint import load_checkpoint
from src.training.config import load_training_config
from src.training.run import create_run, finish_run
from src.training.trainer import get_device, train
```

- `ModelConfig` (7) is a frozen dataclass of six numbers describing the model's shape, with defaults `vocab_size=300`, `context_length=128`, `d_model=128`, `num_heads=4`, `num_layers=4`, `dropout=0.0`.
- `TinyLLM(config)` (7) builds the model with freshly initialised random weights.
- `load_checkpoint(path, device)` (8) returns the saved checkpoint dict, or `None` when the file does not exist.
- `load_training_config()` (8) parses `configs/training.json` into a dict; it raises `FileNotFoundError` if the file is missing.
- `create_run(...)` and `finish_run(...)` (8) write and then complete a small JSON record describing one invocation of training.
- `get_device()` (8) returns the best available device: `cuda`, else `mps` (Apple Silicon), else `cpu`.
- `train(...)` (8) runs the epochs, saves checkpoints, and returns a dict of statistics.

```python
TRAIN_PATH = (
    TRAINING_DATA_DIR
    / "tokenized"
    / "train.jsonl"
)

VALIDATION_PATH = (
    TRAINING_DATA_DIR
    / "tokenized"
    / "validation.jsonl"
)
```

The two tokenized files the script will hand to `train`. They are built from `TRAINING_DATA_DIR` at import time; the strings `"tokenized"`, `"train.jsonl"` and `"validation.jsonl"` must match what 12.13 wrote.

```python
if __name__ == "__main__":
    training_config = load_training_config()

    model_config = ModelConfig()

    model = TinyLLM(
        model_config
    )

    device = get_device()
```

Four objects are created, in this order:

1. `training_config` — a plain dict. With the file as it is now: `epochs: 21`, `learning_rate: 0.0003`, `resume: true`, `checkpoint_every_epochs: 1`, `keep_last_checkpoints: 3`.
2. `model_config = ModelConfig()` — **all defaults**. No argument is passed, nothing is read from a file, and the tokenizer is not consulted. The model's shape, including `vocab_size`, is whatever `src/model/config.py` says.
3. `model = TinyLLM(model_config)` — a new model with random weights, on the CPU.
4. `device` — used in this script for two things only: the run record and loading the checkpoint. `train` works out the device again by itself and moves the model there.

```python
    model_config_dict = {
        "vocab_size": model_config.vocab_size,
        "context_length": model_config.context_length,
        "d_model": model_config.d_model,
        "num_heads": model_config.num_heads,
        "num_layers": model_config.num_layers,
        "dropout": model_config.dropout,
    }
```

The dataclass is copied field by field into an ordinary dict so that it can be written into the run record as JSON. (The same six-key dict is built again inside `save_checkpoint`.)

```python
    # -----------------------------------------
    # Create training run
    # -----------------------------------------

    run_id, run_path = create_run(
        runs_dir=RUNS_DIR,
        device=str(device),
        checkpoint_path=CHECKPOINT_PATH,
        model_config=model_config_dict,
        training_config=training_config,
    )

    print(f"Run: {run_id}")
```

`create_run` makes a new directory under `artifacts/runs/` named with the current UTC time and eight random hex characters, writes `run.json` with `"status": "running"` plus the device, checkpoint path and both config dicts, and returns `(run_id, run_path)`. The two-names-on-the-left form unpacks that tuple. `str(device)` turns the device object into text such as `"mps"`.

**What it means in the pipeline.** The run record is opened **before** training starts and before the checkpoint is even looked at. So there is a record on disk for every time the command was started, including starts that later crash. A run that crashes keeps `"status": "running"` forever, because the only code that changes the status is `finish_run`, further down, and nothing here catches errors. A `run.json` that says "running" when no training process is alive therefore means "this run did not finish".

```python
    # -----------------------------------------
    # Resume
    # -----------------------------------------

    resume_checkpoint = None

    if training_config.get(
        "resume",
        True,
    ):
        resume_checkpoint = load_checkpoint(
            CHECKPOINT_PATH,
            device,
        )
```

`resume_checkpoint` starts as `None`. `training_config.get("resume", True)` reads the `resume` setting and treats a missing setting as `True`. If resuming is on, `load_checkpoint` returns the dict stored in `artifacts/checkpoints/tiny_model.pt`, or `None` if there is no such file. The variable is therefore `None` in two situations — resume switched off, or nothing to resume from — and in both the model simply starts from its random weights.

With `"resume": false` an existing checkpoint is not deleted at this point; it is ignored, and then overwritten at the first checkpoint save of the new training.

```python
    # -----------------------------------------
    # Train
    # -----------------------------------------

    training_stats = train(
        model=model,
        config=model_config,
        train_path=TRAIN_PATH,
        epochs=training_config["epochs"],
        learning_rate=training_config["learning_rate"],
        checkpoint_path=CHECKPOINT_PATH,
        training_config=training_config,
        resume_checkpoint=resume_checkpoint,
        validation_path=VALIDATION_PATH,
    )
```

The single call that does the work. Each argument:

| Argument | Value | Used in `train` for |
|---|---|---|
| `model` | the untrained `TinyLLM` | receives the checkpoint's weights if resuming, then is trained in place |
| `config` | `model_config` | `context_length` (how sequences are cut) and `vocab_size` (reshaping for the loss) |
| `train_path` | tokenized train file | the examples for every epoch |
| `epochs` | `training_config["epochs"]` | the **total** number of epochs to reach, not "how many more" |
| `learning_rate` | `training_config["learning_rate"]` | the AdamW optimizer |
| `checkpoint_path` | `artifacts/checkpoints/tiny_model.pt` | where the latest checkpoint is saved |
| `training_config` | the whole dict | `checkpoint_every_epochs`, `keep_last_checkpoints`; also stored inside the checkpoint |
| `resume_checkpoint` | dict or `None` | restoring weights, optimizer state and counters |
| `validation_path` | tokenized validation file | validation loss at each checkpoint, which decides "best" |

`training_config["epochs"]` and `["learning_rate"]` use square brackets: these two settings are required, and a config without them fails here with `KeyError`. The other settings are read with `.get` and have defaults.

`train` returns `training_stats`, a dict with `epochs_completed`, `global_step`, `tokens_seen`, `training_seconds`, `final_loss`, `validation_loss`, `best_validation_loss`, `learning_rate`.

Because `epochs` is a total, the meaning of running the command again depends on the checkpoint: if it says 21 epochs are done and the config says 21, `train` prints `Training already completed 21/21 epochs.` and returns the old counters without touching the checkpoint. To train longer you raise `epochs` in the config and run the same command.

```python
    # -----------------------------------------
    # Model stats
    # -----------------------------------------

    model_stats = {
        "total_parameters": sum(
            parameter.numel()
            for parameter in model.parameters()
        ),

        "trainable_parameters": sum(
            parameter.numel()
            for parameter in model.parameters()
            if parameter.requires_grad
        ),
    }
```

Two numbers computed by the script itself.

**What PyTorch does.** `model.parameters()` yields every learnable tensor in the model (each weight matrix, each bias vector). `.numel()` is "number of elements": a `[300, 128]` matrix has `300 × 128 = 38,400`. `sum(...)` over a generator expression adds them all. The second sum has a filter, `if parameter.requires_grad`, keeping only tensors that training is allowed to change.

**What it means for the model.** "Total parameters" is the size of the model — the count of individual numbers that training adjusts. In this project nothing is frozen, so the two sums are equal. The same computation appears in `scripts/model_stats.py` and inside `save_checkpoint`.

```python
    # -----------------------------------------
    # Finish run
    # -----------------------------------------

    finish_run(
        run_path=run_path,
        training_stats=training_stats,
        model_stats=model_stats,
    )
```

`finish_run` re-reads `run.json`, sets `"status": "completed"`, adds `finished_at`, `training_stats` and `model_stats`, and replaces the file (written to a temporary file first, then renamed — see 8).

```python
    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print()
    print(f"Checkpoint: {CHECKPOINT_PATH}")

    print(
        f"Epochs completed: "
        f"{training_stats['epochs_completed']}"
    )

    print(
        f"Global steps: "
        f"{training_stats['global_step']:,}"
    )

    print(
        f"Tokens seen: "
        f"{training_stats['tokens_seen']:,}"
    )

    print(
        f"Run metadata: {run_path}"
    )
```

The summary. `:,` inside an f-string formats an integer with thousands separators (`5418` → `5,418`). `CHECKPOINT_PATH` and `run_path` are printed as full paths.

**Running it twice.** Designed for it, and three cases are worth separating:

- *Checkpoint has fewer epochs than the config asks for* → training continues from the saved epoch to the configured total.
- *Checkpoint already at the configured total* → no training; the checkpoint is left alone. A new run directory is still created and still marked `completed`, with the old counters copied in. So the number of directories in `artifacts/runs/` counts invocations, not trainings.
- *No checkpoint, or `resume` is `false`* → training from random weights; `tiny_model.pt` is overwritten.

One thing to keep in mind when resuming: the model is built from `ModelConfig()` defaults, and the checkpoint's own stored `config` is not compared with it. If you change a default in `src/model/config.py` and then resume, the saved weights no longer fit the new shapes and `load_state_dict` fails with a size-mismatch error — after the run record has already been created.

**Empty or missing input.** Missing `configs/training.json` → `FileNotFoundError` before anything is created. Missing `tokenized/train.jsonl` → `FileNotFoundError` in the first epoch. A train file that yields no examples (empty, or every document shorter than two tokens) → `ValueError: No training examples were produced`. In those last two cases a `run.json` with status `running` is left behind. A missing or empty `validation.jsonl` is not an error: training proceeds, there is simply no validation loss and no "best" checkpoint.

---

### 12.15 `python -m scripts.evaluate`

#### `scripts/evaluate.py`

**Command.** No arguments.

```
python -m scripts.evaluate
```

**Why this file exists.** Measures how well the saved model predicts the next token on each of the three splits and prints loss and perplexity. The measuring is `evaluate()` in `src/evaluation/evaluator.py` (9); the script rebuilds the model from the checkpoint and loops over the splits.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `artifacts/checkpoints/tiny_model.pt` (12.14) and the three tokenized files (12.13). |
| Writes | Nothing. There is no write call in the script or in `evaluate`. |
| Prints | Per split: `<split>: loss=…, perplexity=…, steps=…` or `<split>: no evaluation examples`. |

**How it connects.** A read-only check after training. Nothing consumes its output.

**The code, section by section.**

```python
import torch

from paths import (
    CHECKPOINT_PATH,
    TRAINING_DATA_DIR,
)
from src.evaluation.evaluator import evaluate
from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.training.trainer import get_device
```

`torch` is PyTorch (7); here it is needed for `torch.load`. `evaluate(model, config, dataset_path, device)` (9) puts the model in evaluation mode, runs every example of the file through it without computing gradients, and returns a dict: `available` (False if the file produced no examples), `loss` (the average cross-entropy), `perplexity` (`e` raised to that loss), and `steps` (how many chunks were scored).

```python
if __name__ == "__main__":
    device = get_device()

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device,
    )

    config = ModelConfig(
        **checkpoint["config"]
    )

    model = TinyLLM(config)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
```

The "rebuild a model from a checkpoint" sequence. You will see the same five steps in 12.16:

1. `torch.load(CHECKPOINT_PATH, map_location=device)` reads the checkpoint file back into a Python dict. `map_location` says where to place the tensors — a checkpoint saved on one device can be opened on another.
2. `ModelConfig(**checkpoint["config"])`. The checkpoint stores the six shape numbers as a dict. `**` unpacks a dict into keyword arguments, so this is the same as writing `ModelConfig(vocab_size=300, context_length=128, …)` with the saved values.
3. `TinyLLM(config)` builds a model of exactly that shape, with random weights.
4. `model.load_state_dict(checkpoint["model_state_dict"])` copies the saved weights over the random ones. This only works because step 2 recreated the same shapes.
5. `model.to(device)` moves the model to the device.

**What it means in the pipeline.** Unlike `scripts.train`, this script takes the model's shape **from the checkpoint**, not from the defaults in `src/model/config.py`. A checkpoint is self-describing for evaluation and inference: it carries the shape needed to open it.

The file loaded is `tiny_model.pt`, the *latest* checkpoint. `best_tiny_model.pt` and the history files are not looked at by this script.

```python
    TOKENIZED_DIR = (
        TRAINING_DATA_DIR
        / "tokenized"
    )

    for split in (
        "train",
        "validation",
        "test",
    ):
        result = evaluate(
            model=model,
            config=config,
            dataset_path=TOKENIZED_DIR / f"{split}.jsonl",
            device=device,
        )
```

`TOKENIZED_DIR` is defined inside the main block here (in other scripts the same path is a module-level constant). The loop calls `evaluate` once per split with the matching file.

```python
        if not result["available"]:
            print(
                f"{split}: no evaluation examples"
            )
            continue

        print(
            f"{split}: "
            f"loss={result['loss']:.4f}, "
            f"perplexity={result['perplexity']:.4f}, "
            f"steps={result['steps']}"
        )
```

If the split produced no examples the script says so and moves on. Otherwise it prints three numbers; `:.4f` formats a float with four digits after the decimal point.

Real output with the project in its current state (one training document; validation and test files exist but are empty):

```
train: loss=2.0433, perplexity=7.7162, steps=3
validation: no evaluation examples
test: no evaluation examples
```

How to read it: `steps=3` because the single training document is cut into three chunks of at most 128 positions (12.17 shows the arithmetic). `perplexity=7.7162` is `e^2.0433`. And the `train` line measures the model on the very text it was trained on, so it tells you how well the model has *fitted* that text, not how well it handles new text — only the validation and test lines can tell you that, and with this corpus there is nothing in them yet.

**Running it twice.** Safe; read-only, and the same checkpoint and data give the same numbers.

**Empty or missing input.** No checkpoint → `FileNotFoundError` from `torch.load`. An empty split file → the "no evaluation examples" line. A **missing** split file → `FileNotFoundError` when `evaluate` tries to read it (the script does not check `is_file()` first, unlike the trainer's validation step).

---

### 12.16 `python -m scripts.inference`

#### `scripts/inference.py`

**Command.** Everything after the script name is the prompt.

```
python -m scripts.inference hello
python -m scripts.inference "i love coffee"
python -m scripts.inference i love coffee
```

The second and third forms give the same prompt: all arguments are joined with single spaces. With no argument, a default Arabic prompt written in the file is used.

**Why this file exists.** The shortest path from a prompt to generated text, without a server: load tokenizer and model, call `generate` once, print.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `artifacts/tokenizer/tokenizer.json` (12.12) and `artifacts/checkpoints/tiny_model.pt` (12.14). |
| Writes | Nothing. |
| Prints | `Device: <device>`, a blank line, then the prompt followed by the generated continuation. |

**How it connects.** A read-only use of the trained model. The server (12.18) calls the same `generate` function for its `/generate` route.

**The code, section by section.**

```python
import sys

import torch

from paths import (
    CHECKPOINT_PATH,
    TOKENIZER_PATH,
)
from src.inference.generator import generate
from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.tokenization.tokenizer import Tokenizer
from src.training.trainer import get_device
```

`generate(model, tokenizer, prompt, max_new_tokens, temperature)` (10) encodes the prompt with a BOS in front, then repeatedly asks the model for the next token, appends it, and stops at EOS or after `max_new_tokens`; it returns the decoded text of the whole sequence — prompt included.

```python
if __name__ == "__main__":
    prompt = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "علي حسن"
    )
```

**What Python does.** This is a conditional expression: `A if condition else B`. `sys.argv[1:]` is every command-line word after the script name. If there is at least one (`len(sys.argv) > 1`), they are joined with spaces into one string; otherwise the literal default is used. The parentheses only allow the expression to span several lines.

A detail of joining: the shell splits unquoted words on any amount of whitespace, so `i   love   coffee` typed without quotes arrives as the prompt `i love coffee`. Quote the prompt if exact spacing matters.

```python
    device = get_device()

    tokenizer = Tokenizer.load(
        TOKENIZER_PATH
    )

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device,
    )

    config = ModelConfig(
        **checkpoint["config"]
    )

    model = TinyLLM(config)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
```

`Tokenizer.load` and then the same five-step model rebuild as in 12.15.

```python
    output = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        max_new_tokens=50,
        temperature=0.0,
    )

    print(f"Device: {device}")
    print()
    print(output)
```

Two generation settings are fixed in this script:

- `max_new_tokens=50` — at most fifty tokens are added. Tokens are bytes or merged byte groups (6), so fifty tokens is usually fewer than fifty characters of Arabic.
- `temperature=0.0` — `generate` treats a temperature of zero or less as "always take the single most likely token" (argmax, 10). No randomness is involved, so the same prompt with the same checkpoint always gives the same output.

Real output for the made-up prompt `hello`, with the current checkpoint:

```
Device: mps

hello  مجياتج  مشخصي لييعمسية مس     عع  مس ي غيمسي
```

The line starts with the prompt because `generate` returns prompt plus continuation. The continuation is not meaningful language — this checkpoint has seen one short document for 63 optimizer steps — but notice what *is* right about it: every character is a complete, valid character. That is the UTF-8 constraint from 10 at work; without it a model at this stage would regularly emit half an Arabic letter.

**Running it twice.** Safe and, with temperature `0.0`, identical every time.

**Empty or missing input.** No arguments → the default prompt. An argument that is an empty string (`""`) → an empty prompt; generation then starts from BOS alone. Missing tokenizer or checkpoint → `FileNotFoundError`.

---

### 12.17 `python -m scripts.model_stats`

#### `scripts/model_stats.py`

**Command.** No arguments.

```
python -m scripts.model_stats
```

**Why this file exists.** A one-screen answer to "how big is the model, and how much data does one epoch contain?". Unlike most scripts here, nearly all of its logic is its own: two counting functions and a size calculation.

**What enters / what leaves.**

| | |
|---|---|
| Needs | `artifacts/checkpoints/tiny_model.pt` (12.14), `artifacts/tokenizer/tokenizer.json` (12.12), `storage/training/tokenized/train.jsonl` (12.13). |
| Writes | Nothing. The file contains only loads, counting and `print` calls. |
| Prints | The table shown below. |

**How it connects.** Read-only. Nothing depends on it.

Real output with the project in its current state:

```
JSM MODEL STATS
--------------------------
Parameters:       884,480
Trainable params: 884,480
Model FP32 size:  3.37 MB

Vocabulary:       300
Context length:   128
d_model:          128
Attention heads:  4
Layers:           4

Train documents:  1
Dataset tokens:   259
Prediction tokens/epoch: 258
Steps/epoch:      3
```

**The code, section by section.**

```python
import json

import torch

from paths import (
    CHECKPOINT_PATH,
    TOKENIZER_PATH,
    TRAINING_DATA_DIR,
)
from src.dataset.loader import load_token_sequences
from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.tokenization.tokenizer import Tokenizer


TRAIN_PATH = (
    TRAINING_DATA_DIR
    / "tokenized"
    / "train.jsonl"
)
```

`load_token_sequences(path)` (5) is a generator that yields the `input_ids` list of each record in a tokenized JSONL file. `json` is imported and not used in this file.

```python
def count_parameters(model):
    total = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return total, trainable
```

`count_parameters(model)` returns two integers as a tuple — the same two sums explained in 12.14: every element of every learnable tensor, and the subset that training may change.

Where 884,480 comes from, for the saved shape (`vocab_size=300`, `context_length=128`, `d_model=128`, 4 layers), using the tensor sizes the model actually reports:

| Part (7) | Tensors | Elements |
|---|---|---|
| Token embedding | `[300, 128]` | 38,400 |
| Position embedding | `[128, 128]` | 16,384 |
| One transformer block | two LayerNorms (4 × 128), four attention projections (4 × 128 × 128, no bias), feed-forward `[512, 128]` + 512 and `[128, 512]` + 128 | 197,760 |
| Four blocks | 4 × 197,760 | 791,040 |
| Final LayerNorm | weight 128 + bias 128 | 256 |
| Output head | `[300, 128]`, no bias | 38,400 |
| **Total** | | **884,480** |

So almost nine tenths of the model is in the four blocks, and each `vocab_size`-dependent table (the embedding at the entrance and the head at the exit) costs `vocab_size × d_model` numbers.

```python
def count_dataset_tokens(path):
    documents = 0
    stored_tokens = 0
    prediction_tokens = 0
    steps = 0

    context_length = 128

    for token_ids in load_token_sequences(path):
        documents += 1
        stored_tokens += len(token_ids)

        if len(token_ids) < 2:
            continue

        prediction_tokens += len(token_ids) - 1
```

`count_dataset_tokens(path)` walks the tokenized training file once and keeps four counters.

- `documents` — one per record.
- `stored_tokens` — the length of every `input_ids` list, added up. This includes each document's BOS and EOS.
- `prediction_tokens` — `len(token_ids) - 1` per document.

**What it means for the model.** A sequence of `n` tokens contains `n − 1` next-token questions: given token 1 predict token 2, …, given token `n−1` predict token `n`. The first token (BOS) is never a *target* because nothing comes before it. That is why "prediction tokens" is always exactly one less per document than "stored tokens": here `259 − 1 = 258`. A document with fewer than two tokens offers no question at all; `continue` skips it after it has been counted as a document and its tokens counted as stored.

`context_length = 128` is a **local literal**. The function does not receive the model's configuration; it assumes the same number that `ModelConfig` uses by default. If a checkpoint had a different context length, the "Context length" line of the output would show the checkpoint's value while "Steps/epoch" would still be computed with 128.

```python
        for start in range(
            0,
            len(token_ids) - 1,
            context_length,
        ):
            chunk = token_ids[
                start:start + context_length + 1
            ]

            if len(chunk) >= 2:
                steps += 1

    return {
        "documents": documents,
        "stored_tokens": stored_tokens,
        "prediction_tokens_per_epoch": prediction_tokens,
        "steps_per_epoch": steps,
    }
```

The inner loop re-enacts how the trainer cuts a document into training examples — it is a copy of the loop in `make_training_examples` (5), with the tensor-building replaced by `steps += 1`.

**What Python does.** `range(0, len(token_ids) - 1, context_length)` produces start positions `0, 128, 256, …` that are less than `n − 1`. For each start, the slice `token_ids[start:start + context_length + 1]` takes up to 129 tokens — 128 inputs plus one extra so that the last input also has a target. A slice past the end of a list is simply shorter, never an error. Each slice with at least two tokens counts as one step.

**What it means for training.** The trainer feeds one such chunk per optimizer step (batch size 1), so this count is the number of weight updates in one epoch. For the current data: `n = 259`, starts at `0`, `128`, `256`, giving chunks of 129, 129 and 3 tokens — **3 steps**, containing `128 + 128 + 2 = 258` targets, which agrees with the prediction-token count. It also agrees with what training recorded: the saved checkpoint reports 21 epochs, 63 global steps (`21 × 3`) and 5,418 tokens seen (`21 × 258`).

The function returns its four counters in a dict.

```python
if __name__ == "__main__":
    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location="cpu",
    )

    config = ModelConfig(
        **checkpoint["config"]
    )

    model = TinyLLM(config)

    total_params, trainable_params = (
        count_parameters(model)
    )
```

**What PyTorch does.** `torch.load(..., map_location="cpu")` reads the checkpoint onto the CPU regardless of where it was saved; no accelerator is needed for counting. The model is then built from the checkpoint's `config`.

Notice what is **absent** compared with 12.15 and 12.16: there is no `load_state_dict`. The model counted here has the checkpoint's *shape* but fresh random *values*. That is fine for this purpose — the number of parameters depends only on the shapes — but it means the checkpoint is being used purely as the place where the shape is recorded. Its weights are loaded from disk into the `checkpoint` dict and then not used.

```python
    tokenizer = Tokenizer.load(
        TOKENIZER_PATH
    )

    dataset = count_dataset_tokens(
        TRAIN_PATH
    )

    model_bytes = sum(
        parameter.numel()
        * parameter.element_size()
        for parameter in model.parameters()
    )
```

The tokenizer is loaded only to read `tokenizer.vocab_size` later. The dataset counters are computed.

`model_bytes` — **What PyTorch does.** `parameter.element_size()` is the number of bytes one element of that tensor occupies. Model weights are 32-bit floating-point numbers ("FP32", `float32`), so it is `4` for every tensor here. `numel() × element_size()` is the tensor's size in bytes; the sum covers the whole model.

**What it means.** `884,480 × 4 = 3,537,920` bytes; divided by 1024 twice, `3.37 MB`. This is the memory the weights themselves need. The checkpoint file on disk is about three times larger (roughly 10.7 MB) because it also stores the optimizer's state — AdamW keeps two extra numbers for every parameter (8) — plus the configs and statistics.

```python
    print("JSM MODEL STATS")
    print("--------------------------")

    print(f"Parameters:       {total_params:,}")
    print(f"Trainable params: {trainable_params:,}")
    print(
        f"Model FP32 size:  "
        f"{model_bytes / 1024 / 1024:.2f} MB"
    )

    print()
    print(f"Vocabulary:       {tokenizer.vocab_size:,}")
    print(f"Context length:   {config.context_length}")
    print(f"d_model:          {config.d_model}")
    print(f"Attention heads:  {config.num_heads}")
    print(f"Layers:           {config.num_layers}")
```

The first two blocks of the output. `{total_params:,}` adds thousands separators; `:.2f` prints two decimals. The spaces inside the string literals are there to line the values up in a column.

Two sources are mixed in the second block, and it is worth knowing which is which:

| Line | Comes from |
|---|---|
| `Vocabulary` | `tokenizer.vocab_size` — computed from `tokenizer.json` as `259 + number of merges` |
| `Context length`, `d_model`, `Attention heads`, `Layers` | `config`, i.e. the shape stored in the checkpoint |

The model's own `config.vocab_size` is never printed. Today both are 300. If the tokenizer had stopped learning merges early (say at 290), this line would read 290 while the model's embedding table would still have 300 rows; the difference would be invisible in this output.

```python
    print()
    print(
        f"Train documents:  "
        f"{dataset['documents']:,}"
    )
    print(
        f"Dataset tokens:   "
        f"{dataset['stored_tokens']:,}"
    )
    print(
        f"Prediction tokens/epoch: "
        f"{dataset['prediction_tokens_per_epoch']:,}"
    )
    print(
        f"Steps/epoch:      "
        f"{dataset['steps_per_epoch']:,}"
    )
```

The third block prints the four counters from `count_dataset_tokens`:

| Line | Meaning | Current value |
|---|---|---|
| `Train documents` | records in the tokenized train file | 1 |
| `Dataset tokens` | all stored token ids, BOS and EOS included | 259 |
| `Prediction tokens/epoch` | next-token targets the model is trained on in one pass | 258 |
| `Steps/epoch` | optimizer updates in one pass (one chunk per step) | 3 |

Put the first and last blocks side by side and you have the most important fact about the project's current state: 884,480 adjustable numbers are being fitted to 258 prediction targets. A model with thousands of times more parameters than training targets can only memorise; that is what the loss and the sample output in 12.15 and 12.16 are showing.

**Running it twice.** Safe; read-only and deterministic.

**Empty or missing input.** Any of the three files missing → `FileNotFoundError`. An empty tokenized train file → the dataset block shows four zeros and the rest prints normally.

---

### 12.18 `python -m scripts.serve`

#### `scripts/serve.py`

**Command.** No arguments.

```
python -m scripts.serve
```

**Why this file exists.** Starts the web server that exposes the model over HTTP. It is the smallest script: nine lines, no project imports.

**What enters / what leaves.**

| | |
|---|---|
| Needs | The Python packages `uvicorn` and `fastapi`. For useful answers: a tokenizer and at least one checkpoint under `artifacts/checkpoints/`. Port 8000 must be free. |
| Writes | Nothing on disk. |
| Prints | The server's start-up lines and then one access-log line per HTTP request. It does not return until you stop it with `Ctrl+C`. |

**How it connects.** The last link: a long-running process instead of a one-shot command. Everything it serves is defined in `src/serving/server.py` (11).

**The code, section by section.**

```python
import uvicorn
```

`uvicorn` is a third-party web server program for Python applications of the kind FastAPI produces. FastAPI (11) defines *what* the routes do; uvicorn is what actually listens on a network port and passes requests to it.

```python
if __name__ == "__main__":
    uvicorn.run(
        "src.serving.server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
```

`uvicorn.run` takes:

- `"src.serving.server:app"` — an *import string*, not an object. It means "import the module `src.serving.server` and use the variable named `app` in it". The script itself never imports the server module; uvicorn does, at start-up. That import is the moment the server code in 11 runs for the first time: the device is chosen, the model manager is created, the routes are registered, and the built web apps are mounted if their build folders exist.
- `host="127.0.0.1"` — listen on the loopback address only. The server is reachable from this computer and not from other machines on the network.
- `port=8000` — the port number; with the host, this gives the address `http://127.0.0.1:8000`.
- `reload=False` — do not watch source files for changes. After editing Python code, or after building the web apps for the first time, you stop the server and start it again to pick up the change.

All four values are literals. There is no option to choose another port or host from the command line.

**Running it twice.** The second copy cannot bind the port while the first is running; uvicorn reports that the address is already in use and exits. The first copy is unaffected.

**Empty or missing input.** The server starts even with no checkpoint at all — the model is only needed when a request asks for it, and the `/generate` route answers with an error status in that case (11).

---

### 12.19 The author's command notes: `scripts/README.md`

`scripts/README.md` is a 90-line plain list of the commands above in run order, followed by notes on the web apps. It is not reproduced here. Checked line by line against the scripts, **every `python -m scripts.…` command in it is valid as written**: the names exist, the order is the pipeline order, and the arguments match what each script reads. The things that would trip someone following it literally:

| Where | What it says | What to know |
|---|---|---|
| line 5 | `python -m scripts.provenance_review <a specific batch id> allowed owned_data` | The batch id is a literal one from the author's own storage. It exists on this machine today, so the line works here. Batch ids contain a timestamp and a random suffix (12.1), so on any other machine, or after the uploads are acquired again, that id will not exist — and as explained in 12.4 the command will still succeed and write a decision for the non-existent batch. Use the id that 12.1 or 12.3 printed. |
| lines 4–6 | `provenance`, `provenance_review`, `provenance` | Correct and intentional: status, decide, confirm. Only one batch gets a decision in the notes; every other batch stays blocked and is not ingested. |
| every command | bare `python -m …` | Each one assumes the current directory is the project root and that the virtual environment is active. The notes say this once, near the bottom (`cd jsm_0.1`, `source .venv/bin/activate`), not at the top. From any other directory the first `from paths import …` fails with `ModuleNotFoundError`. |
| line 21 | `for test :` | A label, not a command. The `python -c "…"` line under it is a real one-line round-trip test of the tokenizer (encode a short Arabic string with BOS and EOS, decode, compare); it runs and prints `PASS` with the current tokenizer. It needs 12.12 to have been run. |
| lines 28–31 | `inference` listed before `evaluate` | Harmless; both only read the checkpoint. |
| line 48 | `python -m scripts.model_stats` | Valid; it just sits after the web-app notes rather than with the other model commands. |
| lines 33–45, 62–90 | `cd apps && npm install && npm run build`, `npm run dev:…` | These are web front-end commands, outside this course. The script names they use (`build`, `dev:website`, `dev:chat`, `dev:admin`) do exist in `apps/package.json`. The dev-server port numbers in the notes were not checked. |
| lines 87–90 | "build and serve everything from one port" ends with `npm run build` | The step that makes this work is missing from that spot: the server decides at start-up whether a built app exists (12.18), so after the first build you must (re)start `python -m scripts.serve`. |
| line 56 | "A copy I started is already running on port 8000…" | A note about one particular moment, not an instruction. If a server is running, starting another fails as described in 12.18; if none is running, you do need the command. |
| lines 36–40 | URLs listed directly under `python -m scripts.serve` | Addresses to open in a browser, not commands. Pasting the whole block into a terminal would produce "command not found" lines for these, for `for test :`, and for the box-drawing table at the end. |

The notes do not mention the optional arguments of `scripts.inspection` (12.2), and they contain no command that the scripts directory lacks.

---

#### What I should understand before moving on

- Every command is `python -m scripts.<name>`, typed from the project root, and the only thing connecting one command to the next is **files on disk**: each script reads the directory the previous one wrote. No script calls another script.
- The scripts are not uniformly "glue". The decisions *which inspection is the latest*, *which files are accepted and allowed*, *what counts as a duplicate across batches*, *how documents are routed into three files*, *that every document is framed with BOS and EOS*, and *how many steps an epoch has* are all made in `scripts/`.
- The file-in/file-out stages (extraction → deduplication) only ever create or overwrite. They never delete. Re-running one of them is safe; re-running an *earlier* stage that changes ids (ingestion) or verdicts (filtering, deduplication) can leave stale files that later stages will still pick up.
- Write behaviour differs by stage and is visible in the code: acquisition and the catalog records are append-only (`exist_ok=False`, exclusive-create modes, new timestamped directories); the processing stages overwrite file by file; the dataset and tokenized files are rebuilt from empty on every run (`"w"`); training resumes.
- `scripts.train` builds the model from the defaults in `src/model/config.py`, while `evaluate`, `inference` and `model_stats` build it from the shape stored inside the checkpoint. The vocabulary size is fixed in two unconnected places: `target_vocab_size=300` in `scripts/tokenizer_training.py` and `vocab_size = 300` in `ModelConfig`.
- Retraining the tokenizer invalidates the tokenized dataset and every checkpoint, because token ids change meaning. The order tokenizer → tokenize → train is a dependency, not just a habit.
- A run record in `artifacts/runs/` is created on every start of `scripts.train`, completed only on a clean finish, and created even when no training is left to do.
- With the corpus as it stands — 1 training document, 258 prediction targets, 884,480 parameters — the pipeline is demonstrating that every stage works end to end, not producing a model that has learned language.

#### Self-test

1. You run `python -m scripts.cleaning` from inside the `scripts/` directory and get `ModuleNotFoundError: No module named 'paths'`. Why, and what is the fix?
2. You add one new file to an upload folder that was acquired last week and run `scripts.acquisition` again. What ends up in `storage/incoming/batches/`, and at which later stage do the repeated old files stop being duplicated?
3. A batch was inspected twice: the first inspection accepted all five files, the second (after a policy change) accepted three. Which files does `scripts.ingestion` copy, and what in the code makes it so?
4. You record a provenance decision but mistype the batch id. What does `scripts.provenance_review` do, and how would you notice?
5. `scripts.filtering` rejected a document today that it accepted yesterday. After today's run, is that document in `storage/processed/filtered/`? Explain from the code.
6. Why does `scripts/dataset_building.py` collect the full list of documents before writing any record, when every earlier stage handles one file at a time?
7. `configs/training.json` says `"epochs": 21` and the checkpoint on disk already records 21 completed epochs. Describe everything that happens, on screen and on disk, when you run `python -m scripts.train`.
8. `scripts.model_stats` reports `Dataset tokens: 259`, `Prediction tokens/epoch: 258`, `Steps/epoch: 3`. Derive the second and third numbers from the first, given a context length of 128.

<details><summary>Answers</summary>

1. The scripts import `paths` and `src…` as top-level modules, and `python -m` puts the *current directory* on the import path. From inside `scripts/` there is no `paths.py` in the current directory. Change to the project root (the directory containing `paths.py`) and run the same command there.
2. The folder's fingerprint is `(platform, sorted tuple of all file hashes)`. One more file means a different tuple, so the fingerprint is not in the set of existing ones and the **whole folder** is acquired as a new batch; last week's batch is untouched. Both batches now hold copies of the old files. They travel through inspection, ingestion, extraction, cleaning, normalization and filtering as separate documents, and are collapsed at `scripts.deduplication`, whose `seen_hashes` set spans all batches and keeps only the first copy of each identical text.
3. Only the three accepted by the second inspection. `load_latest_inspections` iterates the record directories in sorted order — names begin with a timestamp, so that is chronological order — and stores each under `latest[batch_id]`, so the later record overwrites the earlier. The main loop then copies only artifacts whose `decision` is exactly `accepted_for_ingestion` in that surviving record (and only if the provenance gate allows the batch).
4. It succeeds: neither the script nor `write_rights_decision` checks that the batch exists, so a valid decision record is written for a batch id nobody has. The real batch has no decision, so it stays blocked. You notice by running `python -m scripts.provenance` afterwards and still seeing `BLOCK: <real batch> — training use status: review_required`, or by `scripts.ingestion` printing the same `BLOCK` line.
5. Yes, yesterday's copy is still there. For a rejected document the loop prints `FILTERED OUT` and `continue`s; it reaches no code that removes anything. The script only writes accepted files, it never deletes previously written ones, so the stale file remains and the next stages will read it.
6. Because of the rule in `assign_splits` that train must not be empty: whether to apply the "put everything in train" fallback depends on the splits of *all* documents, so every id has to be known before the first record can be routed. The list holds only names and paths, not texts, so this costs little memory.
7. The config is loaded; an untrained model is built from `ModelConfig()` defaults; a new directory `artifacts/runs/run_<stamp>_<hex8>/` is created with `run.json` at status `running`, and `Run: <id>` is printed. Because `resume` is true, the checkpoint is loaded. Inside `train`, the weights and counters are restored and it prints `Resuming from epoch 21, …`, `Device: …`, then `Training already completed 21/21 epochs.` and returns the old statistics without running an epoch or saving a checkpoint. The script counts the parameters, `finish_run` sets the run to `completed` with those old statistics, and the summary lines are printed. Net effect on disk: one extra run directory; the checkpoint files are unchanged.
8. Prediction tokens: a sequence of `n` tokens has `n − 1` next-token targets (the first token has no predecessor), and there is one document, so `259 − 1 = 258`. Steps: chunk starts are `range(0, 258, 128)` = `0, 128, 256`; each chunk is `token_ids[start:start+129]`, giving lengths 129, 129 and 3, all at least 2 — three steps. Check: the chunks contain `128 + 128 + 2 = 258` targets.

</details>

---

## 13. End to end: from an uploaded file to a live response

This chapter adds no new code. It follows one text file through every stage in order, naming the command you run, the code that does the work, and where the result lands. Each step points back to the chapter that explains it.

| | |
|---|---|
| **INPUT** | One source file placed under `storage/uploads/`. |
| **PROCESS** | Seventeen commands, each reading what the previous one wrote. |
| **OUTPUT** | A JSON response from `POST /generate` containing text the model produced. |
| **WHY IT EXISTS** | To see the whole system as one chain before studying improvements to any single link. |

### 13.1 The data half: from upload to dataset

**1. Upload.** You put a file, or a folder of files with an `origin.json` describing where they came from, under `storage/uploads/`. Nothing has run yet. This folder is the only place a human puts data by hand.

**2. Acquisition** — `python -m scripts.acquisition` (chapter 4.1). The files are copied byte for byte into a new batch folder under `storage/incoming/batches/<batch id>/objects/`, and each copy is hashed with SHA-256. A source manifest listing every file, its size and its hash is written next to them, with a checksum of the manifest itself. From here on the data is identified by its **batch id**, and the copies are never edited.

**3. Inspection** — `python -m scripts.inspection` (chapter 4.2). Each incoming batch is checked against the limits in `configs/inspection.json`: sizes, counts, allowed file types, whether the bytes match what the file claims to be, and the deeper structural checks. The result is an inspection record under `storage/catalog/inspections/`. A batch that fails is recorded under `storage/quarantine/` and goes no further.

**4. Provenance** — `python -m scripts.provenance`, then `python -m scripts.provenance_review <batch id> <decision> <basis>`, then `python -m scripts.provenance` again (chapter 4.3). Passing inspection says a batch is safe to open; it does not say you are allowed to train on it. The gate looks at what is known about the batch's origin and licence. A person records the decision with the review command, and the decision is stored under `storage/catalog/provenance/`. Only batches whose decision allows training use move on.

**5. Ingestion** — `python -m scripts.ingestion` (chapter 4.4). Approved batches are copied from `storage/incoming/` into `storage/raw/<batch id>/objects/`. Each file receives a **document id**, and a raw manifest with its checksum is written. `storage/raw/` is the trusted store: everything in it has passed inspection and provenance.

**6. Extraction** — `python -m scripts.extraction` (chapter 4.5). Each raw document is turned into plain text and written to `storage/extracted/<batch id>/<document id>.txt`. Today only `.txt` files have a working reader.

**7. Cleaning → 8. Normalization → 9. Filtering → 10. Deduplication** — `python -m scripts.cleaning`, `scripts.normalization`, `scripts.filtering`, `scripts.deduplication` (chapter 4.6). Four small passes, each reading the previous folder and writing its own under `storage/processed/`: `cleaned/`, `normalized/`, `filtered/`, `deduplicated/`. Cleaning and normalization change the text. Filtering and deduplication change nothing inside a document; they decide whether the document continues.

**11. Dataset building** — `python -m scripts.dataset_building` (chapter 5). Every surviving document becomes one line of JSON holding its document id, batch id and text. The document id is hashed to choose a split, and the line is appended to `train.jsonl`, `validation.jsonl` or `test.jsonl` under `storage/training/dataset/`. If the hash split would leave the training file empty, every document goes to train.

At this point the corpus factory is finished. Everything after this is the model side, and it reads only `storage/training/`.

### 13.2 The model half: from dataset to checkpoint

**12. Tokenizer training** — `python -m scripts.tokenizer_training` (chapter 6). The training texts are turned into bytes, and byte-pair encoding repeatedly merges the most frequent adjacent pair into a new token until the vocabulary reaches 300. The merge list is saved to `artifacts/tokenizer/tokenizer.json`. This is the first *learned* artifact in the project, and it is learned only from the training split.

**13. Tokenizing the dataset** — `python -m scripts.tokenize_dataset` (chapters 5 and 6). Each document's text is encoded into token ids with a BOS id in front and an EOS id at the end, and written to `storage/training/tokenized/<split>.jsonl`. The model never sees text again; from here on it sees integers.

**14. Training** — `python -m scripts.train` (chapters 7 and 8). The script builds a `TinyLLM` with random weights, or restores the latest checkpoint if resume is on. Then, for each epoch:

1. The token ids of each document are cut into windows of at most `context_length` tokens. Each window gives an input `x` and a target `y`, where `y` is `x` moved one position to the left: the target at every position is the token that actually came next.
2. `x` goes through the **embeddings**, which turn each id and each position into a vector of `d_model` numbers.
3. The vectors pass through the stack of **transformer blocks**. In each block, attention lets every position gather information from earlier positions (the causal mask hides later ones), and the feed-forward network transforms the result.
4. The output head turns each position's vector into **logits**: one score per token in the vocabulary.
5. **Cross-entropy loss** compares those scores with the true next tokens and produces one number: how wrong the model was.
6. `loss.backward()` computes, for every one of the model's parameters, which direction would reduce that number. This is **backpropagation**.
7. `optimizer.step()` lets **AdamW** move every parameter a small step in that direction.

After each checkpointed epoch the trainer saves a **checkpoint** under `artifacts/checkpoints/`: the weights, the optimizer state, the model and training configuration, and the running counters. The run is recorded in `artifacts/runs/<run id>/run.json`.

**15. Evaluation** — `python -m scripts.evaluate` (chapter 9). The saved model is run over each tokenized split with gradients switched off, and the average loss and its perplexity are printed. A split with no examples is reported as unavailable.

### 13.3 The serving half: from checkpoint to response

**16. Inference** — `python -m scripts.inference "<prompt>"` (chapter 10). This is the same generation code the server uses, run once from the terminal. It is the quickest way to see what a checkpoint produces.

**17. Serving** — `python -m scripts.serve` (chapter 11). A FastAPI server starts on `http://127.0.0.1:8000`. It does not load a model at startup; it only prepares a `ModelManager` that knows where checkpoints live.

When a client sends

```
POST /generate
{"prompt": "...", "model": "tiny_model.pt", "temperature": 0.0, "max_new_tokens": 80}
```

this happens, in order:

1. FastAPI validates the JSON against `GenerateRequest`. A missing prompt or an out-of-range number is rejected before any model code runs.
2. The server asks the `ModelManager` for the model. The id is looked up among the checkpoints the manager discovered itself; an unknown id is a 404. The first request for a model reads the checkpoint from disk, rebuilds `TinyLLM` from the saved configuration, loads the weights and moves it to the device. Later requests reuse the cached model.
3. The shared tokenizer is loaded on first use.
4. The server takes the generation lock, so one request uses the device at a time, and calls `generate()`.
5. `generate()` encodes the prompt to token ids with BOS in front. Then it loops: run the model on the most recent `context_length` tokens, take the scores for the last position, rule out tokens that would break UTF-8, choose the next token (the highest score at temperature 0, a random draw otherwise), append it, and stop at EOS or after `max_new_tokens`.
6. The ids are decoded back to text and returned as `{"model": ..., "text": ...}`. The text is the prompt followed by what the model added.

That response is the end of the chain that began with a file in `storage/uploads/`.

### 13.4 What depends on what

A change in one stage makes everything after it stale. The table shows what must be re-run.

| If you change… | Re-run from… | Because |
|---|---|---|
| The uploaded sources | acquisition | New bytes need a new batch, and every later stage is per batch. |
| Cleaning, normalization, filtering or deduplication rules | that stage | The text reaching the dataset changes. |
| The dataset split | dataset building | The tokenizer is trained on the train split only. |
| The tokenizer (vocabulary size, merges) | tokenizer training | Token ids change meaning, so the tokenized dataset and every existing checkpoint no longer match. |
| The model configuration | training, from scratch | Saved weights only fit the architecture they were trained in. |
| Training settings only | training | Resume continues from the latest checkpoint. |
| Nothing but the checkpoint files | nothing; reload the page | The server discovers checkpoints on each listing. |

#### What I should understand before moving on

- The batch id ties together everything from acquisition to deduplication; the document id ties a document from ingestion to its line in the dataset.
- The corpus factory ends at `storage/training/dataset/`. The model side begins there and never reads earlier folders.
- Text exists only up to tokenization. Training, evaluation and the inside of generation work on integers.
- Training and inference run the same forward pass. Training adds a loss, a backward pass and an optimizer step; inference adds a loop that feeds each prediction back in.
- The tokenizer and the checkpoint are a matched pair. A checkpoint is only meaningful with the tokenizer whose ids it was trained on.
- The server holds no model logic of its own: it validates, finds the model, and calls the same `generate()` as the command line.

#### Self-test

1. A batch passes inspection but never appears in `storage/raw/`. Which stage stopped it, and where would you look for the reason?
2. You retrain the tokenizer with a vocabulary of 500, re-tokenize the dataset, and then run `python -m scripts.train` with resume on. What goes wrong, and at which point?
3. Which stages change the content of a document, and which only decide whether it continues?
4. During training the model receives `x` and is compared against `y`. During generation there is no `y`. What takes its place?
5. Two people send `POST /generate` at the same moment. What does the server do, and why?
6. Name the three learned or generated artifacts that must be kept together for a saved model to be usable.

<details><summary>Answers</summary>

1. The provenance gate. Inspection only decides whether the batch is safe to process; ingestion copies only batches with a provenance decision that allows training use. Look under `storage/catalog/provenance/` for a decision for that batch id; if there is none, the batch is waiting for `scripts.provenance_review`.
2. The existing checkpoint was trained with 300 token ids and its embedding and output layers have 300 rows. The model configuration still says 300 as well, but the newly tokenized dataset can now contain ids up to 499, which have no row in the embedding table, so the first forward pass that meets such an id fails. Even without that failure the saved weights would be meaningless, because the same id now stands for different bytes.
3. Cleaning and normalization change text; extraction produces it. Inspection, provenance, filtering and deduplication only decide whether something continues. Acquisition and ingestion copy bytes unchanged.
4. Nothing is compared. The model's own prediction for the last position is turned into a chosen token, and that token is appended to the input for the next pass. The loop replaces the target.
5. Both requests are accepted, but generation runs under a lock, so the second waits until the first has finished. The models share one device, and the generation loop is not written to run two sequences at once.
6. The checkpoint (`artifacts/checkpoints/*.pt`, which carries the weights and the model configuration), the tokenizer (`artifacts/tokenizer/tokenizer.json`), and — to continue training rather than only generate — the optimizer state, which is stored inside the same checkpoint file.

</details>

---

## 14. Numbers from our current JSM MVP

Every number in this chapter was read from the real files on the day this course was written: the checkpoint `artifacts/checkpoints/tiny_model.pt`, the run record under `artifacts/runs/`, the tokenizer file, and the tokenized dataset. They describe one specific trained model and will change the next time you train.

| | |
|---|---|
| **INPUT** | Checkpoint metadata, the run record, the tokenizer file, the tokenized dataset. |
| **PROCESS** | Read each number and work out where it comes from. |
| **OUTPUT** | A sense of scale: how small this model and its data are, and what each number would have to become for a capable model. |
| **WHY IT EXISTS** | You cannot judge an improvement without knowing the baseline it is measured against. |

### 14.1 The model

| Quantity | Value | Where it comes from |
|---|---|---|
| Vocabulary size | 300 | 256 byte values + 3 special tokens + 41 learned merges. |
| Context length | 128 tokens | The most tokens the model can look at in one pass. |
| `d_model` | 128 | The length of the vector that represents each position inside the model. |
| Attention heads | 4 | Each head works on 128 / 4 = 32 numbers per position. |
| Transformer layers | 4 | Four blocks stacked one after another. |
| Dropout | 0.0 | Switched off. |
| Parameters | 884,480 | All trainable. Chapter 7.7 derives this total layer by layer. |

**Vocabulary size (300).** The model's final layer produces 300 scores at every position, one per possible next token. With so few merges, most tokens are still single bytes, so an Arabic word of five letters costs roughly ten tokens. A larger vocabulary would let common words or word pieces become single tokens, so the same 128-token window would cover more text.

**Context length (128).** At roughly two tokens per Arabic letter, 128 tokens is on the order of 60 to 70 Arabic characters, about one short sentence. Anything earlier than that is invisible to the model when it predicts the next token.

**`d_model` (128), heads (4), layers (4).** These three set the model's capacity. Parameter count grows roughly with the square of `d_model` and linearly with the number of layers, which is why widening a model is far more expensive than deepening it.

**Parameters (884,480).** Each parameter is one 32-bit number that training adjusts. For comparison, models that write fluent text have from hundreds of millions to hundreds of billions.

### 14.2 The data

| Quantity | Value |
|---|---|
| Documents in the training split | 1 |
| Documents in validation / test | 0 / 0 |
| Characters in the training text | 297 |
| Bytes in the training text (UTF-8) | 536 |
| Tokens in the tokenized training split | 259 (including BOS and EOS) |

**One document.** The whole training corpus is a single short document. The validation and test splits are empty, because with one document there is nothing to hold back.

**297 characters, 536 bytes, 259 tokens.** Arabic letters take two bytes each in UTF-8, which is why there are almost twice as many bytes as characters. Byte-pair encoding then merged frequent byte pairs, bringing 536 bytes down to 257 tokens; BOS and EOS make 259. The tokenizer therefore compresses this text by about a factor of two relative to raw bytes.

**The ratio that matters.** There are 884,480 parameters and 259 training tokens: more than three thousand parameters for every token of data. A model in that position does not need to learn anything about language; it has more than enough capacity to memorise the one document exactly. This is the single most important fact about the current baseline.

### 14.3 The training run

| Quantity | Value |
|---|---|
| Epochs | 21 |
| Steps per epoch | 3 |
| Global steps | 63 |
| Next-token targets per epoch | 258 |
| `tokens_seen` | 5,418 |
| Learning rate | 0.0003 (constant) |
| Batch size | 1 sequence per step |
| Training time | about 10.5 seconds, on Apple MPS |
| Final training loss (epoch 21 average) | 2.1077 |

**Three steps per epoch.** The 259 tokens are cut into windows of 128 inputs: tokens 0–127 predict tokens 1–128, tokens 128–255 predict 129–256, and the remaining tokens 256–257 predict 257–258. That gives three examples of 128, 128 and 2 targets: 258 predictions in total, which is 259 minus one because the last token has nothing after it to predict.

**63 global steps.** 21 epochs × 3 steps. A step is one forward pass, one backward pass and one optimizer update, so the model's parameters were adjusted 63 times in total.

**`tokens_seen` = 5,418.** 21 epochs × 258 targets. It counts predictions the model was trained on, with repeats. It does not mean 5,418 different tokens: the model saw the same 258 positions 21 times.

**Loss 2.1077.** An untrained model that spreads its guesses evenly over 300 tokens has a loss of ln(300) ≈ 5.70. A freshly initialised model of this size starts close to that. A loss of 2.11 after 21 epochs means the model has learned a good deal about this one document, but has not yet memorised it; a loss near 0 would mean it predicts every next token with near certainty.

### 14.4 Loss and perplexity

| Split | Loss | Perplexity | Examples |
|---|---|---|---|
| Train | 2.0433 | 7.72 | 3 |
| Validation | not available | not available | 0 |
| Test | not available | not available | 0 |

These come from `python -m scripts.evaluate` on the final checkpoint.

**Perplexity 7.72** is `exp(2.0433)`. It reads as: on average the model is as uncertain as if it were choosing evenly among about eight tokens at each position, down from 300 for an untrained model.

**Why evaluation shows 2.0433 when training reported 2.1077.** They measure different things. The training figure is the average over epoch 21 while the weights were still being updated after each step. The evaluation figure is measured afterwards, with the final weights, over the same three examples. The final weights are slightly better than the weights the epoch started with.

**What these numbers cannot tell you.** Both are measured on text the model was trained on. They show how well it has absorbed that document and say nothing about text it has never seen. Until the validation split has documents in it, there is no measurement of generalisation at all.

### 14.5 Sizes on disk

| File | Size |
|---|---|
| Model weights alone (884,480 × 4 bytes) | 3.54 MB |
| `artifacts/checkpoints/tiny_model.pt` | 10.68 MB |
| 21 per-epoch history checkpoints | 224 MB in total |
| `artifacts/tokenizer/tokenizer.json` | 1,734 bytes |

**Why the checkpoint is three times the size of the weights.** A checkpoint holds the optimizer state as well as the weights. AdamW keeps two extra numbers for every parameter (a running average of its gradient and of its squared gradient), so the file holds roughly three numbers per parameter: 3 × 3.54 MB ≈ 10.6 MB. The optimizer state is only needed to continue training. A file for generating text only could be a third of the size.

**The history files.** The 21 numbered checkpoints on disk were written by the run above, before the trainer kept only the newest few. The API leaves them out of its model list by default, and nothing in the pipeline reads them. The current trainer would prune them the next time it saves.

**The tokenizer file is tiny** because byte-level BPE only needs to store the list of merges. The 256 byte tokens are implied.

#### What I should understand before moving on

- The model has 884,480 parameters and was trained on 259 tokens: it can memorise its data many times over.
- `tokens_seen` counts training predictions with repetition; it is 21 passes over the same 258 positions.
- A loss of ln(vocabulary size) is the starting point of an untrained model; perplexity is `exp(loss)` and reads as "choosing among this many tokens".
- All current loss figures are on training data. There is no validation or test measurement yet.
- A checkpoint is about three times the size of the weights because it carries AdamW's state.
- The vocabulary of 300 and the context of 128 tokens mean the model sees about one short Arabic sentence at a time.

#### Self-test

1. Why does one epoch contain 258 training targets when the tokenized document has 259 tokens?
2. If you trained for 42 epochs instead of 21 on the same data, what would `global_step` and `tokens_seen` be?
3. The training loss was 2.1077 and the evaluation loss on the same data was 2.0433. Give the reason they differ.
4. An untrained model with a vocabulary of 1,000 tokens would start at roughly what loss, and what perplexity?
5. Why can no conclusion about the model's ability to write new text be drawn from a perplexity of 7.72?
6. Roughly how large would a checkpoint be for a model with 10 million parameters, saved the same way?

<details><summary>Answers</summary>

1. Each target is "the token that comes next". The last token has no successor, so 259 tokens give 258 input/target pairs.
2. `global_step` = 42 × 3 = 126. `tokens_seen` = 42 × 258 = 10,836.
3. The training figure averages the loss over the three steps of epoch 21, and the weights were updated after each of those steps, so the earlier steps were scored with slightly worse weights. Evaluation scores all three examples with the final weights.
4. Loss ≈ ln(1000) ≈ 6.91. Perplexity ≈ 1,000: it is choosing evenly among all tokens.
5. It was measured on the same single document the model was trained on. It shows how well that document has been absorbed, which a model with thousands of parameters per token can do by memorising. Only loss on held-out text says anything about new text, and the validation and test splits are empty.
6. Weights: 10,000,000 × 4 bytes = 40 MB. With AdamW's two extra values per parameter, about 120 MB.

</details>

---

## 15. The full system map

The whole system on one page. Read it top to bottom; each arrow means "the output of the line above is the input of the line below". The right-hand column gives the command, the place the result is stored, and the chapter.

```
Uploaded source            you place files in             storage/uploads/                          (ch. 13)
      │
      ▼
Acquisition                scripts.acquisition      →     storage/incoming/batches/<batch>/         (4.1)
      │                    copy, hash, manifest
      ▼
Inspection                 scripts.inspection       →     storage/catalog/inspections/              (4.2)
      │                    limits, types, structure        storage/quarantine/  (rejected)
      ▼
Provenance                 scripts.provenance       →     storage/catalog/provenance/               (4.3)
      │                    scripts.provenance_review       may this be used for training?
      ▼
Ingestion                  scripts.ingestion        →     storage/raw/<batch>/                      (4.4)
      │                    trusted copy, document ids
      ▼
Extraction                 scripts.extraction       →     storage/extracted/<batch>/                (4.5)
      │                    file → plain text
      ▼
Cleaning                   scripts.cleaning         →     storage/processed/cleaned/                (4.6.1)
      ▼
Normalization              scripts.normalization    →     storage/processed/normalized/             (4.6.2)
      ▼
Filtering                  scripts.filtering        →     storage/processed/filtered/               (4.6.3)
      ▼
Deduplication              scripts.deduplication    →     storage/processed/deduplicated/           (4.6.4)
      │
      ▼
Dataset Building           scripts.dataset_building →     storage/training/dataset/*.jsonl          (5)
      │                    one JSON line per document, train / validation / test
      ▼
Tokenizer Training         scripts.tokenizer_training →   artifacts/tokenizer/tokenizer.json        (6)
      │                    byte-level BPE merges
      ▼
Tokenized Dataset          scripts.tokenize_dataset →     storage/training/tokenized/*.jsonl        (5, 6)
      │                    text → token ids, with BOS and EOS
      ▼
┌──────────────────────────  scripts.train  ──────────────────────────┐
│ Embeddings               token ids + positions → vectors [B, T, C]  │                             (7.3)
│      ▼                                                              │
│ Transformer              4 blocks: attention + feed-forward         │                             (7.4, 7.5)
│      ▼                                                              │
│ Logits                   one score per vocabulary token [B, T, V]   │                             (7.6)
│      ▼                                                              │
│ Loss                     cross-entropy against the true next tokens │                             (8)
│      ▼                                                              │
│ Backpropagation          loss.backward(): a gradient per parameter  │                             (8)
│      ▼                                                              │
│ Optimizer                AdamW: optimizer.step() updates parameters │                             (8)
│      │   └────────── repeat for every example, every epoch ────────┘│
└──────┼──────────────────────────────────────────────────────────────┘
       ▼
Checkpoint                 saved during training    →     artifacts/checkpoints/*.pt                (8)
      │                    weights, optimizer, config, counters      artifacts/runs/<run>/run.json
      ▼
Evaluation                 scripts.evaluate               loss and perplexity per split             (9)
      │
      ▼
Inference                  scripts.inference              prompt → ids → loop → ids → text          (10)
      │                    same generate() the server calls
      ▼
Serving API                scripts.serve                  GET /health, GET /models, POST /generate  (11)
      │                    ModelManager finds, loads and caches the model
      ▼
Live model response        {"model": "...", "text": "..."}
```

Three things to notice in the map:

- **Two kinds of storage.** `storage/` holds data on its way to becoming a dataset. `artifacts/` holds what was learned from that data: the tokenizer, the checkpoints, the run records.
- **Two things are learned.** The tokenizer is learned first, from text. The model is learned second, from token ids produced by that tokenizer. Everything else in the chain is ordinary deterministic code.
- **The same forward pass appears twice.** The boxed section is the model running during training. Evaluation and inference run exactly the same embeddings → transformer → logits path; they differ only in what they do with the logits.

---

## Appendix A. The test suite

The project has one test file, `tests/test_inspection.py` (402 lines, 38 tests). It tests the inspection stage of chapter 4.2 and nothing else.

**What a unit test is.** A unit test is a small function that calls one piece of your code with an input you control and then states what the result must be. The statement is called an **assertion**. If the result is what the assertion says, the test passes silently; if not, the test fails and reports the two values. A test never asks you to look at output and judge it: the judgement is written in the test.

Tests are worth having for two reasons. They pin down behaviour: "a file whose content does not match its recorded hash is quarantined" stops being an intention and becomes something a machine checks. And they protect it: when you change `checks.py` next month, running the tests tells you within a second whether one of 38 stated behaviours changed.

A good unit test builds its own input. These tests never touch `storage/`. Each one creates a throw-away folder, writes a tiny fake batch into it, runs the real inspection code on it, and lets the folder be deleted afterwards.

**The framework.** The file uses `unittest`, which is part of Python's standard library. Nothing has to be installed. The rules of `unittest` used here:

- A test class inherits from `unittest.TestCase`.
- Every method whose name starts with `test` is one test.
- A method named `setUp` runs before each test, so every test starts from the same fresh state.
- Assertions are methods such as `self.assertEqual(a, b)` and `self.assertTrue(x)`.

**How it is run.** From the project directory:

```
.venv/bin/python -m unittest discover -s tests -p test_inspection.py -v
```

`-m unittest` runs the standard test runner; `discover -s tests` tells it to look in the `tests` folder; `-p test_inspection.py` is the file-name pattern to load; `-v` prints one line per test. This is the command given in `src/corpus_factory/inspection/README.md`. The shorter `.venv/bin/python -m unittest tests.test_inspection` also works.

What was verified for this appendix:

- `pytest`, the other common Python test runner, is not installed in `.venv` (`import pytest` fails with `ModuleNotFoundError`) and is not in `requirements.txt`. The file does not need it.
- Both commands above were run from the project directory and both found and ran 38 tests.
- Running the file directly, `.venv/bin/python tests/test_inspection.py`, does not work, although the file ends with `unittest.main()`. It stops at the first project import with `ModuleNotFoundError: No module named 'src'`, because Python then puts `tests/` and not the project directory on its import path.
- There is no `tests/__init__.py`, no `conftest.py` and no test configuration file.

**Where the tests write.** Only into the operating system's temporary directory. `setUp` creates a `tempfile.TemporaryDirectory()` and every fake batch, catalog and quarantine folder is placed inside it. The inspection code under test also creates its own temporary files there (a private snapshot of each artifact, and a folder of snapshots for the malware scanner). Nothing is written under `storage/` or `artifacts/`. The tests do **read** one repository file: `configs/inspection.json`, through `load_inspection_config()` in `setUp`. For this appendix the tests were run with Python's `-B` option so that not even compiled `.pyc` files were written into the repository; `git status` was identical before and after.

**Result of the run.** 37 tests pass and 1 fails:

```
Ran 38 tests in 0.238s

FAILED (failures=1)
```

The failing test is `test_pdf_active_names_and_missing_validator`, at line 304:

```
AssertionError: <InspectionDecision.ACCEPTED: 'accepted_for_ingestion'> != <InspectionDecision.QUARANTINED: 'quarantined'>
```

The cause is a disagreement between the test and the project's current policy file, not random behaviour. The test assumes the policy value `require_deep_container_inspection` is `true` when it starts. `setUp` loads the real `configs/inspection.json`, in which that value is currently `false`. The explanation is given with the test itself below, where it was also reproduced with both values. The Git history shows the value was `true` in an earlier commit and was changed to `false` in commit `472447f`.

The inspection stage has seven code modules (plus an `__init__.py` that holds only a docstring). The test file imports from six of them — `checks`, `config`, `inspector`, `quarantine`, `report`, `result` — and exercises the seventh, `deep_inspection`, through `inspect_artifact`.

### `tests/test_inspection.py`

**Why this file exists** — To state, as executable checks, what the inspection stage must decide for each kind of good, damaged, disguised or hostile input.

**What enters / what leaves** — Nothing is passed in. Each test builds its input inside a temporary directory. The only output is the pass/fail report of the test runner. Read: `configs/inspection.json`. Written: temporary files only.

**How it connects** — It calls the functions of `src/corpus_factory/inspection/` directly. No script and no pipeline stage calls it; you run it by hand.

**The code, section by section**

```python
"""Inspection contract tests; fixtures never enter the live incoming catalog."""
import codecs
import hashlib
import io
import json
import os
import stat
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
```

The first line is the module's docstring. A **fixture** is the prepared input of a test; the sentence promises that fixtures are never placed in the real `storage/incoming`.

| Import | Used for |
|---|---|
| `codecs` | Not used anywhere in the file. |
| `hashlib` | SHA-256 of fixture bytes, so the fake manifest carries correct hashes. |
| `io` | `io.BytesIO`, a file-like object that lives in memory; used to build ZIP archives without touching disk. |
| `json` | Writing the fake `source.json`, reading reports back. |
| `os` | `os.mkfifo` for the named-pipe test. |
| `stat` | The constant `stat.S_IFLNK` ("this is a symbolic link") for the archive-symlink test. |
| `subprocess` | Building fake results of an external command (`CompletedProcess`, `TimeoutExpired`). |
| `tempfile` | The temporary directory each test works in. |
| `unittest` | The test framework. |
| `zipfile` | Building small ZIP archives; `.docx`, `.xlsx`, `.epub` and similar files are ZIP archives. |
| `Path` | Paths. |
| `patch` | Temporarily replacing a function with a fake one. Explained at `setUp`. |

```python
from src.corpus_factory.inspection.checks import (
    _scan_snapshots, apply_malware_result, inspect_artifact, scan_malware_batch,
)
from src.corpus_factory.inspection.config import load_inspection_config, validate_inspection_config
from src.corpus_factory.inspection.inspector import inspect_batch
from src.corpus_factory.inspection.quarantine import quarantine_batch
from src.corpus_factory.inspection.report import completed_batches, publish_record, write_inspection_report
from src.corpus_factory.inspection.result import InspectionDecision as D, MalwareScanResult, MalwareScanStatus as M, more_restrictive_decision
```

The code under test. Two names are shortened with `as`: `D` is `InspectionDecision`, whose three values are `D.ACCEPTED`, `D.QUARANTINED` and `D.REJECTED`; `M` is `MalwareScanStatus` (`M.CLEAN`, `M.INFECTED`, `M.UNAVAILABLE`, `M.ERROR`, `M.NOT_RUN`). Almost every assertion in the file compares a decision with one of the three `D` values.

`_scan_snapshots` starts with an underscore, the convention for an internal helper. The tests import it anyway so they can test the scanner-calling logic on its own.

```python
def zip_bytes(members):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in members:
            archive.writestr(name, data)
    return output.getvalue()
```

A helper that builds a ZIP archive in memory and returns its bytes. `members` is a list of `(name, data)` pairs; `archive.writestr(name, data)` adds one file to the archive. `ZIP_DEFLATED` selects ordinary ZIP compression. `output.getvalue()` returns everything written to the in-memory file. The tests use this to manufacture a "Word document" of a few hundred bytes.

```python
def office_members(extra=()):
    return [('[Content_Types].xml', '<Types/>'), ('_rels/.rels', '<Relationships/>'),
            ('word/document.xml', '<document><body>hello</body></document>'), *extra]
```

Returns the smallest set of members that the inspection code accepts as a `.docx`: the two package metadata files every Office document has, and `word/document.xml` whose root element is `document`. `*extra` unpacks any additional members a test wants to add, so a test can take a valid document and add exactly one bad thing to it.

```python
class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.batch = self.root / 'batch-test'
        (self.batch / 'objects').mkdir(parents=True)
```

The one test class. `setUp` runs before every test method.

- `tempfile.TemporaryDirectory()` creates a new, empty, uniquely named folder in the system's temporary area.
- `self.addCleanup(self.temporary.cleanup)` registers a function to be called after the test, whether it passed or failed. Here it deletes the folder and everything in it.
- `self.root` is that folder as a `Path`. `.resolve()` replaces any symbolic links in the path with the real location. This matters: the inspection code rejects an artifact if any folder on the way to it is a symbolic link, and on macOS the temporary area is reached through one. Without `.resolve()` every artifact would be rejected for that reason.
- `self.batch` is a fake batch folder named `batch-test`, with the `objects` sub-folder acquisition would create.

```python
        self.policy = load_inspection_config()
        self.policy['require_malware_scan'] = False
        self.items = []
        self.scanners = patch('src.corpus_factory.inspection.checks.shutil.which', return_value=None)
        self.scanners.start()
        self.addCleanup(self.scanners.stop)
```

- `self.policy` is the real inspection policy, read from `configs/inspection.json` and validated. Each test gets its own copy, so a test may change a limit without affecting the others. `require_malware_scan` is forced to `False` so that the missing scanner (next lines) does not quarantine everything. No other policy value is forced, which means the tests depend on what the configuration file currently contains.
- `self.items` will collect the manifest entries of the files a test adds.
- **`patch`** replaces an object with a stand-in for a limited time. `shutil.which(name)` normally searches the computer for a program and returns its path. The patch makes it return `None` — "no such program" — for every name. `.start()` activates the replacement and the cleanup undoes it after the test.

The purpose is to make the tests independent of the machine. Inspection looks for the virus scanners `clamdscan`/`clamscan` and for the PDF tool `pdfinfo` with `shutil.which`. On the machine used for this appendix all three are installed; with the patch, every test behaves as if none were. The patch string names `checks.shutil.which`, but `shutil` is one shared module object, so the replacement also applies to the `shutil.which('pdfinfo')` call in `deep_inspection.py` (verified: both modules refer to the same `shutil`).

```python
    def add(self, name, data):
        path = self.batch / 'objects' / f'{len(self.items):03d}-{name}'
        path.write_bytes(data)
        item = dict(artifact_id=f'a{len(self.items)}', original_filename=name,
                    stored_relative_path=path.relative_to(self.batch).as_posix(),
                    size_bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        self.items.append(item)
        return item, path
```

The fixture builder used by nearly every test. `add('good.txt', b'hello\n')` does what acquisition would do for one file:

1. Writes the bytes to `objects/000-good.txt`. `{len(self.items):03d}` is the count of files so far, padded to three digits, so the second file is `001-…`.
2. Builds the manifest entry: an artifact id (`a0`, `a1`, …), the original file name, the path relative to the batch, the size, and the SHA-256 of the bytes. These are the fields `read_manifest` requires.
3. Remembers the entry in `self.items` and returns both the entry and the path.

Returning the path lets a test damage the file after its hash was recorded.

```python
    def manifest(self, **updates):
        record = dict(schema_version='1.0.0', record_type='incoming_source_batch',
                      batch_id=self.batch.name, source={}, license={}, artifacts=self.items)
        record.update(updates)
        data = json.dumps(record).encode()
        (self.batch / 'source.json').write_bytes(data)
        (self.batch / 'source.json.sha256').write_text(hashlib.sha256(data).hexdigest())
```

Writes the fake `source.json` and its checksum file, listing every file added so far. `**updates` collects any keyword arguments into a dictionary; `record.update(updates)` overwrites fields with them. So `self.manifest(batch_id='other')` writes a manifest that is valid except for one deliberately wrong field — and still has a correct checksum, so the test reaches the check it is aiming at.

```python
    def inspect(self, item):
        return inspect_artifact(self.batch, item, self.policy, self.policy['max_batch_size_bytes'])

    def run_batch(self):
        self.manifest()
        return inspect_batch(self.batch, self.policy)
```

Two shortcuts for the two levels the tests work at.

- `inspect(item)` calls `inspect_artifact` for one file, with the whole batch byte budget available. No manifest is read and no malware scan is run. Most tests use this.
- `run_batch()` writes the manifest and calls `inspect_batch`, the full path: manifest validation, every artifact, malware scan, combined result.

```python
    def test_decision_never_downgrades(self):
        for candidate in D:
            self.assertEqual(more_restrictive_decision(D.REJECTED, candidate), D.REJECTED)
        self.assertEqual(more_restrictive_decision(D.ACCEPTED, D.QUARANTINED), D.QUARANTINED)
```

**Pins down:** decisions only ever get stricter. Combining `REJECTED` with any decision stays `REJECTED`; combining `ACCEPTED` with `QUARANTINED` gives `QUARANTINED`. **Input:** none; `for candidate in D` loops over the three enum values. This is the rule that lets inspection run many checks on one file and keep the worst verdict.

```python
    def test_mixed_batch_and_actual_duplicate_hashes(self):
        self.add('good.txt', b'hello\n')
        self.add('copy.txt', b'hello\n')
        self.add('fake.pdf', b'hello\n')
        self.add('program.exe', b'MZprogram')
        result = self.run_batch()
        self.assertTrue(result.batch_valid)
        self.assertEqual([a.decision for a in result.artifacts], [D.ACCEPTED, D.ACCEPTED, D.QUARANTINED, D.REJECTED])
        self.assertEqual(result.summary['accepted'], 2)
        self.assertEqual(result.duplicate_groups[0]['count'], 3)
```

**Pins down:** one batch can hold accepted, quarantined and rejected files at once, and each file gets its own verdict. **Input:** four files. Two identical text files are accepted. `fake.pdf` contains plain text, so its content does not match its extension: quarantined. `program.exe` has a blocked extension: rejected. The batch itself stays valid because its manifest is fine.

The last assertion checks duplicate reporting: three files have the same bytes (`good.txt`, `copy.txt`, `fake.pdf`), so there is one duplicate group of size 3. Inspection reports duplicates; it does not remove them, which is why both copies are accepted. The `.exe` is not in a group: it was rejected before it was hashed.

```python
    def test_artifact_corruption_does_not_block_sibling(self):
        item, path = self.add('changed.txt', b'hello')
        path.write_bytes(b'world')
        self.add('good.txt', b'fine')
        result = self.run_batch()
        self.assertTrue(result.batch_valid)
        self.assertEqual(result.artifacts[0].decision, D.QUARANTINED)
        self.assertEqual(result.artifacts[1].decision, D.ACCEPTED)
        self.assertEqual(result.artifacts[0].sha256, hashlib.sha256(b'world').hexdigest())
```

**Pins down:** a file whose bytes no longer match the hash in the manifest is quarantined, and that does not affect the other files of the batch. **Input:** `add` records the hash of `hello`; the test then overwrites the file with `world` (same length, different content). The last line checks that the result records the hash of what is actually on disk, not the hash the manifest claimed.

```python
    def test_invalid_manifest_gates_all_content(self):
        self.add('good.txt', b'hello')
        for changes in ({'batch_id': 'other'}, {'artifacts': [None]}, {'artifacts': []},
                        {'source': []}, {'schema_version': 'unknown'}):
            with self.subTest(changes=changes):
                self.manifest(**changes)
                with patch('src.corpus_factory.inspection.inspector.inspect_artifact') as inspect:
                    result = inspect_batch(self.batch, self.policy)
                self.assertFalse(result.batch_valid)
                self.assertEqual(result.artifacts, ())
                inspect.assert_not_called()
```

**Pins down:** if `source.json` is not trustworthy, no file of the batch is even looked at. **Input:** one good file, and five manifests, each wrong in one way: a batch id that does not match the folder name, an artifact entry that is not an object, an empty artifact list, a `source` that is a list where an object is required, an unknown schema version.

Two new tools appear:

- `with self.subTest(changes=changes):` runs the indented block as a separately reported sub-case. If the third manifest fails, the report says which `changes` value it was, and the remaining ones still run.
- `with patch(...) as inspect:` replaces `inspect_artifact` — as seen from `inspector.py` — with a recording stand-in. `inspect.assert_not_called()` then proves that `inspect_batch` returned without calling it. Checking `result.artifacts == ()` alone would not prove that no file was opened.

```python
    def test_checksum_mismatch(self):
        self.add('good.txt', b'hello')
        self.manifest()
        with (self.batch / 'source.json').open('ab') as stream:
            stream.write(b' ')
        self.assertFalse(inspect_batch(self.batch, self.policy).batch_valid)
```

**Pins down:** a `source.json` that was changed after its checksum was written invalidates the batch. **Input:** a correct manifest, then one space appended to it (`'ab'` opens a file for appending bytes). The JSON is still valid; only the checksum no longer matches.

```python
    def test_duplicate_manifest_ids(self):
        item, _ = self.add('good.txt', b'hello')
        self.items.append(item.copy())
        self.assertFalse(self.run_batch().batch_valid)
```

**Pins down:** a manifest that lists the same artifact id (and the same stored path) twice is invalid. **Input:** one file whose manifest entry is appended a second time. The `_` on the first line is the usual name for "a value I do not need" — here the path.

```python
    def test_traversal_is_artifact_rejection(self):
        item, _ = self.add('bad.txt', b'hello')
        for path in ('../outside.txt', '/etc/passwd', 'objects/../source.json', 'objects\\x.txt', 'objects/C:x.txt'):
            with self.subTest(path=path):
                item['stored_relative_path'] = path
                self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** a manifest cannot point inspection at a file outside the batch's `objects` folder. **Input:** one real file whose manifest entry is rewritten with five hostile paths: up and out of the batch (`..`), an absolute system path, a path that climbs back to `source.json`, a Windows backslash, a Windows drive letter. Each must be `REJECTED`. This kind of attack is called **path traversal**. The only accepted form is exactly `objects/<filename>`.

```python
    def test_links_and_nonregular_files(self):
        item, path = self.add('link.txt', b'hello')
        path.unlink()
        path.symlink_to(self.root / 'nonexistent')
        result = self.inspect(item)
        self.assertEqual(result.decision, D.REJECTED)
        self.assertTrue(result.is_symlink)
        path.unlink()
        path.mkdir()
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** only ordinary files are inspected. **Input:** the file is deleted (`unlink`) and replaced first by a symbolic link — a pointer to another path, here one that does not exist — and then by a directory with the same name. Both are rejected, and for the link the result records `is_symlink=True`. A symbolic link is dangerous because reading "the file" would read whatever it points to, possibly outside the batch.

```python
    def test_symlink_parent(self):
        item, path = self.add('good.txt', b'hello')
        objects = self.batch / 'objects'
        objects.rename(self.root / 'outside')
        objects.symlink_to(self.root / 'outside', target_is_directory=True)
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** a link anywhere on the path counts, not only at the file itself. **Input:** the real `objects` folder is moved out of the batch and a symbolic link named `objects` is put in its place. The file can still be reached through the link and its content is fine, but it is rejected.

```python
    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO')
    def test_fifo_not_opened(self):
        item, path = self.add('fifo.txt', b'hello')
        path.unlink()
        os.mkfifo(path)
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** a named pipe is rejected without being opened. **Input:** the file is replaced by a FIFO (`os.mkfifo`), a special file that connects two programs. Opening a FIFO for reading normally waits until some other program writes to it; an inspector that opened it could hang forever. The name of the test states the point: the test finishing at all shows the pipe was not read.

The line starting with `@` is a **decorator**: it modifies the method below it. `skipUnless(condition, reason)` runs the test only when the condition is true. `hasattr(os, 'mkfifo')` is true on macOS and Linux and false on Windows, where the test would be reported as skipped.

```python
    def test_missing_and_empty(self):
        item, path = self.add('missing.txt', b'hello')
        path.unlink()
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
        item, _ = self.add('empty.pdf', b'')
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
```

**Pins down:** a file that the manifest lists but that is not there, and a file of zero bytes, are both quarantined. **Input:** one deleted file; one empty file. Note the difference from the previous tests: these are `QUARANTINED` (something is wrong or uncertain, a person should look) and not `REJECTED` (a definite policy violation).

```python
    def test_oversized_file_not_hashed(self):
        item, _ = self.add('huge.txt', b'hello')
        self.policy['max_file_size_bytes'] = 4
        with patch('src.corpus_factory.inspection.checks.stream_hash') as hash_file:
            self.assertEqual(self.inspect(item).decision, D.REJECTED)
        hash_file.assert_not_called()
```

**Pins down:** a file over the size limit is rejected before any of its content is read. **Input:** a 5-byte file and a limit lowered to 4 bytes — the test makes the file "too big" by shrinking the limit. `stream_hash`, the function that reads and hashes a file, is replaced by a recording stand-in, and `assert_not_called()` proves it was never used. The point is cost: a hostile 500 GB upload must not make inspection read 500 GB.

```python
    def test_budget_only_rejects_overflow(self):
        self.add('a.txt', b'1234')
        self.add('b.txt', b'1234')
        self.add('c.txt', b'1')
        self.policy['max_batch_size_bytes'] = 5
        self.assertEqual([a.decision for a in self.run_batch().artifacts], [D.ACCEPTED, D.REJECTED, D.ACCEPTED])
        self.policy['max_batch_size_bytes'] = 100
        self.policy['max_files_per_batch'] = 1
        self.assertEqual([a.decision for a in self.run_batch().artifacts], [D.ACCEPTED, D.REJECTED, D.REJECTED])
```

**Pins down:** how the two batch-wide limits are applied. **Input:** files of 4, 4 and 1 bytes.

With a byte budget of 5: the first file uses 4, leaving 1. The second (4 bytes) does not fit and is rejected. The third (1 byte) fits in the remaining 1 and is accepted. So a rejected file does not use up budget, and files after it still get their chance — the "only rejects overflow" of the name.

With a file-count limit of 1: only the first file is within the count; the others are rejected regardless of size.

```python
    def test_text_encodings_statistics(self):
        for encoding in ('utf-8', 'utf-8-sig', 'utf-16'):
            with self.subTest(encoding=encoding):
                item, _ = self.add('arabic.txt', 'مرحبا\r\nworld\nend'.encode(encoding))
                result = self.inspect(item)
                self.assertEqual(result.decision, D.ACCEPTED, result.errors)
                self.assertEqual(result.encoding, encoding)
                self.assertEqual((result.character_count, result.line_count, result.max_line_characters), (16, 3, 5))
```

**Pins down:** text is accepted in three encodings, the encoding is detected correctly, and the statistics are counted in characters, not bytes. **Input:** the same mixed Arabic/English text encoded three ways. `utf-8-sig` is UTF-8 with a byte-order mark at the front; Python's `utf-16` encoder also writes one.

The expected numbers: 16 characters (5 + `\r\n` + 5 + `\n` + 3), 3 lines, longest line 5 characters. They are the same for all three encodings although the files have different byte lengths, the byte-order mark is not counted, and `\r\n` ends one line, not two.

The third argument of `assertEqual`, `result.errors`, is a message shown only if the assertion fails — here, the reasons inspection gave.

```python
    def test_late_invalid_utf8_and_controls(self):
        for data in (b'a' * 70000 + b'\xff', b'a' * 70000 + b'\x00'):
            item, _ = self.add('bad.txt', data)
            self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
```

**Pins down:** the whole file is validated, not just its beginning. **Input:** 70,000 letters `a` followed by one bad byte: `\xff`, which can never occur in UTF-8, or `\x00`, a control character that does not belong in text. `b'a' * 70000` repeats the byte 70,000 times. The number is chosen to be larger than the 65,536-byte chunk inspection reads at a time, so the bad byte sits in the second chunk. A check that sampled only the start of the file would accept it.

```python
    def test_line_limit_and_chunk_boundary(self):
        item, _ = self.add('lines.txt', b'a' * 65535 + b'\r\nlast')
        self.policy['max_line_characters'] = 65534
        result = self.inspect(item)
        self.assertEqual(result.decision, D.QUARANTINED)
        self.assertEqual(result.line_count, 2)
        self.assertEqual(result.max_line_characters, 65535)
```

**Pins down:** line counting is correct even when a line ending is split between two reads, and an over-long line quarantines the file. **Input:** 65,535 letters, then `\r\n`, then `last`. The first chunk of 65,536 bytes ends exactly after the `\r`; the `\n` is the first byte of the next chunk. A careless counter would see `\r` and `\n` as two line endings and report 3 lines. The test requires 2, and a longest line of 65,535 — one more than the lowered limit, hence `QUARANTINED`.

```python
    def test_structured_json(self):
        for suffix, data, expected in (('.json', b'{"a":1}', D.ACCEPTED), ('.json', b'{bad}', D.QUARANTINED),
                                      ('.jsonl', b'{"a":1}\n{bad}', D.QUARANTINED), ('.json', b'NaN', D.QUARANTINED)):
            item, _ = self.add('data' + suffix, data)
            self.assertEqual(self.inspect(item).decision, expected)
```

**Pins down:** files that claim to be JSON must parse as JSON. **Input:** four cases written as `(extension, content, expected decision)` tuples, which the `for` line unpacks into three variables. Valid JSON is accepted. Broken JSON is quarantined. A `.jsonl` file (one JSON value per line) is quarantined when any line is broken. `NaN` is quarantined: Python's parser would accept it, but it is not part of the JSON standard, and inspection refuses it.

```python
    def test_content_disguised_executable(self):
        item, _ = self.add('program.pdf', b'MZpayload')
        self.assertEqual(self.inspect(item).decision, D.REJECTED)

    def test_binary_garbage(self):
        item, _ = self.add('bad.txt', bytes(range(256)))
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
```

**First test pins down:** content is judged by its bytes, not its name. **Input:** a file named `.pdf` that starts with `MZ`, the two bytes every Windows program begins with. Rejected.

**Second test pins down:** a `.txt` file that is not text is quarantined. **Input:** `bytes(range(256))` — every possible byte value from 0 to 255 once.

Compare the two outcomes: a recognised executable is a definite violation (`REJECTED`); unidentifiable bytes are merely suspicious (`QUARANTINED`).

```python
    def test_safe_docx(self):
        item, _ = self.add('safe.docx', zip_bytes(office_members()))
        self.assertEqual(self.inspect(item).decision, D.ACCEPTED)
```

**Pins down:** the baseline for all archive tests — a minimal, harmless `.docx` is accepted. **Input:** the three standard members from `office_members()`, zipped. Without this test, the "bad archive is rejected" tests below would prove little, because rejecting every archive would pass them too.

```python
    def test_archive_attacks(self):
        for name in ('../escape', '/absolute', 'C:/windows', 'a\\b', 'word/vbaProject.bin',
                     'word/embeddings/data.bin', 'word/payload.exe', 'word/payload.dll'):
            with self.subTest(name=name):
                item, _ = self.add('bad.docx', zip_bytes(office_members([(name, 'payload')])))
                self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** a document archive with one dangerous member is rejected as a whole. **Input:** eight archives, each the safe document plus one extra member. The first four have member names that would write outside the target folder if the archive were ever unpacked (path traversal again, inside the ZIP). `vbaProject.bin` is where Office stores macros. `embeddings/` holds embedded objects. `.exe` and `.dll` are executables.

```python
    def test_archive_symlink(self):
        link = zipfile.ZipInfo('word/link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        item, _ = self.add('link.docx', zip_bytes(office_members([(link, '../outside')])))
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** a symbolic link stored inside an archive is rejected. **Input:** built by hand, because `writestr` with a plain name always makes an ordinary file. A `ZipInfo` object describes one member. `create_system = 3` marks it as created on Unix. `external_attr` holds the Unix file mode in its upper 16 bits: `stat.S_IFLNK` is the "symbolic link" type, `0o777` (an octal number) the permissions, `|` combines them, and `<< 16` shifts them into the upper half. The member's data, `../outside`, is the link's target.

```python
    def test_archive_limits(self):
        for key in ('max_archive_files', 'max_archive_member_bytes', 'max_uncompressed_bytes', 'max_compression_ratio'):
            with self.subTest(key=key):
                policy = self.policy.copy()
                self.policy[key] = 1
                item, _ = self.add('large.docx', zip_bytes(office_members([('large.txt', 'a' * 10000)])))
                self.assertEqual(self.inspect(item).decision, D.REJECTED)
                self.policy = policy
```

**Pins down:** each of the four archive resource limits is enforced on its own. **Input:** a document with an extra member of 10,000 identical letters, which compresses to almost nothing. For each limit in turn, the test saves a copy of the policy, sets that one limit to `1`, expects `REJECTED`, and restores the policy. The limits are: number of members, size of one member, total unpacked size, and ratio of unpacked to packed size. Together they defend against a **zip bomb** — a small archive that expands to an enormous size.

```python
    def test_archive_missing_member_and_corruption(self):
        for data in (zip_bytes([('other.xml', '<root/>')]), b'PKgarbage'):
            item, _ = self.add('bad.docx', data)
            self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
```

**Pins down:** an archive that is not a proper document is quarantined, not rejected. **Input:** a valid ZIP that lacks `word/document.xml`, and nine bytes that start like a ZIP (`PK`) and are not one. Neither is hostile in a provable way; both are unusable.

```python
    def test_other_supported_document_containers(self):
        fixtures = {
            'xlsx': [('[Content_Types].xml', '<Types/>'), ('_rels/.rels', '<Relationships/>'), ('xl/workbook.xml', '<workbook/>')],
            'pptx': [('[Content_Types].xml', '<Types/>'), ('_rels/.rels', '<Relationships/>'), ('ppt/presentation.xml', '<presentation/>')],
            'odt': [('mimetype', 'application/vnd.oasis.opendocument.text'), ('content.xml', '<document-content/>')],
            'ods': [('mimetype', 'application/vnd.oasis.opendocument.spreadsheet'), ('content.xml', '<document-content/>')],
            'epub': [('mimetype', 'application/epub+zip'), ('META-INF/container.xml', '<container/>')],
        }
        for suffix, members in fixtures.items():
            with self.subTest(suffix=suffix):
                item, _ = self.add('safe.' + suffix, zip_bytes(members))
                result = self.inspect(item)
                self.assertEqual(result.decision, D.ACCEPTED, result.errors)
```

**Pins down:** the other five ZIP-based formats are recognised and accepted in their minimal form. **Input:** a dictionary from extension to the smallest member list inspection accepts for it: Excel and PowerPoint (same package files as Word, a different main part), OpenDocument text and spreadsheet (a `mimetype` member naming the format, plus `content.xml`), and EPUB.

```python
    def test_encrypted_archive_and_crc_failure(self):
        data = bytearray(zip_bytes(office_members()))
        for signature, flag_offset in ((b'PK\x03\x04', 6), (b'PK\x01\x02', 8)):
            offset = 0
            while (offset := data.find(signature, offset)) >= 0:
                data[offset + flag_offset] |= 1
                offset += 4
        item, _ = self.add('encrypted.docx', data)
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down (first half):** an archive whose members are marked as encrypted is rejected — inspection cannot see inside it. **Input:** a safe document, edited byte by byte. A `bytearray` is a changeable sequence of bytes. In the ZIP format every member has two headers: a local one starting with the bytes `PK\x03\x04` and one in the central directory starting with `PK\x01\x02`. Each header has a flags field, 6 and 8 bytes after the signature respectively, in which the lowest bit means "encrypted".

The loop finds every header and switches that bit on. `data.find(signature, offset)` returns the position of the next occurrence at or after `offset`, or `-1` when there is none; the walrus operator stores it and the loop continues while it is `>= 0`. `|= 1` sets the lowest bit. `offset += 4` steps past the signature just found so the search moves on.

```python
        data = bytearray(zip_bytes(office_members()))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            info = archive.getinfo('word/document.xml')
            offset = info.header_offset + 30 + len(info.filename.encode()) + len(info.extra)
        data[offset] ^= 0xff
        item, _ = self.add('crc.docx', data)
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
```

**Pins down (second half):** a member whose data is damaged is detected, and the file is quarantined. **Input:** a fresh safe document in which one byte of compressed data is corrupted. The position is computed from the format: a member's data begins after its local header, which is 30 fixed bytes plus the file name plus an optional extra field. `^= 0xff` flips all eight bits of that byte. The archive's directory still looks perfect; the damage shows only when the member is actually decompressed and its checksum (CRC) compared. The test therefore proves that inspection reads every member to the end.

```python
    def test_external_relationships(self):
        rels = "<Relationships><Relationship TargetMode = 'External' Target='https://example.com'/></Relationships>"
        item, _ = self.add('external.docx', zip_bytes(office_members([('word/_rels/document.xml.rels', rels)])))
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** an Office document that refers to a resource on the internet is rejected. **Input:** a relationships file declaring an external target. The XML is written with spaces around `=` and single quotes on purpose: both are legal XML, and a check that searched the raw text for `TargetMode="External"` would miss it. Passing requires really parsing the XML.

```python
    def test_xml_declarations_in_utf16_and_beyond_prefix(self):
        for data in ('<!DOCTYPE root [<!ENTITY x "abc">]><root>&x;</root>'.encode('utf-16'),
                     b' ' * 1000100 + b'<!DOCTYPE root><root/>'):
            item, _ = self.add('unsafe.xml', data)
            self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** XML with a `DOCTYPE` or entity declaration is rejected however it is hidden. Such declarations are the basis of well-known attacks on XML parsers. **Input:** two attempts to hide one. In the first the document is encoded as UTF-16, so the bytes of `<!DOCTYPE` are not adjacent in the file and a byte search would not find them. In the second the declaration comes after more than a million spaces, beyond any "look at the first N bytes" shortcut.

```python
    def test_xml_malformed_and_depth(self):
        item, _ = self.add('bad.xml', b'<root>')
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
        self.policy['max_xml_depth'] = 2
        item, _ = self.add('deep.xml', b'<a><b><c/></b></a>')
        self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down:** broken XML is quarantined; XML nested deeper than the limit is rejected. **Input:** `<root>` with no closing tag, and a three-level document tested against a limit lowered to 2.

```python
    def test_pdf_active_names_and_missing_validator(self):
        for name in (b'JavaScript', b'JS', b'J#53', b'Launch', b'EmbeddedFile', b'OpenAction', b'AA'):
            item, _ = self.add('active.pdf', b'%PDF-1.4\n/' + name + b' 1\nstartxref\n0\n%%EOF')
            self.assertEqual(self.inspect(item).decision, D.REJECTED)
```

**Pins down (first part):** a PDF that can run something is rejected. **Input:** seven tiny files with the outer markers of a PDF (`%PDF-` at the start, `startxref` and `%%EOF` at the end) and one keyword each. The keywords are how a PDF declares scripts, programs to launch, embedded files and actions that run on opening. `J#53` is the keyword `JS` in disguise: PDF allows a character to be written as `#` plus its hexadecimal code, and `53` is `S`. The test requires inspection to decode that before looking. This part passes.

```python
        item, _ = self.add('plain.pdf', b'%PDF-1.4\n/AAPL:Keywords 1\nstartxref\n0\n%%EOF')
        self.assertEqual(self.inspect(item).decision, D.QUARANTINED)
        self.policy['require_deep_container_inspection'] = False
        result = self.inspect(item)
        self.assertEqual(result.decision, D.ACCEPTED)
        self.assertIn('pdf_validator_unavailable', result.flags)
```

**Pins down (second part):** three things. A harmless name that merely begins with `AA` (`/AAPL:Keywords`) must not be mistaken for the `/AA` action keyword. When the external PDF validator `pdfinfo` is missing and the policy requires deep inspection, the PDF is quarantined. When the policy does not require it, the PDF is accepted and carries the flag `pdf_validator_unavailable`, so the missing check is on record. `pdfinfo` is "missing" here because of the `shutil.which` patch in `setUp`.

**This is the test that fails today**, on its second line (line 304 of the file). The first assertion expects `QUARANTINED`, which is correct only when `require_deep_container_inspection` is `True`. The test never sets it to `True`; it relies on the value loaded from `configs/inspection.json`, and that file currently says `false`. With `false`, the PDF is accepted at once and the assertion fails.

This was reproduced outside the test file, using the same PDF bytes in a scratch directory with `shutil.which` patched the same way:

| `require_deep_container_inspection` | Decision | Flags | Error text |
|---|---|---|---|
| `True` | `quarantined` | none | `pdfinfo unavailable; PDF structure not validated` |
| `False` | `accepted_for_ingestion` | `pdf_validator_unavailable` | none |

So the inspection code does what the test describes for both settings. The code and the test agree with each other; the test and the configuration file do not.

```python
    def test_html_rtf_and_legacy(self):
        for name, data, expected in [('page.html', b'<html><body>hello</body></html>', D.ACCEPTED),
                                     ('page.html', b'<html><script>alert(1)</script></html>', D.REJECTED),
                                     ('safe.rtf', b'{\\rtf1 hello}', D.ACCEPTED),
                                     ('bad.rtf', b'{\\rtf1 \\object thing}', D.REJECTED),
                                     ('legacy.doc', b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1xxx', D.QUARANTINED)]:
            item, _ = self.add(name, data)
            self.assertEqual(self.inspect(item).decision, expected)
```

**Pins down:** the rules for three more formats. **Input:** five files. Plain HTML is accepted; HTML with a `<script>` element is rejected. Plain RTF is accepted; RTF with an embedded object (`\object`) is rejected. In the Python source `\\` inside a bytes literal is one backslash, so `b'{\\rtf1 hello}'` is the text `{\rtf1 hello}`. The last file begins with the eight signature bytes of the old binary Word format (`.doc`). Inspection recognises the format but has no safe way to check it, so it is quarantined.

```python
    def test_scanner_unavailable_never_clean(self):
        self.add('good.txt', b'hello')
        self.policy['require_malware_scan'] = True
        result = self.run_batch().artifacts[0]
        self.assertEqual(result.decision, D.QUARANTINED)
        self.assertEqual(result.malware_scan_status, M.UNAVAILABLE)
```

**Pins down:** "no scanner installed" is never reported as "clean". **Input:** a good text file, with the policy switched to require a malware scan, while `setUp`'s patch hides every scanner. The file is quarantined and its status is `UNAVAILABLE`. This is the opposite setting from the rest of the file, where `setUp` turns the requirement off.

```python
    def test_scanner_batch_fallback_and_infection(self):
        paths = [self.root / '1.txt', self.root / '2.txt']
        def run(command, **kwargs):
            self.assertNotIn('shell', kwargs)
            self.assertEqual(command[-2:], list(map(str, paths)))
            if command[0] == 'clamdscan':
                return subprocess.CompletedProcess(command, 2, '', 'daemon unavailable')
            return subprocess.CompletedProcess(command, 1, f'{paths[0]}: OK\n{paths[1]}: Eicar FOUND\n', '')
```

The next four tests check how inspection talks to a virus scanner without having one. This first one defines `run`, a fake for `subprocess.run` (the function that starts an external program).

The fake checks how it was called: `shell` must not be among the keyword arguments (running a command through a shell with file names in it is a classic security hole), and the last two items of the command must be the two paths. Then it answers like a scanner would. `CompletedProcess(command, returncode, stdout, stderr)` is the object `subprocess.run` returns. For `clamdscan` the fake reports exit code 2 and "daemon unavailable". For anything else it reports exit code 1 with one verdict line per file: the first `OK`, the second `Eicar FOUND`.

The two paths are never created; because the scanner is faked, nothing reads them.

```python
        with patch('src.corpus_factory.inspection.checks.shutil.which', side_effect=lambda name: name), patch('src.corpus_factory.inspection.checks.subprocess.run', side_effect=run) as scanner:
            result = _scan_snapshots(paths, self.policy)
        self.assertEqual(scanner.call_count, 2)
        self.assertEqual(result[paths[0]].status, M.CLEAN)
        self.assertEqual(result[paths[1]].status, M.INFECTED)
```

**Pins down:** when the first scanner fails, the second is tried; and a `FOUND` line means infected. **Input:** two patches in one `with`. `shutil.which` is patched so that both scanners appear installed — `side_effect=lambda name: name` makes the stand-in call that small function, which returns the name it was given. `subprocess.run` is patched with the fake above.

`scanner.call_count == 2` proves both programs were run: `clamdscan` first, which failed, then `clamscan`. The results are read per file: the first is `CLEAN`, the second `INFECTED`.

```python
    def test_scanner_missing_verdict_timeout_and_error(self):
        paths = [self.root / '1.txt']
        for response in (subprocess.CompletedProcess([], 0, '', ''), subprocess.CompletedProcess([], 2, f'{paths[0]}: OK\n', 'failed')):
            with patch('src.corpus_factory.inspection.checks.shutil.which', return_value='scanner'), patch('src.corpus_factory.inspection.checks.subprocess.run', return_value=response):
                self.assertEqual(_scan_snapshots(paths, self.policy)[paths[0]].status, M.ERROR)
        with patch('src.corpus_factory.inspection.checks.shutil.which', return_value='scanner'), patch('src.corpus_factory.inspection.checks.subprocess.run', side_effect=subprocess.TimeoutExpired('scanner', 1)):
            self.assertEqual(_scan_snapshots(paths, self.policy)[paths[0]].status, M.ERROR)
```

**Pins down:** anything short of a clear verdict is an error, never "clean". **Input:** three fake scanner behaviours for one path.

1. Exit code 0 and no output at all. The scanner "succeeded" but said nothing about the file → `ERROR`.
2. Exit code 2 (the scanner's own "something went wrong") although an `OK` line was printed → `ERROR`. The verdict line is not trusted when the program reports failure.
3. `side_effect=subprocess.TimeoutExpired('scanner', 1)`: when `side_effect` is an exception, the stand-in raises it when called. This imitates a scanner that hangs past its time limit → `ERROR`.

In the first two cases `return_value=response` makes the fake `subprocess.run` return a prepared object without running anything.

```python
    def test_infected_decision_and_changed_snapshot(self):
        item, path = self.add('good.txt', b'hello')
        result = self.inspect(item)
        infected = apply_malware_result(result, MalwareScanResult(M.INFECTED, 'test', 'Eicar'), self.policy)
        self.assertEqual(infected.decision, D.REJECTED)
        clean = apply_malware_result(infected, MalwareScanResult(M.CLEAN, 'test'), self.policy)
        self.assertEqual(clean.decision, D.REJECTED)
        path.write_bytes(b'world')
        self.assertEqual(scan_malware_batch(self.batch, [result], self.policy)[item['artifact_id']].status, M.ERROR)
```

**Pins down:** two things. First, an infected verdict rejects the file, and a later clean verdict cannot bring it back — the "never downgrades" rule from the first test, seen at the level of a whole artifact. **Input:** an accepted artifact result, to which the test applies hand-made scan results: `MalwareScanResult(status, engine, signature)`.

Second, the file given to the scanner must be the file that was inspected. After inspection recorded the hash of `hello`, the test overwrites the file with `world` and calls `scan_malware_batch` with the old result. Inspection copies each file to a private snapshot for the scanner and re-hashes it on the way; the hash no longer matches, so the status is `ERROR` and nothing is scanned.

```python
    def test_malware_chunks_bound_bytes_and_count(self):
        artifacts = [self.inspect(self.add(f'{i}.txt', b'hello')[0]) for i in range(5)]
        self.policy['max_malware_chunk_bytes'] = 10
        self.policy['malware_chunk_size'] = 3
        def scan(paths, policy):
            self.assertLessEqual(sum(p.stat().st_size for p in paths), 10)
            return {p: MalwareScanResult(M.CLEAN, 'test') for p in paths}
        with patch('src.corpus_factory.inspection.checks._scan_snapshots', side_effect=scan) as scanner:
            result = scan_malware_batch(self.batch, artifacts, self.policy)
        self.assertEqual(scanner.call_count, 3)
        self.assertEqual(len(result), 5)
```

**Pins down:** files are handed to the scanner in groups limited by total size and by count. **Input:** five 5-byte files. The first line is dense: `self.add(...)` returns `(item, path)`, `[0]` takes the item, `self.inspect(...)` inspects it, and the list comprehension does that for `i` from 0 to 4.

The limits are set to 10 bytes and 3 files per group. Two files already reach 10 bytes, so the groups are 2 + 2 + 1. The fake `scan` function checks on every call that the snapshot files it was given total at most 10 bytes, and reports everything clean. `call_count == 3` confirms the grouping, and `len(result) == 5` confirms that every file received a verdict.

```python
    def test_reports_immutable_and_quarantine_references(self):
        self.add('good.txt', b'hello')
        self.add('bad.pdf', b'fake')
        result = self.run_batch()
        before = {p: p.read_bytes() for p in self.batch.rglob('*') if p.is_file()}
        catalog = self.root / 'catalog'
        one = write_inspection_report(self.batch, result, catalog)
        two = write_inspection_report(self.batch, result, catalog)
        self.assertNotEqual(one, two)
        self.assertEqual(hashlib.sha256(one.read_bytes()).hexdigest(), one.with_suffix('.json.sha256').read_text().strip())
```

The longest test. It covers what inspection leaves on disk — the records that the provenance and ingestion stages read (4.3, 4.4). **Input:** a batch with one good file and one fake PDF (quarantined), inspected once. `catalog` is a folder inside the temporary directory, passed in place of the real `storage/catalog/inspections`.

`before` is a dictionary comprehension: for every file in the batch folder, its path mapped to its bytes. It is a snapshot to compare against at the end.

**Pins down so far:** writing a report twice for the same result gives two different records (`one != two`): each call gets a new inspection id, and nothing is overwritten. And the checksum file next to a report contains the SHA-256 of the report's bytes.

```python
        record = json.loads(one.read_text())
        self.assertEqual(record['next_stage'], 'ingestion')
        self.assertEqual(record['eligible_artifact_ids'], ['a0'])
        quarantine = quarantine_batch(self.batch, result, one.parent.name, self.root / 'quarantine')
        self.assertEqual(json.loads(quarantine.read_text())['artifacts'][0]['artifact_id'], 'a1')
        with self.assertRaises(FileExistsError):
            publish_record(catalog, one.parent.name, 'manifest.json', {})
```

**Pins down:** the content of the records. The report says the batch may go on to ingestion and lists exactly the accepted artifact, `a0`. The quarantine record, written by `quarantine_batch` into a temporary quarantine folder, lists the other one, `a1`. `one.parent.name` is the name of the report's folder, which is the inspection id.

`with self.assertRaises(FileExistsError):` asserts that the indented code raises that exception; the test fails if it does not. Publishing a second record under an id that already exists must be refused. That is the "immutable" in the test's name: a published record is never replaced.

```python
        self.assertEqual(before, {p: p.read_bytes() for p in self.batch.rglob('*') if p.is_file()})
        self.assertIn(str(self.batch), completed_batches(self.policy, catalog, self.root / 'quarantine'))
        self.assertNotIn(str(self.batch), completed_batches(self.policy, catalog, self.root / 'missing-quarantine'))
        changed = {**self.policy, 'max_line_characters': 17}
        self.assertNotIn(str(self.batch), completed_batches(changed, catalog))
```

**Pins down:** four more facts.

1. The batch folder is byte-for-byte what it was before reporting and quarantining. Inspection observes; it never modifies or moves incoming files. Quarantine is a record that refers to a file, not a place files are moved to.
2. `completed_batches` — the function `scripts/inspection.py` uses to skip batches already inspected — counts this batch as done when given the catalog and the quarantine folder.
3. It does not count the batch as done when the quarantine record cannot be found (a folder that does not exist is passed). A report that mentions quarantined files is only complete together with its quarantine record.
4. It does not count the batch as done under a different policy. `{**self.policy, 'max_line_characters': 17}` builds a copy of the policy with one value changed. An inspection made under old rules does not satisfy new rules, so the batch would be inspected again.

In the last call no quarantine folder is passed, so the function's default — the real `storage/quarantine` — applies. It is not reached: the policy comparison fails first and the record is skipped before any quarantine file is looked up.

```python
    def test_bad_config_rejected(self):
        for key, value in [('max_file_size_bytes', True), ('max_line_characters', 0),
                           ('max_compression_ratio', float('inf')), ('require_malware_scan', 'yes'),
                           ('unknown_file_policy', 'accept'), ('expected_mime_types', {})]:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Inspection config'):
                validate_inspection_config({**self.policy, key: value})
```

**Pins down:** a nonsensical policy is refused before any inspection starts. **Input:** six copies of the valid policy, each with one bad value: `True` where a number is required (Python would otherwise treat `True` as `1`), a limit of zero, an infinite ratio, the text `'yes'` where a true/false value is required, an unknown-file policy of `'accept'` (only `quarantine` and `reject` exist — there is deliberately no way to configure "accept unknown files"), and an empty table of expected content types.

`assertRaisesRegex(ValueError, 'Inspection config')` requires both the exception type and that its message contains that text.

```python
if __name__ == '__main__':
    unittest.main()
```

The standard ending of a `unittest` file: when the file is run as a program, `unittest.main()` finds and runs the tests in it. As noted above, running this particular file directly fails earlier, at its imports, so in practice these two lines are not what starts the tests; the `python -m unittest …` command is.

### What the tests do not cover

Within inspection, the tests call the library functions. The command-line script `scripts/inspection.py` (argument handling, choosing which batches to inspect) is not run by any test.

Outside inspection there are no tests at all. These backend areas have no test file:

| Area | Code |
|---|---|
| Acquisition | `src/corpus_factory/acquisition/` |
| Provenance | `src/corpus_factory/provenance/` |
| Ingestion | `src/corpus_factory/ingestion/` |
| Extraction | `src/corpus_factory/extraction/` |
| Preprocessing | `src/corpus_factory/preprocessing/` (cleaning, normalization, filtering, deduplication) |
| Dataset | `src/dataset/` |
| Tokenization | `src/tokenization/` |
| Model | `src/model/` |
| Training | `src/training/` |
| Evaluation | `src/evaluation/` |
| Inference | `src/inference/` |
| Serving | `src/serving/` |
| Entry-point scripts | `scripts/` (all of them) |
| Shared modules | `paths.py`, `config.py` |

---

## Appendix B. Things to revisit after the course

This appendix collects what was noticed while reading the code line by line: empty files, unused code, places where two parts of the system disagree, and behaviour that is easy to misread. **Nothing here has been changed.** The list is the baseline's known rough edges, to be weighed before the next phase of work. It is not a plan.

Items are grouped by the chapter they belong to. Most are small. The ones that affect what a training result means, or that can silently corrupt a later run, are gathered first.

### Read these first

- **There is no held-out data.** The corpus is one document, validation and test are empty, and every loss or perplexity figure is measured on training text. (Chapters 5, 9, 14.)
- **The split of a document can change later.** The tiny-corpus rule moved the only document from validation to train. When more documents arrive it can move back, after the model has trained on it. (Chapter 5.)
- **Running ingestion twice duplicates documents**, and the later stages never delete old output files. What reaches the dataset can include leftovers from earlier runs. (Chapters 4.4, 4.6, 12.)
- **Vocabulary size is fixed in two unconnected places**: the tokenizer training script and the model configuration. They agree today by coincidence of the same number being typed twice. (Chapters 6, 7, 12.)
- **Changing the learning rate and resuming has no effect**, because the restored optimizer state carries the old value. (Chapter 8.)
- **The tokenizer and the checkpoints are not tied together.** A retrained tokenizer with the same vocabulary size would be accepted with an old checkpoint and produce nonsense; the server also keeps the old tokenizer until it restarts. (Chapters 6, 11.)
- **Extraction handles far fewer file types than inspection accepts.** Only `.txt` and `.md` become text; everything else that passes inspection stops at extraction. (Chapters 4.2, 4.5.)
- **Inspection is more permissive than its README says**: malware scanning and deep validation are not required by the current config. One test fails for the same reason. (Chapter 4.2, Appendix A.)
- **`/admin` has no authentication** and relies on the server listening only on `127.0.0.1`. (Chapter 11.)
- **Only the inspection stage has tests.** (Appendix A.)

### Project root, `paths.py` and `configs/`

- **Empty files** — `config.py` at the project root (imported by nothing, and easily confused with the three real `config.py` files under `src/`), `src/training/optimizer.py`, and the `pdf`, `docx` and `md` readers under `src/corpus_factory/extraction/readers/`.
- **Extraction accepts far less than inspection allows** — `extractor.py` handles only `.txt` and `.md`, while `configs/inspection.json` allows 24 extensions.
- **Leftover folders** — six directories directly under `src/` (`acquisition`, `extraction`, `ingestion`, `inspection`, `preprocessing`, `provenance`) hold only stale `__pycache__` files from before the move to `corpus_factory/`. Four empty `preprocessing/<stage>/` folders hold only `.gitkeep`.
- **`paths.py`, unused constants** — `LOGS_DIR` and `EVALUATIONS_DIR` are used by nothing. `INCOMING_DIR`, `ARTIFACTS_DIR`, `TOKENIZER_DIR`, `CATALOG_DIR` and `APPS_DIR` are used only inside `paths.py` itself.
- **`paths.py`, missing constants** — there are none for `processed/<stage>`, `training/dataset` or `training/tokenized`. Each script retypes those folder names, so a typo would break the chain silently.
- **The same folder is defined twice** — `src/corpus_factory/inspection/report.py` defines its own `INSPECTIONS_DIR` instead of importing `INSPECTIONS_CATALOG_DIR`.
- **`requirements.txt`** pins no versions. `numpy` is listed but imported nowhere; `pydantic` is imported by serving but arrives only through `fastapi`; the optional inspection tools (`magic`, `clamscan`, `pdfinfo`) are not mentioned.
- **`.gitignore`** — the exceptions for `storage/.gitkeep` and `artifacts/.gitkeep` name files that do not exist; the real `.gitkeep` files are one level deeper and are tracked only because they were added explicitly.
- **Stale documents** — `docs/COURSE.md` describes an older, different project layout, and `docs/pipeline.md` marks only acquisition and inspection as done.
- **`configs/training.json`** gets no validation beyond "is a JSON object", while `configs/inspection.json` is validated strictly.
- **`epochs` is a target total, not an increment** — with `resume` on and the value unchanged, a second run trains nothing. The name does not say so.
- **`inspection.json`, `malware_chunk_size`** is a number of files, not a size.

### Acquisition (`src/corpus_factory/acquisition/`)

- **`batch.py`** imports `sha256_file` and never uses it; the chunked hash loop is written out again in two functions.
- **No cleanup on failure** — an interrupted run leaves a batch folder with objects and no `source.json`. Discovery ignores it and the source is acquired again, but `scripts/inspection.py` lists every folder under `BATCHES_DIR` and will still see the orphan.
- **`_safe_source_name` keeps only ASCII** — an all-Arabic folder name becomes `unattributed`, the same batch-id prefix as loose files. The manifest still records the real name.
- **Sub-folder paths are lost** — files are collected recursively, but only the file name is recorded.
- **"Immutable" is a declaration** — the manifest says so and files are created in exclusive mode, but nothing makes the stored files read-only.
- **`intake.py`, hidden files** — only the file's own name is checked, so a normally named file inside a hidden sub-folder would be acquired.
- **`origin.json` is not validated** — a missing or empty `platform` is written to the manifest, discovery then skips that manifest, and the source is acquired again on every run.
- **`discovery.py`** — a `source.json` that is valid JSON but not an object raises an uncaught error. The variable `source_name` actually holds the platform.
- **The "already acquired" fingerprint** — changing only `attribution`, `license_identifier`, `source_url` or `source_type` in `origin.json` is treated as already acquired, so corrected licence metadata never reaches a manifest. Any one-file change re-copies the whole source, and each new file is read twice.
- **README versus code** — the acquisition README's example numbers files in a different order from the code (which sorts), and does not mention recursion or skipped dot-files.

### Inspection (`src/corpus_factory/inspection/`)

- **The README and the config disagree** — the inspection README says malware scanning and deep validation are required by default. `configs/inspection.json` sets both `require_malware_scan` and `require_deep_container_inspection` to `false`, so a missing validator or an unavailable scanner only adds a flag and the artifact is still accepted.
- **`.doc` is allowed but can never pass** — it is in `allowed_extensions` and `expected_mime_types`, yet `inspect_deep_container` raises for `.doc` unconditionally, so every `.doc` is quarantined.
- **`deep_inspection.py`, RTF screen** — the pattern for `\bin` does not match `\bin` followed directly by digits, and in RTF `\bin` is always followed by a number. A test input `{\rtf1 \bin4 abcd}` is accepted. The `\bin` check is effectively inactive.
- **`checks.py`, type detection of text starting with `<`** — anything beginning with `<` that is not an obvious HTML opening is labelled XML. HTML fragments, pages that start with a comment, and `.md` or `.txt` files that start with `<` are quarantined as type mismatches.
- **`checks.py`, files starting with `#!`** are classed as shell scripts and rejected, including a text or Markdown file that happens to start that way.
- **`deep_inspection.py`, PDF scan** — it cannot see names inside compressed object streams, it rejects any PDF with an open action (including a harmless "open at page 1"), and its short byte patterns can match by chance inside compressed data.
- **`deep_inspection.py`, XML and HTML** — any `<!DOCTYPE>` in XML is rejected; XML or JSON over 16 MiB is quarantined although the file-size limit is 2 GiB; in HTML any attribute starting with "on" and any `data:` URL rejects the whole file.
- **`checks.py`, symlink walk** — it starts at the filesystem root. If the project ever sits under a symlinked directory, every artifact is rejected.
- **Dead or unused code in `checks.py`** — `detect_mime_type` is called nowhere; the `policy` parameter of `inspect_text` is unused; one half of a symlink condition can never be true.
- **Unreachable config values** — four `blocked_mime_types` and five `expected_mime_types` can only be produced by the `python-magic` fallback, which is not installed.
- **`report.py`, completion is keyed on an absolute path** — moving or renaming the project makes every batch pending again. Inspection reports and quarantine records also contain absolute home-directory paths.
- **`report.py`, any policy edit makes all batches pending** — the next run re-inspects everything and appends new records. This is intended, but the catalog grows: there are already 15 inspection records for 8 batches.
- **Report fields nobody reads** — `eligible_artifact_ids` and `next_stage` are written, but ingestion filters on each artifact's own `decision`.
- **Two checksum conventions** — acquisition writes its `.sha256` without a trailing newline; inspection writes one with it. Both readers strip whitespace, so it works.
- **A checksum beside its manifest** detects accidental damage or a careless edit, not a consistent rewrite of both files.

### Provenance (`src/corpus_factory/provenance/`)

- **`scripts/provenance.py` only prints a report** — it writes nothing. The real gate runs inside `scripts/ingestion.py`.
- **`gate.py`, a misleading status** — with no decision record, `evaluate_training_rights` returns `allowed=False` but copies the licence's `training_use` into `status`, so a hand-edited `source.json` can show `status='allowed'` together with `allowed=False`. Callers only test `allowed`.
- **`gate.py`, tampering is silent** — decision records with a bad checksum are skipped without warning, so damaging the newest decision makes the previous one take effect. An empty `.sha256` file raises an uncaught error. Every call re-hashes the whole catalog.
- **`gate.py`, "latest" is a string sort on `created_at`** — correct except in a one-in-a-million case where the timestamp has exactly zero microseconds.
- **`decision.py`** — the batch id is not checked against existing batches, and the record and its checksum are written directly rather than with write-then-replace.

### Ingestion (`src/corpus_factory/ingestion/`)

- **Four of the five files are unused** — `loader.py`, `dispatcher.py`, `worker.py` and `document.py` form a chain that nothing imports. `worker.process_file` never reads the file and sets `raw_text=None`. The ingestion README still describes this chain and refers to `data/raw`.
- **`ingest.py`, random document ids** — every run copies each file again under a new id (see Scripts).
- **`ingest.py`, the hash is not recomputed** — the `sha256` in the raw manifest is carried over from the inspection record rather than computed on the copy.
- **`ingest.py`, absolute paths** — `source_path` in the raw manifest is an absolute machine path.
- **The raw manifest's checksum is never verified** by anything downstream.

### Extraction (`src/corpus_factory/extraction/`)

- **Only `.txt` and `.md` are extracted** — accepted PDF, DOCX, HTML, JSON and CSV files are ingested into `storage/raw` and then skipped.
- **UTF-16 text is accepted by inspection but skipped by extraction**, which decodes UTF-8 only.
- **A UTF-8 byte-order mark survives** as an invisible character at the start of the text; neither cleaning nor normalization removes it.
- **`readers/`** — `txt_reader.read_txt` is unused and duplicates `extract_text`; the `md`, `pdf` and `docx` readers are empty.

### Preprocessing (`src/corpus_factory/preprocessing/`)

- **`cleaning.py`** — the two carriage-return replacements do nothing in the real pipeline, because the text is read in a mode that has already translated line endings. Runs of blank lines inside the text, the byte-order mark and control characters are not touched.
- **`filtering.py`** — the threshold of 20 is hard-coded and counts characters of the unstripped text, so 19 spaces plus one letter passes, as do 20 exclamation marks. There is no language or quality check. The rejection reason is printed, never stored.
- **`deduplication.py`** — exact match only. The set of seen hashes is rebuilt on each run, and "first wins" follows sorted batch and document id, not upload order.
- **Layout** — `cleaning.py` sits next to an empty `cleaning/` folder, and likewise for the other three stages.
- **`utc_now()`** is defined three times, in provenance, ingestion and inspection.

### Tests (`tests/`)

- **One test currently fails** — `test_pdf_active_names_and_missing_validator` loads the real `configs/inspection.json` and assumes `require_deep_container_inspection` is `true`; the config now says `false`. The inspection code behaves as the test describes for each value, so the mismatch is between the test and the config. 37 of 38 tests pass.
- **Only inspection is tested** — there are no tests for acquisition, provenance, ingestion, extraction, preprocessing, the dataset, tokenization, the model, training, evaluation, inference, serving, or any script.
- **`pytest` is not installed**; the suite runs with the standard library's `unittest`.

### Dataset (`src/dataset/`)

- **`builder.py`, `assign_splits`** — the tiny-corpus rule makes a document's split depend on the rest of the corpus. Today's only document is a validation document by hash and was moved to train. When a second document lands in train by hash, the first silently returns to validation after the model has trained on it. That is leakage unless you retrain.
- **No held-out data today** — `validation.jsonl` and `test.jsonl` are empty, so every evaluation number is measured on training text.
- **`loader.py`, `make_training_examples`**
  - Chunks do not overlap, so every chunk after the first starts with no left context.
  - The last partial chunk can be as short as one token and is treated as a full training step.
  - There is no shuffling and no batching.
  - The `if len(chunk) < 2: continue` guard cannot be reached for any positive `context_length`, and `context_length=0` raises a bare `range()` error with no explanation.
- **`loader.py`, `load_token_sequences`** — checks only that `input_ids` is a list, not that its elements are integers within the vocabulary.
- **`num_tokens`** — written by `scripts/tokenize_dataset.py` but never read anywhere.

### Tokenization (`src/tokenization/`)

- **Vocabulary size is hardcoded in two unrelated places** — `target_vocab_size=300` in `scripts/tokenizer_training.py` and `vocab_size = 300` in `src/model/config.py`. They agree only because the corpus happened to yield all 41 merges. If BPE stopped early or the target changed, the model config would not follow.
- **The tokenizer is fitted to one document** — 41 merges from 536 bytes, the last ones being whole words that occur twice. English text gets no merges at all.
- **`bpe.py`, `train_bpe`** — recounts all pairs from scratch on every merge and holds the whole corpus in memory, which defeats the streaming in `load_texts`. Fine at 536 bytes; it will not scale. It also prints progress from inside library code.
- **`bpe.py`, `BYTE_VOCAB_SIZE`** — defined but never used; `tokenizer.py` writes `256` directly instead.
- **`PAD_ID`** — reserved and exposed, but nothing inserts PAD because there is no batching. Its only use is being excluded during generation.
- **Tokens that cut through a character** — BPE merges across UTF-8 character boundaries, so some learned tokens end on the first byte of a character and one starts on a second byte. This is normal for byte-level BPE, and it is the reason inference needs its UTF-8 constraint.
- **`tokenizer.py`, `decode(skip_special_tokens=False)`** — raises `ValueError` rather than showing `<BOS>`/`<EOS>`, which the parameter name does not suggest. The `"token"` strings stored in the JSON are never used.
- **`tokenizer.py`, `load`** — reads only `"merges"`. The other fields (`type`, `version`, `special_tokens`, `first_merge_id`, `vocab_size`) are not checked, so a file with different special ids would load silently using the constants in `bpe.py`.
- **`tokenizer.py`, `save`** — a direct write, not the write-then-replace used for checkpoints and manifests.
- **`tokenizer.py`, `encode`** — makes one full pass over the sequence per merge. The cost grows with merges × length.

### Model (`src/model/`)

- **`config.py`, `vocab_size: int = 300`** — hardcoded, not derived from the tokenizer. `scripts/train.py` uses `ModelConfig()` as is, so the model and tokenizer agree only because `scripts/tokenizer_training.py` also hardcodes 300. Only serving checks the match when it loads a model; a mismatch during training would surface as an index error or as silently unused rows.
- **`model.py`, `lm_head`** — the output head is not tied to the token embedding. That is a legitimate choice, but it spends 38,400 parameters (4.3%) on a second table.
- **`attention.py`, causal mask** — rebuilt on every forward call in every layer instead of being stored once. Correct, slightly wasteful.
- **No custom weight initialisation** anywhere in `src/model/`; PyTorch defaults apply. Token and position embeddings start with a standard deviation near 1 while `Linear` weights are bounded by about 0.088, so the embeddings are much larger than everything else at the start.
- **Dropout** is 0.0, and the only dropouts are on the attention weights and at the end of the feed-forward network. The dropout paths are effectively untested.
- **`embeddings.py`** — `batch_size` is unpacked but never used; it only acts as an implicit two-dimensional check.
- **`transformer.py`** — the feed-forward expansion factor 4 is hardcoded, not a `ModelConfig` field, so it is not recorded in checkpoints. Changing it would make old checkpoints fail on shape with no hint in the saved config.
- **`TinyLLM.forward`** has no length handling of its own and relies on the embedding's `ValueError`; every caller must crop to `context_length`.
- **`d_model` and `context_length` are both 128**, which makes transposed-dimension bugs harder to spot.
- **Checkpoint parameter names come from attribute names** (`blocks.N.feed_forward.net.0.weight` and so on). Renaming an attribute or reordering the `nn.Sequential` breaks loading of existing checkpoints.

### Training (`src/training/`) and evaluation (`src/evaluation/`)

- **`optimizer.py`** — empty and imported nowhere. The optimizer is built inline in `trainer.py`.
- **`trainer.py`, resume and the learning rate** — restoring the optimizer state also restores its learning rate, which overrides the value just read from `configs/training.json`. Editing `learning_rate` and resuming therefore has no effect on the optimizer, yet the saved stats record the new value. (Checked: resumed with 0.01; the optimizer still used 0.0003 while the stats said 0.01.)
- **`trainer.py`, stale `validation_loss`** — when validation yields no examples, `validation_loss` keeps the value restored from the checkpoint and is written into the new stats as if it were current.
- **`trainer.py`, the final save** — it runs no validation and never marks a checkpoint as best, so a save that falls off the `checkpoint_every_epochs` cadence can never update the best file.
- **The best checkpoint is never produced today** — the validation file is empty, so `best_tiny_model.pt` does not exist. Nothing loads the best file anyway; inference and serving use the latest.
- **Loss averaging (`trainer.py` and `evaluator.py`)** — the average is over per-example means and is not weighted by token count. Today a 2-token chunk counts as much as a 128-token chunk, and perplexity inherits this. `final_loss` is also an average over an epoch during which the model was changing (2.1077), not the loss of the finished model (2.0433).
- **Training-loop facts** — batch size is fixed at 1; there is no shuffling, no gradient clipping, and no learning-rate schedule or warm-up. Weight decay is 0.01 because that is PyTorch's AdamW default, not because the config chose it, and it applies to every parameter including biases, LayerNorm and embeddings.
- **`scripts/train.py` builds `ModelConfig()` from the defaults**, not from the configuration stored in the checkpoint. If the defaults change, resume fails inside `load_state_dict` rather than with a clear message.
- **`artifacts/checkpoints/` is older than the code** — it holds 21 history files written before retention existed, the stored `training_config` has no `keep_last_checkpoints`, and the stored stats have no validation fields. The next save will delete all but the newest three history files.
- **`checkpoint.py`, `prune_history`** — it looks at every history file in the folder regardless of which model or run wrote it. With `keep_last_checkpoints` of 0 or less it deletes every history file. Leftover `*.tmp` files from an interrupted save are never cleaned up.
- **Run records (`run.py`, `scripts/train.py`)**
  - A run folder is created before the resume check, so an "already completed" invocation still creates a run marked `completed`.
  - A crashed run stays `"status": "running"` forever; there is no failed status.
  - `run.json` stores an absolute `checkpoint_path`, which contains the home-directory path. (The admin API returns only the file name.)
  - The first write of `run.json` is not atomic, while the final one is.
- **`training_seconds`** includes validation and checkpoint-writing time.
- **`config.py`** — checks only that the JSON is an object. A missing `epochs` or `learning_rate` appears as a bare `KeyError`, and there are no type or range checks.
- **`scripts/evaluate.py`** — results are only printed. `artifacts/evaluations/` is empty, and `EVALUATIONS_DIR` and `LOGS_DIR` in `paths.py` are not used by these stages.
- **`evaluator.py`** — leaves the model in evaluation mode and relies on the caller to switch back (the trainer does). With dropout at 0.0 the two modes currently give identical numbers.
- **No measurement of generalisation exists** — validation and test are empty and the corpus is one 259-token document, so the perplexity of 7.7 is purely fit to the training text.

### Inference (`src/inference/generator.py`)

- **`apply_utf8_constraint`, cost** — a Python loop over the whole vocabulary on every step, re-checking the entire byte history for each candidate token. About half a millisecond per step at a vocabulary of 300; it grows with vocabulary size and with output length.
- **`generate`, no caching** — the full context is run through the model again at every step.
- **`generate`, prompt in the output** — the returned text always includes the prompt, so the server's `text` field is prompt plus continuation.
- **`generate`, default temperature** — the function defaults to 1.0, while the server and `scripts/inference.py` pass 0.0.
- **`generate`, token budget** — the final cleanup of an unfinished character can return fewer than `max_new_tokens` tokens.

### Serving (`src/serving/`)

**`model_manager.py`**

- **A server path can leak** — when the tokenizer file is missing, the error text contains the full absolute tokenizer path, and `server.py` returns it to the client as the 503 `detail`. This contradicts the rule in `admin.py` that absolute paths are not part of the API.
- **The tokenizer is cached for the life of the process** — unlike checkpoints, it has no file-signature check. Retraining the tokenizer without restarting the server leaves the old one in use; a new checkpoint with the same vocabulary size would pass the check and produce nonsense.
- **A vocabulary mismatch hides the checkpoint** — it is marked unusable under the checkpoint's signature. If the tokenizer was the cause and is fixed later, the checkpoint stays hidden from `/models` until its file changes or the server restarts.
- **Config validation is one-sided** — `ModelConfig(**config)` rejects unknown keys only. Missing keys silently take the defaults, so a truncated config is not detected.
- **Reading metadata is expensive** — the whole checkpoint, optimizer state included, is read to extract a few numbers. The first `/models?include_checkpoints=true` reads all 22 files while holding the manager lock.
- **A deleted file can cause a 500** — a checkpoint removed between discovery and `stat()` raises an unhandled error.
- **"Latest" means "the default file name if present, else the newest file"** — a newer model with another name is not latest.
- **A folder with only per-epoch checkpoints** gives `404 No models found`, although each is loadable by its explicit id.
- **Hiding per-epoch checkpoints is presentation only** — `load` ignores `kind`, so any of them can be loaded by id.
- **Other exceptions during load** (for example from building the model) are neither marked unusable nor mapped to a clear status; the client gets a generic 500.

**`server.py`**

- **No authentication on `/admin`** — the admin API and console rely solely on the server being bound to `127.0.0.1`. The TODO's wording ("like the /admin API routes") reads as if those routes were already protected; they are not.
- **Error details reach the client** — a failed generation returns the exception type and message.
- **Model loading is outside the generation lock** — a model can be loaded onto the device while another generation is running.
- **An empty model id** (`""`) is treated as "use the latest" rather than as invalid.
- **Whether an app is built is decided at import time**, so building an app needs a server restart.
- **`openapi_url`** — the non-default path has no comment explaining why.

**`admin.py`**

- **`count_files`** filters hidden file names only; files inside hidden directories are still counted.
- **`read_runs`** — a non-string `started_at` in a `run.json` would break the sort and fail the whole endpoint. Only `checkpoint_path` is reduced to a file name; the config and stats objects are passed through as they are.
- **`data_summary`** walks `storage/uploads` and reads the dataset files line by line on every request, with no caching.

### Scripts (`scripts/`)

- **`ingestion.py` is not safe to run twice** — each call gives every file a new random document id, and there is no "already ingested" check. A second run copies every accepted file again and rewrites the manifest to list only the new ids. The old raw objects become orphans, and their old text files keep flowing downstream until deduplication collapses them.
- **The file-in, file-out stages never delete** (`extraction`, `cleaning`, `normalization`, `filtering`, `deduplication`) — a document that was accepted earlier and is rejected or duplicate now keeps its old output file, and `dataset_building` picks up everything in `deduplicated/`.
- **`provenance_review.py`** does not check that the batch id exists. A typo records a valid decision for a batch that does not exist, and the real one stays blocked.
- **`train.py`** builds the model from `ModelConfig()` defaults and never reads the tokenizer or the checkpoint's stored configuration.
- **`model_stats.py`** hardcodes `context_length = 128` instead of using the checkpoint's config, re-implements the example loop by hand, and prints the tokenizer's vocabulary size rather than the model's, so a mismatch would be invisible.
- **`tokenize_dataset.py`** opens each output file for writing before opening its input. A missing input split leaves that split's tokenized file emptied, then fails, and later splits are not processed.
- **`dataset_building.py`** empties all three dataset files even when there are no documents to write.
- **Two different ways of finding a batch id** — `provenance.py` and `ingestion.py` each have their own helper, with different branches. `provenance.py` also lists every inspection record, so a batch inspected twice is printed twice.
- **`ingestion.py`** reads inspection manifests without verifying their checksum, and "latest inspection" relies on the alphabetical order of folder names.
- **`extraction.py`** — a `.txt` file that is not valid UTF-8 is reported as skipped, while a missing file crashes.
- **`evaluate.py`** evaluates only the latest checkpoint and writes no file.
- **`scripts/README.md`** — every `python -m scripts.…` command in it works as written, but it hardcodes one real batch id, and it contains lines that are notes rather than commands (including a sentence pasted from a chat reply).
- **Unused imports** — `Path` in `extraction.py`, `cleaning.py` and `dataset_building.py`; `json` in `model_stats.py`.
