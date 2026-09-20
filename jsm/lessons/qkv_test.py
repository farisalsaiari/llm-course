import torch
import torch.nn as nn

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


context_tensor = torch.tensor(
    context_ids
)


# -----------------------------------
# Token IDs → Embeddings
# -----------------------------------

vectors = embedding(
    context_tensor
)


# -----------------------------------
# Create Q, K, V layers
# -----------------------------------

query_layer = nn.Linear(
    3,
    3,
    bias=False
)

key_layer = nn.Linear(
    3,
    3,
    bias=False
)

value_layer = nn.Linear(
    3,
    3,
    bias=False
)


# -----------------------------------
# Embeddings → Q, K, V
# -----------------------------------

Q = query_layer(vectors)

K = key_layer(vectors)

V = value_layer(vectors)


# -----------------------------------
# Q × Kᵀ
# Then divide by √d_k
# -----------------------------------

d_k = K.shape[-1]

attention_scores = (
    Q @ K.T
) / (d_k ** 0.5)


# -----------------------------------
# Create Causal Mask
# -----------------------------------

mask = torch.triu(
    torch.ones_like(attention_scores),
    diagonal=1
).bool()


# -----------------------------------
# Block Future Tokens
# -----------------------------------

attention_scores = attention_scores.masked_fill(
    mask,
    float("-inf")
)


# -----------------------------------
# Masked Scores → Attention Weights
# -----------------------------------

attention_weights = torch.softmax(
    attention_scores,
    dim=-1
)


# -----------------------------------
# Attention Weights × Values
# → Attention Output
# -----------------------------------

attention_output = (
    attention_weights @ V
)


# -----------------------------------
# Show results
# -----------------------------------

print("Original vectors:")
print(vectors)

print()

print("Query Q:")
print(Q)

print()

print("Key K:")
print(K)

print()

print("Value V:")
print(V)

print()

print("d_k:")
print(d_k)

print()

print("Causal Mask:")
print(mask)

print()

print("Masked Attention Scores:")
print(attention_scores)

print()

print("Attention Weights:")
print(attention_weights)

print()

print("Attention Output:")
print(attention_output)