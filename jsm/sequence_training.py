import torch
import torch.nn as nn

from tokenizer import vocabulary
from embedding import embedding


# Tiny training dataset
training_pairs = [
    ("i", "love"),
    ("love", "coffee"),
]


# Embedding vector → Logits
output_layer = nn.Linear(
    3,
    len(vocabulary)
)

# Loss function
loss_function = nn.CrossEntropyLoss()

# Convert words to token IDs
for input_word, target_word in training_pairs:

    input_id = vocabulary[input_word]
    target_id = vocabulary[target_word]

    input_tensor = torch.tensor(input_id)

    # Token ID → Embedding vector
    input_vector = embedding(input_tensor)

    # Embedding vector → Logits
    logits = output_layer(input_vector)

    target_tensor = torch.tensor(target_id)

    # Compare prediction with correct target
    loss = loss_function(
        logits.unsqueeze(0),
        target_tensor.unsqueeze(0)
    )

    print("Loss:", loss.item())

    print("Input vector:", input_vector)
    print("Logits:", logits)

    print("Input tensor:", input_tensor)
    print("Target tensor:", target_tensor)

    print(input_word, "→", input_id)
    print(target_word, "→", target_id)
    print()