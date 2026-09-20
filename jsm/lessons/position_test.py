import torch
import torch.nn as nn

from tokenizer import vocabulary
from embedding import embedding


# -----------------------------------
# Create Position Embedding
# -----------------------------------

position_embedding = nn.Embedding(
    num_embeddings=2,
    embedding_dim=3
)


# -----------------------------------
# Output Layer
# 6 context values → vocabulary logits
# -----------------------------------

output_layer = nn.Linear(
    6,
    len(vocabulary)
)


# -----------------------------------
# Test two contexts with reversed order
# -----------------------------------

contexts = [
    ["i", "love"],
    ["love", "i"]
]


for context in contexts:

    # Words → Token IDs
    context_ids = [
        vocabulary[word]
        for word in context
    ]


    # Token IDs → Tensor
    context_tensor = torch.tensor(
        context_ids
    )


    # Token IDs → Embedding vectors
    context_vectors = embedding(
        context_tensor
    )


    # Positions: 0, 1
    positions = torch.tensor(
        [0, 1]
    )


    # Position IDs → Position vectors
    position_vectors = position_embedding(
        positions
    )


    # Token Embedding + Position Embedding
    context_vectors = (
        context_vectors + position_vectors
    )


    print("Vectors with position:")
    print(context_vectors)


    # Keep order by joining the vectors
    # 2 tokens × 3 values = 6 values
    context_vector = context_vectors.flatten()


    # Ordered context vector → Logits
    logits = output_layer(
        context_vector
    )


    print("Context:", context)

    print("Combined vector:")
    print(context_vector)

    print("Logits:")
    print(logits)

    print()