import math


def cosine_warmup_multiplier(
    step,
    warmup_steps,
    total_steps,
    minimum_multiplier=0.1
):

    if total_steps < 1:
        raise ValueError("total_steps must be positive.")

    if not 0 <= warmup_steps < total_steps:
        raise ValueError(
            "warmup_steps must be in [0, total_steps)."
        )

    if not 0 <= minimum_multiplier <= 1:
        raise ValueError(
            "minimum_multiplier must be in [0, 1]."
        )

    if warmup_steps and step < warmup_steps:
        return (step + 1) / warmup_steps

    decay_steps = max(total_steps - warmup_steps - 1, 1)
    progress = min(
        max((step - warmup_steps) / decay_steps, 0.0),
        1.0
    )
    cosine = 0.5 * (1 + math.cos(math.pi * progress))

    return minimum_multiplier + (
        1 - minimum_multiplier
    ) * cosine
