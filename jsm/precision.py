from contextlib import nullcontext

import torch


def autocast_context(device, precision):

    if precision == "fp32":
        return nullcontext()

    if device.type != "cuda":
        raise ValueError(
            f"{precision} training is only enabled for CUDA in this project."
        )

    dtype = {
        "fp16": torch.float16,
        "bf16": torch.bfloat16
    }.get(precision)

    if dtype is None:
        raise ValueError("precision must be fp32, fp16, or bf16.")

    if precision == "bf16" and not torch.cuda.is_bf16_supported():
        raise ValueError("BF16 is not supported by this CUDA device.")

    return torch.autocast(device_type="cuda", dtype=dtype)
