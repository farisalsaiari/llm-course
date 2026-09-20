import torch

from tokenizer import vocabulary
from embedding import embedding


# -----------------------------------
# Context
# -----------------------------------

context = [
    "i",
    "love"
]


# -----------------------------------
# Words → Token IDs
# -----------------------------------

context_ids = [
    vocabulary[word]
    for word in context
]


# -----------------------------------
# Token IDs → Tensor
# -----------------------------------

context_tensor = torch.tensor(
    context_ids
)


# -----------------------------------
# Token IDs → Embedding vectors
# -----------------------------------

context_vectors = embedding(
    context_tensor
)


# -----------------------------------
# Temporary attention weights
# We choose them manually for learning
#
# i    → 20%
# love → 80%
# -----------------------------------

attention_weights = torch.tensor(
    [0.2, 0.8]
)


# -----------------------------------
# Apply attention weights
# to each token vector
# -----------------------------------



# -----------------------------------
# Apply attention weights
# to each token vector
# -----------------------------------

weighted_vectors = (
    context_vectors *
    attention_weights.unsqueeze(1)
)


# -----------------------------------
# Combine weighted vectors
# into one attention output
# -----------------------------------

attention_output = weighted_vectors.sum(dim=0)


# -----------------------------------
# Print results
# -----------------------------------

print("Context:")
print(context)

print()

print("Context IDs:")
print(context_ids)

print()

print("Context vectors:")
print(context_vectors)

print()

print("Attention weights:")
print(attention_weights)

print()

print("Weighted vectors:")
print(weighted_vectors)

print()

print("Attention output:")
print(attention_output)