import torch

from embedding import embedding, vocabulary


# Get "love" ID
love_id = vocabulary["love"]

# Temporary target for learning
target = torch.tensor([1.0, 0.0, 0.0])


for step in range(5):

    # Current embedding
    love_vector = embedding.weight[love_id]

    # Calculate loss
    loss = ((love_vector - target) ** 2).mean()

    print("Step:", step)
    print("Loss:", loss.item())
    print("Love:", love_vector)
    print()

    # Calculate gradients
    loss.backward()

    # Update embedding
    with torch.no_grad():
        embedding.weight -= 0.1 * embedding.weight.grad

    # Clear old gradients
    embedding.weight.grad.zero_()