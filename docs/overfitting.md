# Memorization Versus Generalization

Predicting `coffee` with 99% confidence after seeing only `i love coffee` and `i drink coffee` demonstrates fitting a tiny distribution. It does not demonstrate broad language understanding.

`lessons/overfitting_demo.py` trains on one token pattern and evaluates a disjoint pattern. Training loss can approach zero while validation remains poor or worsens. The gap is overfitting: parameters store training-specific associations that do not transfer.

Generalization requires representative held-out data, adequate diversity, suitable capacity/regularization, and evaluation that the model could not solve by memorizing duplicates.
