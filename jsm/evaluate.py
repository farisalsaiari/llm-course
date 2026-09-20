import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from checkpoint import load_model_checkpoint
from data_loader import documents, split_documents
from dataset import LanguageModelDataset
from device import get_device
from generation import generate
from metrics import perplexity
from model import TinyModel
from paths import CHECKPOINT_PATH
from subword_tokenizer import encode_documents, load_tokenizer


def evaluate_loader(model, dataloader, device):

    loss_function = nn.CrossEntropyLoss(reduction="sum")
    total_loss = 0
    total_correct = 0
    total_tokens = 0
    model.eval()

    with torch.no_grad():
        for input_ids, target_ids in dataloader:
            input_ids = input_ids.to(device)
            target_ids = target_ids.to(device)
            logits = model(input_ids)
            flat_logits = logits.reshape(-1, logits.shape[-1])
            flat_targets = target_ids.reshape(-1)
            total_loss += loss_function(
                flat_logits,
                flat_targets
            ).item()
            total_correct += (
                flat_logits.argmax(dim=-1) == flat_targets
            ).sum().item()
            total_tokens += flat_targets.numel()

    mean_loss = total_loss / total_tokens

    return {
        "loss": mean_loss,
        "perplexity": perplexity(mean_loss),
        "next_token_accuracy": total_correct / total_tokens,
        "tokens": total_tokens
    }


def main():

    device = get_device()
    tokenizer = load_tokenizer()
    model, _ = load_model_checkpoint(
        CHECKPOINT_PATH,
        TinyModel,
        map_location=device
    )
    model = model.to(device)

    encoded = encode_documents(tokenizer, documents)
    _, validation_documents = split_documents(encoded, 0.2, 42)
    dataset = LanguageModelDataset(
        validation_documents,
        sequence_length=16,
        stride=1
    )
    dataloader = DataLoader(dataset, batch_size=2, shuffle=False)
    metrics = evaluate_loader(model, dataloader, device)

    print("Device:", device)
    print("Validation metrics:", metrics)
    print("Generation samples:")

    for prompt in ("i love", "i drink"):
        print(
            repr(prompt),
            "->",
            repr(generate(
                model,
                tokenizer,
                prompt,
                max_new_tokens=8,
                temperature=0
            ))
        )

    print("Warning: tiny-corpus metrics measure memorization, not intelligence.")


if __name__ == "__main__":
    main()
