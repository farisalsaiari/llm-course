from pathlib import Path

import torch

from src.model.config import ModelConfig
from src.model.model import TinyLLM


def save_checkpoint(
    path: Path,
    model: TinyLLM,
    optimizer: torch.optim.Optimizer,
    model_config: ModelConfig,
    training_config: dict,
    training_stats: dict,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),

        "config": {
            "vocab_size": model_config.vocab_size,
            "context_length": model_config.context_length,
            "d_model": model_config.d_model,
            "num_heads": model_config.num_heads,
            "num_layers": model_config.num_layers,
            "dropout": model_config.dropout,
        },

        "training_config": training_config,
        "training_stats": training_stats,

        "model_stats": {
            "total_parameters": sum(
                parameter.numel()
                for parameter in model.parameters()
            ),
            "trainable_parameters": sum(
                parameter.numel()
                for parameter in model.parameters()
                if parameter.requires_grad
            ),
        },
    }

    epoch = training_stats["epochs_completed"]
    global_step = training_stats["global_step"]

    # --------------------------------------------------
    # Historical checkpoint
    # --------------------------------------------------

    history_path = (
        path.parent
        / (
            f"checkpoint_epoch_{epoch:06d}"
            f"_step_{global_step:09d}.pt"
        )
    )

    history_temporary_path = history_path.with_suffix(
        history_path.suffix + ".tmp"
    )

    torch.save(
        checkpoint,
        history_temporary_path,
    )

    history_temporary_path.replace(
        history_path
    )

    # --------------------------------------------------
    # Latest checkpoint
    # --------------------------------------------------

    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    torch.save(
        checkpoint,
        temporary_path,
    )

    temporary_path.replace(
        path
    )


def load_checkpoint(
    path: Path,
    device: torch.device,
) -> dict | None:
    if not path.is_file():
        return None

    return torch.load(
        path,
        map_location=device,
    )