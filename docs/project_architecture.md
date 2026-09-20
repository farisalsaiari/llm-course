# Project Architecture

Production modules remain flat under `jsm/` so each mechanism is easy to open while learning. Entry points are `train.py`, `inference.py`, `evaluate.py`, and `train_tokenizer.py`. Model components, data/tokenizer utilities, generation, metrics, device/precision, checkpoints, and scale estimators each have one focused module.

`lessons/` owns historical experiments and is not imported by production code. `data/raw/` owns source documents. `artifacts/` contains reproducible generated outputs and may be replaced by retraining. `paths.py` centralizes production filesystem locations.

A deeper package hierarchy would add import ceremony without solving current complexity. Refactor again only when module name collisions, multiple model families, or reusable packaging create a concrete need.
