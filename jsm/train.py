import json
import torch
import torch.nn as nn

from tokenizer import vocabulary, tokenized_documents
from model import TinyModel


# -----------------------------------
# Keep random initialization
# the same every run
# -----------------------------------

torch.manual_seed(42)


# -----------------------------------
# Context size
# -----------------------------------

context_size = 2


# -----------------------------------
# Create Training Pairs
#
# Example:
#
# i love coffee
#
# ["i", "love"] → "coffee"
# -----------------------------------

training_pairs = []

for document_words in tokenized_documents:

    for i in range(
        len(document_words) - context_size
    ):

        context_words = document_words[
            i:i + context_size
        ]

        target_word = document_words[
            i + context_size
        ]

        training_pairs.append(
            (
                context_words,
                target_word
            )
        )


print("Training pairs:")
print(training_pairs)


# -----------------------------------
# Create Model
# -----------------------------------

model = TinyModel(
    vocab_size=len(vocabulary),
    embedding_dim=3,
    context_size=context_size
)


# -----------------------------------
# Loss Function
# -----------------------------------

loss_function = nn.CrossEntropyLoss()


# -----------------------------------
# Optimizer
# -----------------------------------

optimizer = torch.optim.SGD(
    model.parameters(),
    lr=0.1
)


# -----------------------------------
# Training
# -----------------------------------

for epoch in range(50):

    total_loss = 0


    for context_words, target_word in training_pairs:

        # -----------------------------------
        # Context Words → Token IDs
        #
        # ["i", "love"]
        # ↓
        # [0, 3]
        # -----------------------------------

        context_ids = [
            vocabulary[word]
            for word in context_words
        ]


        # Target Word → Token ID
        target_id = vocabulary[
            target_word
        ]


        # -----------------------------------
        # IDs → Tensors
        # -----------------------------------

        input_tensor = torch.tensor(
            context_ids
        )

        target_tensor = torch.tensor(
            [target_id]
        )


        # -----------------------------------
        # Forward Pass
        #
        # Context IDs
        # ↓
        # Token Embeddings
        # ↓
        # Position Embeddings
        # ↓
        # Ordered Context
        # ↓
        # Output Layer
        # ↓
        # Logits
        # -----------------------------------

        logits = model(
            input_tensor
        )


        # -----------------------------------
        # Calculate Loss
        # -----------------------------------

        loss = loss_function(
            logits.unsqueeze(0),
            target_tensor
        )


        # -----------------------------------
        # Clear old gradients
        # -----------------------------------

        optimizer.zero_grad()


        # -----------------------------------
        # Backpropagation
        # -----------------------------------

        loss.backward()


        # -----------------------------------
        # Update weights
        # -----------------------------------

        optimizer.step()


        total_loss += loss.item()


    print(
        "Epoch:",
        epoch,
        "Loss:",
        total_loss
    )


# -----------------------------------
# Test After Training
# -----------------------------------

test_contexts = [
    ["i", "love"],
    ["i", "drink"]
]


model.eval()


with torch.no_grad():

    for context_words in test_contexts:

        # Context Words → IDs
        context_ids = [
            vocabulary[word]
            for word in context_words
        ]


        # IDs → Tensor
        input_tensor = torch.tensor(
            context_ids
        )


        # Model → Logits
        logits = model(
            input_tensor
        )


        # Logits → Probabilities
        probabilities = torch.softmax(
            logits,
            dim=0
        )


        print(
            "\nPrediction for:",
            context_words
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


# -----------------------------------
# Save Model Weights
# -----------------------------------

torch.save(
    {
        "embedding":
            model.embedding.state_dict(),

        "position_embedding":
            model.position_embedding.state_dict(),

        "attention":
            model.attention.state_dict(),

        "output_layer":
            model.output_layer.state_dict()
    },

    "artifacts/tiny_model.pt"
)


# -----------------------------------
# Save Vocabulary
# -----------------------------------

with open(
    "artifacts/vocabulary.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        vocabulary,
        file,
        ensure_ascii=False,
        indent=4
    )


print(
    "\nModel saved to "
    "artifacts/tiny_model.pt"
)

print(
    "Vocabulary saved to "
    "artifacts/vocabulary.json"
)