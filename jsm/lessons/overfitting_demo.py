import torch
import torch.nn as nn

from config import ModelConfig
from model import TinyModel


def sequence_loss(model, inputs, targets, loss_function):

    logits = model(inputs)

    return loss_function(
        logits.reshape(-1, logits.shape[-1]),
        targets.reshape(-1)
    )


def run_demo(epochs=120):

    torch.manual_seed(42)
    model = TinyModel(ModelConfig(
        vocab_size=32,
        max_seq_len=4,
        embedding_dim=16,
        num_heads=4,
        num_layers=1
    ))
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.02)
    loss_function = nn.CrossEntropyLoss()

    training_inputs = torch.tensor([[4, 5, 6, 7]])
    training_targets = torch.tensor([[5, 6, 7, 8]])
    validation_inputs = torch.tensor([[20, 21, 22, 23]])
    validation_targets = torch.tensor([[21, 22, 23, 24]])

    with torch.no_grad():
        initial_training_loss = sequence_loss(
            model, training_inputs, training_targets, loss_function
        ).item()
        initial_validation_loss = sequence_loss(
            model, validation_inputs, validation_targets, loss_function
        ).item()

    model.train()

    for _ in range(epochs):
        loss = sequence_loss(
            model, training_inputs, training_targets, loss_function
        )
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    model.eval()

    with torch.no_grad():
        final_training_loss = sequence_loss(
            model, training_inputs, training_targets, loss_function
        ).item()
        final_validation_loss = sequence_loss(
            model, validation_inputs, validation_targets, loss_function
        ).item()

    return {
        "initial_training_loss": initial_training_loss,
        "final_training_loss": final_training_loss,
        "initial_validation_loss": initial_validation_loss,
        "final_validation_loss": final_validation_loss
    }


if __name__ == "__main__":
    results = run_demo()
    print(results)
    print(
        "The model memorized its training sequence; "
        "that does not imply held-out generalization."
    )
