import torch
import torch.nn as nn
import json

from tokenizer import vocabulary, tokenized_documents
from embedding import embedding


# -----------------------------------
# Create training pairs
# -----------------------------------

training_pairs = []

for document_words in tokenized_documents:

    for i in range(len(document_words) - 1):

        input_word = document_words[i]
        target_word = document_words[i + 1]

        training_pairs.append(
            (input_word, target_word)
        )


print("Training pairs:")
print(training_pairs)


# -----------------------------------
# Embedding → Logits
# -----------------------------------

output_layer = nn.Linear(
    3,
    len(vocabulary)
)


# -----------------------------------
# Loss function
# -----------------------------------

loss_function = nn.CrossEntropyLoss()


# -----------------------------------
# Optimizer
# Updates embedding + output layer
# -----------------------------------

optimizer = torch.optim.SGD(
    list(embedding.parameters()) +
    list(output_layer.parameters()),
    lr=0.1
)


# -----------------------------------
# Training
# -----------------------------------

for epoch in range(50):

    total_loss = 0

    for input_word, target_word in training_pairs:

        # Words → IDs
        input_id = vocabulary[input_word]
        target_id = vocabulary[target_word]

        # IDs → Tensors
        input_tensor = torch.tensor(input_id)
        target_tensor = torch.tensor([target_id])

        # Token ID → Embedding
        input_vector = embedding(input_tensor)

        # Embedding → Logits
        logits = output_layer(input_vector)

        # Calculate loss
        loss = loss_function(
            logits.unsqueeze(0),
            target_tensor
        )

        # Clear old gradients
        optimizer.zero_grad()

        # Backpropagation
        loss.backward()

        # Update weights
        optimizer.step()

        total_loss += loss.item()

    print(
        "Epoch:", epoch,
        "Loss:", total_loss
    )




# -----------------------------------
# Test after training
# -----------------------------------

# -----------------------------------
# Test after training
# -----------------------------------

test_words = [
    "i",
    "drink",
    "love"
]


for test_word in test_words:

    test_id = vocabulary[test_word]

    test_tensor = torch.tensor(test_id)

    # Token ID → Embedding
    test_vector = embedding(test_tensor)

    # Embedding → Logits
    logits = output_layer(test_vector)

    # Logits → Probabilities
    probabilities = torch.softmax(logits, dim=0)


    print("\nPrediction for:", test_word)

    for word, probability in zip(
        vocabulary.keys(),
        probabilities
    ):
        print(
            word,
            "→",
            round(probability.item() * 100, 2),
            "%"
        )

test_id = vocabulary[test_word]

test_tensor = torch.tensor(test_id)

# Token ID → Embedding
test_vector = embedding(test_tensor)

# Embedding → Logits
logits = output_layer(test_vector)

# Logits → Probabilities
probabilities = torch.softmax(logits, dim=0)


print("\nPrediction for:", test_word)

for word, probability in zip(vocabulary.keys(), probabilities):
    print(
        word,
        "→",
        round(probability.item() * 100, 2),
        "%"
    )


    # Save trained weights
# Save trained model weights
torch.save(
    {
        "embedding": embedding.state_dict(),
        "output_layer": output_layer.state_dict()
    },
    "artifacts/tiny_model.pt"
)


# Save vocabulary used during training
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


print("\nModel saved to artifacts/tiny_model.pt")
print("Vocabulary saved to artifacts/vocabulary.json")