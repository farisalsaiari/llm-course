import torch
import torch.nn as nn

from embedding import embedding, vocabulary


# Get "love" embedding
love_id = vocabulary["love"]
love_vector = embedding.weight[love_id]

# Correct next word = "coffee"
coffee_id = vocabulary["coffee"]
target = torch.tensor([coffee_id])


# Create output layer
output_layer = nn.Linear(
    3,
    len(vocabulary)
)


# Loss function
loss_function = nn.CrossEntropyLoss()


# Optimizer
optimizer = torch.optim.SGD(
    output_layer.parameters(),
    lr=0.1
)


# Train  times
for step in range(20):

    # Embedding → Logits
    logits = output_layer(love_vector)

    # Add batch dimension for CrossEntropyLoss
    logits = logits.unsqueeze(0)

    # Calculate error
    loss = loss_function(logits, target)

    print("Step:", step)
    print("Loss:", loss.item())

    # Clear old gradients
    optimizer.zero_grad()

    # Calculate gradients
    loss.backward()

    # Update weights
    optimizer.step()

    print()




# Test the model after training
with torch.no_grad():

    # love embedding → logits
    final_logits = output_layer(love_vector)

    # logits → probabilities
    probabilities = torch.softmax(final_logits, dim=0)


print("After training:")

for word, probability in zip(vocabulary.keys(), probabilities):
    print(word, "→", probability.item())