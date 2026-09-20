import torch

from transformer_block import TransformerBlock


# -----------------------------------
# Example Token Vectors
#
# 2 tokens
# each token has 3 values
# -----------------------------------

vectors = torch.tensor([
    [0.2, 0.5, -0.1],
    [0.8, -0.3, 0.4]
])


# -----------------------------------
# Create Transformer Block
# -----------------------------------

block = TransformerBlock(
    embedding_dim=3
)


# -----------------------------------
# Run Transformer Block
# -----------------------------------

output = block(
    vectors
)


# -----------------------------------
# Show Results
# -----------------------------------

print("Input vectors:")
print(vectors)

print()

print("Input shape:")
print(vectors.shape)

print()

print("Transformer Block output:")
print(output)

print()

print("Output shape:")
print(output.shape)