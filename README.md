# JSM: A GPT-Style Language Model From First Principles

JSM is an educational PyTorch decoder language model. Core mechanisms are implemented locally: Byte-Level BPE, shifted datasets, multi-head/GQA causal attention, pre-norm Transformer blocks, generation, sampling, KV caching, training, checkpointing, and evaluation. PyTorch supplies tensors, autograd, and device kernels; no pretrained model, tokenizer, or external tokenizer library is used.

## Layout

```text
jsm/                 production modules and executable scripts
jsm/data/raw/        separate local corpus documents
jsm/artifacts/       generated tokenizer and checkpoint
jsm/lessons/         preserved focused educational experiments
docs/                concept and engineering notes
tests/               lightweight automated tests (Phase 36)
```

## Commands

From the repository root:

```bash
python3 jsm/train_tokenizer.py
python3 jsm/train.py --epochs 20
python3 jsm/inference.py
python3 jsm/inference.py "language models"
python3 jsm/inference.py --interactive
python3 jsm/evaluate.py
python3 jsm/debug_shapes.py
python3 jsm/scale_report.py
```

Paths are resolved relative to the production directory, so these commands also work when launched from `jsm/` without changing artifact/data locations.

See `LLM_UPGRADE_PROGRESS.md` for verified phases and known limitations.

## Next Learning Stage — From Building the LLM to Understanding Intelligence

The core GPT-style LLM architecture and training pipeline are now implemented.

The next stage of learning moves away from simply adding more model components and focuses on understanding **how a model actually learns language, knowledge, reasoning, behavior, and useful intelligence from data and training**.

### Learning Roadmap

```text
LLM Architecture                    ✅
Tokenizer + Dataset                 ✅
Transformer + Attention             ✅
Training + Backpropagation          ✅
Generation + Sampling               ✅
Evaluation + Scaling Architecture   ✅

                ↓

NEXT STAGE

Pretraining
↓
Data Quality & Data Mixture
↓
How Weights Learn Language
↓
Scaling Laws
↓
Training Dynamics
↓
Generalization vs Memorization
↓
Knowledge Acquisition
↓
Reasoning Training
↓
Post-Training
↓
Instruction Tuning
↓
Supervised Fine-Tuning
↓
Preference / Alignment Training
↓
Reasoning & Verification
↓
Tool Use
↓
RAG
↓
Memory
↓
Agents
↓
Multimodal Models
↓
Model Evaluation & Benchmarks
↓
Production Foundation Models
```

### Stage 1 — How Pretraining Creates Intelligence

Learn what actually happens when billions of tokens pass through a Transformer.

Topics:

* Random initialization of model weights
* Forward pass through billions of token sequences
* Next-token prediction as the learning objective
* Cross-entropy loss
* Backpropagation through all Transformer layers
* Gradient-based weight updates
* How repeated prediction errors gradually produce useful internal representations
* Why next-token prediction can teach grammar, facts, relationships, style, structure, and patterns of reasoning
* What embeddings and hidden states become during training
* How early, middle, and later Transformer layers may develop different representations

Core question:

> How do random numbers inside a neural network become a language model that can understand and generate useful language?

---

### Stage 2 — Data Engineering for Foundation Models

Study how training data affects model capability.

Topics:

* Raw corpus collection
* Provenance and licensing
* Text extraction
* Cleaning
* Unicode normalization
* Language identification
* Arabic dialect identification
* Exact deduplication
* Near deduplication
* Semantic deduplication
* Quality scoring
* Filtering
* Toxicity and unsafe-content handling
* Document boundaries
* Data contamination
* Benchmark contamination
* Data mixture design
* Sampling ratios
* Curriculum strategies

Example data mixture:

```text
Arabic / Saudi data
General Arabic
English
Programming
Mathematics
Science
Reasoning
Books
Technical documents
Conversations
High-quality educational material
```

The goal is to understand that:

```text
Model Architecture
+
Training Data
+
Training Objective
+
Optimization
+
Compute
=
Model Capability
```

---

### Stage 3 — Scaling Laws

Understand what happens when increasing:

```text
Parameters
Training Tokens
Compute
Context Length
Batch Size
Dataset Quality
```

Study:

* Parameters vs tokens
* Undertraining
* Overtraining
* Chinchilla-style compute-efficient training
* Training FLOPs
* Token budgets
* Model width vs depth
* Data scaling
* Compute scaling
* Why simply increasing parameters does not guarantee intelligence

Compare conceptual sizes:

```text
10M
100M
500M
1B
3B
7B
30B
70B+
```

---

### Stage 4 — Training Dynamics

Learn what happens during a real pretraining run.

```text
Random Model
↓
Step 1
↓
Step 10
↓
Step 1,000
↓
Step 100,000
↓
Billions of Tokens
↓
Base Foundation Model
```

Study:

* Training loss
* Validation loss
* Perplexity
* Gradient norms
* Learning-rate warmup
* LR decay
* Batch size
* Gradient accumulation
* Checkpoints
* Training instability
* NaNs
* Loss spikes
* Overfitting
* Underfitting
* Data ordering
* Hardware failures
* Resume training

---

### Stage 5 — Knowledge and Generalization

Investigate the difference between:

```text
Memorization
vs
Generalization
```

Learn how models can:

* memorize sequences
* learn recurring patterns
* combine learned patterns
* represent relationships
* answer unseen combinations
* fail on unfamiliar distributions

Study probing experiments to understand what the model has actually learned.

---

### Stage 6 — Reasoning

Study reasoning separately from basic language modeling.

Topics:

* Reasoning examples in pretraining data
* Mathematical reasoning
* Code reasoning
* Multi-step reasoning
* Synthetic reasoning data
* Chain-of-thought style training concepts
* Process supervision
* Outcome supervision
* Verifiers
* Self-consistency
* Search
* Test-time compute
* Reinforcement learning for reasoning

Important question:

> What causes a model to become better at solving problems instead of merely producing fluent text?

---

### Stage 7 — Post-Training

After building a base pretrained model:

```text
Base Model
↓
Post-Training
↓
Assistant Model
```

Study:

#### Supervised Fine-Tuning — SFT

```text
Instruction
+
High-quality answer
↓
Training
```

Teach the model how to follow instructions and interact with users.

#### Preference Training

Study concepts such as:

* preference datasets
* chosen vs rejected answers
* reward modeling
* DPO
* RLHF
* RLAIF
* reinforcement learning

Understand what each technique changes and what it does **not** change.

---

### Stage 8 — Evaluation

Learn how to know whether a model is actually improving.

Evaluate separately:

```text
Language
Arabic
Saudi dialects
Knowledge
Reasoning
Mathematics
Programming
Instruction following
Safety
Long context
Hallucination
Tool use
```

Study:

* held-out validation
* benchmark datasets
* contamination
* human evaluation
* LLM-as-judge limitations
* reproducible evaluation
* regression testing

Never conclude that a model is intelligent only because training loss decreased.

---

### Stage 9 — Retrieval-Augmented Generation — RAG

Learn how a model can access information outside its weights.

```text
User Question
↓
Search / Retrieval
↓
Relevant Documents
↓
Context
↓
LLM
↓
Answer
```

Study:

* embeddings
* vector databases
* chunking
* retrieval
* reranking
* citations
* grounding
* context construction

Understand clearly:

```text
Knowledge stored in weights
≠
Knowledge retrieved at runtime
```

---

### Stage 10 — Tool Use

Teach models to interact with external systems.

Examples:

```text
Web Search
Calculator
Python
Databases
APIs
Files
Email
Code Execution
Business Systems
```

Study:

```text
User request
↓
Model reasoning
↓
Tool selection
↓
Tool arguments
↓
Tool execution
↓
Tool result
↓
Model response
```

---

### Stage 11 — Memory

Study different meanings of AI memory:

* context-window memory
* conversation history
* retrieval memory
* user-profile memory
* episodic memory
* semantic memory
* long-term external memory

Understand that model weights themselves are not automatically updated after every conversation.

---

### Stage 12 — Agents

Move from:

```text
Prompt
→ Answer
```

to:

```text
Goal
↓
Plan
↓
Act
↓
Observe
↓
Reason
↓
Use Tools
↓
Update State
↓
Repeat
↓
Finish Task
```

Study:

* planning
* task decomposition
* tool selection
* state
* memory
* retries
* verification
* permissions
* agent loops
* multi-agent systems

---

### Stage 13 — Multimodal Foundation Models

After mastering text LLMs, study:

```text
Text
Images
Audio
Video
Documents
Sensors
```

Topics:

* vision encoders
* image tokens
* multimodal embeddings
* cross-modal attention
* speech encoders
* audio generation
* vision-language models
* multimodal pretraining

---

### Stage 14 — From JSM Mini to a Real JSM Foundation Model

Use the current educational implementation as the conceptual foundation.

```text
Current JSM Mini
↓
10M–100M research models
↓
500M experiments
↓
~1B foundation model
↓
3B
↓
7B
↓
larger model family
```

For each scale, study:

* architecture configuration
* tokenizer
* dataset size
* token count
* GPU requirements
* memory
* distributed training
* training duration
* checkpoint storage
* evaluation
* inference cost

Do not scale until smaller experiments prove that:

```text
Data pipeline works
Tokenizer works
Training is stable
Loss behaves correctly
Validation improves
Generation improves
Benchmarks improve
Checkpoints recover correctly
```

---

## Main Goal of the Next Stage

The first stage answered:

> **How do I build a Transformer language model?**

The next stage must answer:

> **How does that Transformer become intelligent after training on massive amounts of high-quality data?**

Then:

> **How do we turn a pretrained base model into a useful reasoning assistant, tool-using agent, and eventually a multimodal foundation model?**

The long-term learning path is:

```text
Build the Model        ✅
↓
Understand Pretraining
↓
Engineer the Data
↓
Understand Scaling
↓
Train Base Models
↓
Evaluate Them
↓
Post-Train Them
↓
Teach Reasoning
↓
Add Tools + RAG + Memory
↓
Build Agents
↓
Build Multimodal Models
↓
Scale JSM into a Foundation-Model Family
```
