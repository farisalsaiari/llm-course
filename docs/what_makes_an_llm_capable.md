# What Makes An LLM Capable?

There is no single intelligence component. Capability emerges from interacting systems:

## Architecture

Attention moves information between positions; FFNs transform representations; residual paths and normalization make optimization practical. Architecture supplies useful computation, but untrained layers contain no language knowledge.

## Data Quality And Diversity

Training text supplies patterns, facts, styles, and tasks. Duplicate, noisy, biased, or narrow data teaches those properties. Filtering and document boundaries matter as much as raw volume.

## Tokenization

Tokens define the units the model predicts. Vocabulary design changes sequence length, multilingual coverage, code handling, and the meaning of loss/perplexity.

## Capacity And Compute

Parameters provide capacity to store and combine patterns. Training compute is needed to fit them. Too little capacity underfits; more capacity without enough diverse data/optimization can memorize or waste compute.

## Optimization

Initialization, batches, AdamW, learning-rate schedules, precision, clipping, and distributed systems determine whether useful parameters are actually learned. A theoretically good architecture can fail under unstable training.

## Context

Context lets inference condition on recent tokens. Longer context does not add knowledge by itself, and models must be trained to use long positions effectively.

## Post-Training

Instruction tuning, preference optimization, tool-use training, and safety work shape how a pretrained model follows requests. They do not replace broad pretraining knowledge.

## Evaluation

Validation loss, perplexity, task accuracy, generation review, robustness, bias, and safety tests measure different properties. Training loss alone mostly measures fit to seen data.

Adding Transformer layers only increases potential capacity and compute cost. It does not guarantee better data, stable optimization, generalization, reasoning, factuality, or alignment. The original two-sentence model predicted coffee confidently because it memorized a tiny distribution, not because it understood coffee or language.
