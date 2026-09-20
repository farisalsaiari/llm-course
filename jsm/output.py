import torch
import torch.nn as nn
import torch.nn.functional as F
from embedding import embedding, vocabulary


# Get the ID for "love"
love_id = vocabulary["love"]

# Get the embedding vector for "love"
love_vector = embedding.weight[love_id]


# Create output layer:
# 3 embedding numbers → one score for every vocabulary token
output_layer = nn.Linear(
    3,
    len(vocabulary)
)


# Embedding vector → Logits
logits = output_layer(love_vector)


print("Love embedding:")
print(love_vector)

print("Logits:")
print(logits)

# Show each token with its logit score
for word, logit in zip(vocabulary.keys(), logits):
    print(word, "→", logit.item())


# Convert logits into probabilities
probabilities = F.softmax(logits, dim=0)

print("Probabilities:")

for word, probability in zip(vocabulary.keys(), probabilities):
    print(word, "→", probability.item())



# Get the ID with the highest probability
next_token_id = torch.argmax(probabilities).item()

# Convert ID back to word
next_word = list(vocabulary.keys())[next_token_id]

print("Next token ID:", next_token_id)
print("Predicted next word:", next_word)