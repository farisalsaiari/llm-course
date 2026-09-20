import torch
import torch.nn as nn

from tokenizer import tokenized_documents, vocabulary
from embedding import embedding


# -----------------------------------
# Create context training pairs
# -----------------------------------

context_pairs = []

for document in tokenized_documents:

    if len(document) >= 3:

        context = document[:2]
        target = document[2]

        context_pairs.append(
            (context, target)
        )


print("Context pairs:")
print(context_pairs)
print()


# -----------------------------------
# Context vector → Logits
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

for epoch in range(5):

    total_loss = 0

    for context, target in context_pairs:

        # Context words → Token IDs
        context_ids = [
            vocabulary[word]
            for word in context
        ]


        # Correct next word → Token ID
        target_id = vocabulary[target]


        # Context IDs → Tensor
        context_tensor = torch.tensor(
            context_ids
        )


        # Token IDs → Embedding vectors
        context_vectors = embedding(
            context_tensor
        )


        # Combine context vectors
        # into one context vector
        context_vector = context_vectors.mean(
            dim=0
        )


        # Context vector → Logits
        logits = output_layer(
            context_vector
        )


        # Target ID → Tensor
        target_tensor = torch.tensor(
            [target_id]
        )


        # Calculate Loss
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


        # Add this example's loss
        total_loss += loss.item()


    print(
        "Epoch:", epoch,
        "Loss:", total_loss
    )





# -----------------------------------
# Test after training
# -----------------------------------

test_contexts = [
    ["i", "love"],
    ["i", "drink"]
]


for context in test_contexts:

    # Words → Token IDs
    context_ids = [
        vocabulary[word]
        for word in context
    ]

    # IDs → Tensor
    context_tensor = torch.tensor(context_ids)

    # IDs → Embeddings
    context_vectors = embedding(context_tensor)

    # Combine context
    context_vector = context_vectors.mean(dim=0)

    # Context → Logits
    logits = output_layer(context_vector)

    # Logits → Probabilities
    probabilities = torch.softmax(logits, dim=0)

    print("\nContext:", context)

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