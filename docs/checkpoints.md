# Checkpoints

A weights-only checkpoint is enough for inference but cannot reproduce optimizer momentum, scheduler position, or training progress. A training-resume checkpoint needs all of those states.

`artifacts/tiny_model.pt` now contains `model_state_dict`, `optimizer_state_dict`, `scheduler_state_dict`, `epoch`, `global_step`, and `config`.

The tokenizer remains a separate artifact because it defines the text/ID contract and may be inspected or reused independently. Inference rebuilds the model from checkpoint configuration and loads the complete model state. Training can continue with:

```bash
python3 train.py --resume --epochs <new-total>
```

Resume assumes the same tokenizer and architecture. Dataset shuffle state is not stored yet, so this is a practical resume path rather than bit-for-bit replay.
