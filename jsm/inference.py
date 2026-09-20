import json
import torch

from model import TinyModel


# -----------------------------------
# Load Vocabulary
# -----------------------------------

with open(
    "artifacts/vocabulary.json",
    "r",
    encoding="utf-8"
) as file:

    vocabulary = json.load(file)


# -----------------------------------
# Model Configuration
# -----------------------------------

context_size = 2
embedding_dim = 3


# -----------------------------------
# Create Model
# -----------------------------------

model = TinyModel(
    vocab_size=len(vocabulary),
    embedding_dim=embedding_dim,
    context_size=context_size
)


# -----------------------------------
# Load Saved Checkpoint
# -----------------------------------

checkpoint = torch.load(
    "artifacts/tiny_model.pt",
    weights_only=True
)


# -----------------------------------
# Load Token Embedding
# -----------------------------------

model.embedding.load_state_dict(
    checkpoint["embedding"]
)


# -----------------------------------
# Load Position Embedding
# -----------------------------------

model.position_embedding.load_state_dict(
    checkpoint["position_embedding"]
)


# -----------------------------------
# Load Self-Attention
# -----------------------------------

model.attention.load_state_dict(
    checkpoint["attention"]
)


# -----------------------------------
# Load Output Layer
# -----------------------------------

model.output_layer.load_state_dict(
    checkpoint["output_layer"]
)


# -----------------------------------
# Evaluation Mode
# -----------------------------------

model.eval()


# -----------------------------------
# Input Context
# -----------------------------------

input_words = [
    "i",
    "love"
]


# -----------------------------------
# Words → Token IDs
# -----------------------------------

input_ids = [
    vocabulary[word]
    for word in input_words
]


input_tensor = torch.tensor(
    input_ids
)


# -----------------------------------
# Run Model
# -----------------------------------

with torch.no_grad():

    logits = model(
        input_tensor
    )


    probabilities = torch.softmax(
        logits,
        dim=0
    )


# -----------------------------------
# Show Prediction
# -----------------------------------

print(
    "Input:",
    input_words
)

print()

print(
    "Predictions:"
)


for word, probability in zip(
    vocabulary.keys(),
    probabilities
):

    print(
        word,
        "→",
        round(
            probability.item() * 100,
            2
        ),
        "%"
    )