from dataclasses import asdict

import torch

from config import ModelConfig


def save_training_checkpoint(
    path,
    model,
    optimizer,
    scheduler,
    epoch,
    global_step
):

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "epoch": epoch,
            "global_step": global_step,
            "config": asdict(model.config)
        },
        path
    )


def load_model_checkpoint(path, model_class, map_location="cpu"):

    checkpoint = torch.load(
        path,
        map_location=map_location,
        weights_only=True
    )
    config = ModelConfig(**checkpoint["config"])
    model = model_class(config)
    model.load_state_dict(checkpoint["model_state_dict"])

    return model, checkpoint


def restore_training_state(
    checkpoint,
    model,
    optimizer,
    scheduler
):

    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    return checkpoint["epoch"] + 1, checkpoint["global_step"]
