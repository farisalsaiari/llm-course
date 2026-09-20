# Tokenizer

A character tokenizer is simple but creates long sequences. A word tokenizer creates short sequences but cannot naturally represent unseen words. Subword tokenizers learn reusable pieces between those extremes.

This project uses a Byte-Level BPE tokenizer implemented from scratch in pure Python and trained only on `jsm/data/raw/*.txt`. It does not use Hugging Face, SentencePiece, or another tokenizer library. BPE repeatedly counts adjacent byte-symbol pairs, merges the most frequent pair deterministically, and repeats until reaching the configured vocabulary size or exhausting available pairs. Byte-level input guarantees coverage for arbitrary UTF-8 text without downloading another model's vocabulary.

Special tokens:

- `<BOS>` marks a document start.
- `<EOS>` marks a document end and prevents document boundaries from being ambiguous.
- `<PAD>` is reserved for batches that later need padding; fixed-size training windows do not use it.
- `<UNK>` is configured for completeness, although byte-level coverage should make it rare.

Artifacts are saved independently at `jsm/artifacts/tokenizer/tokenizer.json`. Token IDs index embeddings, but tokenization and embedding are separate operations: the tokenizer maps text to discrete IDs, while the embedding table maps each ID to a learned vector.

The JSON artifact stores special tokens and learned merge pairs as hexadecimal byte sequences. Encoding begins with individual UTF-8 bytes and applies learned merges in training order. Decoding concatenates token bytes and converts them back to UTF-8 text.
