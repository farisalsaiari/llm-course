# Local Mini Corpus

The corpus contains eight separate local documents: the two original coffee examples plus six original short texts about learning, software, language models, science, daily routine, and computer systems. It is large enough to exercise BPE merges, 16-token windows, batching, validation, and generation without downloading external data.

Document files remain separate so training windows never create transitions between unrelated endings and beginnings. Run `python3 train_tokenizer.py` after changing corpus text, then train a fresh model because changing tokenizer IDs invalidates old embedding/checkpoint semantics.

This is still a miniature teaching corpus, not enough data for broad language capability. Its purpose is pipeline correctness and observable overfitting/generalization behavior on local hardware.
