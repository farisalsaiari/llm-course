import torch

from feed_forward import FeedForward


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
# Create Feed-Forward Network
# -----------------------------------

ffn = FeedForward(
    embedding_dim=3
)


# -----------------------------------
# Run Feed-Forward Network
# -----------------------------------

output = ffn(
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

print("FFN output:")
print(output)

print()

print("Output shape:")
print(output.shape)
