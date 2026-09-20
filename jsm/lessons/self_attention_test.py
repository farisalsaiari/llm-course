import torch

from tokenizer import vocabulary
from embedding import embedding
from lessons.self_attention import SelfAttention


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
# Create Self-Attention
# -----------------------------------

attention = SelfAttention(
    embedding_dim=3
)


# -----------------------------------
# Run Self-Attention
# -----------------------------------

attention_output = attention(
    vectors
)


# -----------------------------------
# Show Results
# -----------------------------------

print("Original vectors:")
print(vectors)

print()

print("Attention Output:")
print(attention_output)