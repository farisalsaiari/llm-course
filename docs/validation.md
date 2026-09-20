# Training And Validation

Training data updates parameters. Validation data never calls backward or optimizer step; it estimates behavior on held-out examples. A falling training loss with rising validation loss is a classic overfitting signal.

The split is deterministic and document-level. Splitting documents before creating windows prevents nearly identical overlapping windows from leaking between sets and preserves semantic boundaries. The current two-document corpus leaves only one document per set, so its validation number is highly noisy and is educational rather than statistically meaningful.

Perplexity is `exp(mean cross-entropy loss)`. Informally, lower values mean the model assigns more probability to held-out next tokens. It is only comparable when tokenization, data, and loss averaging are comparable; changing the tokenizer changes the prediction units. Tiny validation sets and domain mismatch can also make it misleading.
