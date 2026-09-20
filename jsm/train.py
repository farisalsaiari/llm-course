import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from checkpoint import restore_training_state, save_training_checkpoint
from config import ModelConfig
from data_loader import documents, split_documents
from dataset import LanguageModelDataset
from device import get_device
from metrics import perplexity
from model import TinyModel
from paths import CHECKPOINT_PATH, TOKENIZER_PATH
from precision import autocast_context
from subword_tokenizer import (
    encode_documents,
    load_or_train_tokenizer
)
from training_utils import cosine_warmup_multiplier
from utils import count_parameters, parameter_breakdown


# -----------------------------------
# Keep random initialization
# the same every run
# -----------------------------------

torch.manual_seed(42)

parser = argparse.ArgumentParser()
parser.add_argument("--resume", action="store_true")
parser.add_argument("--epochs", type=int, default=50)
parser.add_argument(
    "--precision",
    choices=("fp32", "fp16", "bf16"),
    default="fp32"
)
args = parser.parse_args()
device = get_device()

print("Device:", device)


# -----------------------------------
# Maximum Sequence Length
# -----------------------------------

max_seq_len = 16
sequence_length = 16
batch_size = 2


# -----------------------------------
# Train/Load Local Byte-Level BPE
# -----------------------------------

tokenizer = load_or_train_tokenizer()
encoded_documents = encode_documents(
    tokenizer,
    documents
)
training_documents, validation_documents = split_documents(
    encoded_documents,
    validation_fraction=0.2,
    seed=42
)
vocab_size = tokenizer.get_vocab_size()


# -----------------------------------
# Create Dataset and DataLoader
# -----------------------------------

training_dataset = LanguageModelDataset(
    encoded_documents=training_documents,
    sequence_length=sequence_length,
    stride=1
)

training_loader = DataLoader(
    training_dataset,
    batch_size=batch_size,
    shuffle=True
)

validation_dataset = LanguageModelDataset(
    encoded_documents=validation_documents,
    sequence_length=sequence_length,
    stride=1
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size=batch_size,
    shuffle=False
)

first_input_batch, first_target_batch = next(iter(training_loader))

print("Training windows:", len(training_dataset))
print("Validation windows:", len(validation_dataset))
print("Input batch shape:", first_input_batch.shape)
print("Target batch shape:", first_target_batch.shape)


# -----------------------------------
# Create Model
# -----------------------------------

model_config = ModelConfig(
    vocab_size=vocab_size,
    max_seq_len=max_seq_len,
    embedding_dim=32,
    num_heads=4,
    num_layers=2,
    ffn_multiplier=4
)

model = TinyModel(model_config).to(device)
model.train()

total_parameters, trainable_parameters = count_parameters(model)

print("Parameter breakdown:", parameter_breakdown(model))
print("Total parameters:", total_parameters)
print("Trainable parameters:", trainable_parameters)


# -----------------------------------
# Loss Function
# -----------------------------------

loss_function = nn.CrossEntropyLoss()


# -----------------------------------
# Optimizer
# -----------------------------------

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=3e-3,
    betas=(0.9, 0.95),
    weight_decay=0.01
)

epochs = args.epochs
total_steps = epochs * len(training_loader)
warmup_steps = min(5, total_steps - 1)
max_grad_norm = 1.0

scheduler = torch.optim.lr_scheduler.LambdaLR(
    optimizer,
    lr_lambda=lambda step: cosine_warmup_multiplier(
        step=step,
        warmup_steps=warmup_steps,
        total_steps=total_steps,
        minimum_multiplier=0.1
    )
)

start_epoch = 0
global_step = 0

if args.resume:
    resume_checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location=device,
        weights_only=True
    )

    if resume_checkpoint["config"] != model_config.__dict__:
        raise ValueError(
            "Checkpoint model config does not match training config."
        )

    start_epoch, global_step = restore_training_state(
        checkpoint=resume_checkpoint,
        model=model,
        optimizer=optimizer,
        scheduler=scheduler
    )

    print("Resuming from epoch:", start_epoch)
    print("Resuming from global step:", global_step)


# -----------------------------------
# Training
# -----------------------------------

for epoch in range(start_epoch, epochs):

    total_loss = 0

    model.train()

    for input_batch, target_batch in training_loader:

        input_batch = input_batch.to(device)
        target_batch = target_batch.to(device)

        with autocast_context(device, args.precision):
            logits = model(input_batch)

            loss = loss_function(
                logits.reshape(-1, logits.shape[-1]),
                target_batch.reshape(-1)
            )

        optimizer.zero_grad()

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=max_grad_norm
        )

        optimizer.step()

        scheduler.step()
        global_step += 1

        total_loss += loss.item()


    if epoch % 5 == 0 or epoch == epochs - 1:
        model.eval()
        validation_loss = 0

        with torch.no_grad():
            for input_batch, target_batch in validation_loader:
                input_batch = input_batch.to(device)
                target_batch = target_batch.to(device)
                logits = model(input_batch)
                loss = loss_function(
                    logits.reshape(-1, logits.shape[-1]),
                    target_batch.reshape(-1)
                )
                validation_loss += loss.item()

        mean_validation_loss = validation_loss / len(validation_loader)

        print(
            "Epoch:",
            epoch,
            "Train Loss:",
            total_loss / len(training_loader),
            "Validation Loss:",
            mean_validation_loss,
            "Validation Perplexity:",
            perplexity(mean_validation_loss),
            "LR:",
            scheduler.get_last_lr()[0]
        )


# -----------------------------------
# Test After Training
# -----------------------------------

test_contexts = [
    "i love",
    "i drink"
]


model.eval()


with torch.no_grad():

    for context_text in test_contexts:

        context_ids = tokenizer.encode(
            context_text
        ).ids


        # IDs → Tensor
        input_tensor = torch.tensor(
            context_ids,
            device=device
        )


        # Model → Per-Token Logits
        logits = model(
            input_tensor
        )


        # Use the final position to predict the next token
        next_token_logits = logits[-1]


        # Logits → Probabilities
        probabilities = torch.softmax(
            next_token_logits,
            dim=0
        )


        print(
            "\nPrediction for:",
            context_text
        )

        top_probabilities, top_ids = torch.topk(
            probabilities,
            k=min(5, vocab_size)
        )

        for token_id, probability in zip(
            top_ids.tolist(),
            top_probabilities.tolist()
        ):

            print(
                repr(tokenizer.id_to_token(token_id)),
                "→",
                round(
                    probability * 100,
                    2
                ),
                "%"
            )


# -----------------------------------
# Save Training Checkpoint
# -----------------------------------

save_training_checkpoint(
    path=CHECKPOINT_PATH,
    model=model,
    optimizer=optimizer,
    scheduler=scheduler,
    epoch=epochs - 1,
    global_step=global_step
)

print(
    "\nModel saved to",
    CHECKPOINT_PATH
)

print(
    "Tokenizer saved to",
    TOKENIZER_PATH
)
