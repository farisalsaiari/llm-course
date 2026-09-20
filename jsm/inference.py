import torch

from checkpoint import load_model_checkpoint
from device import get_device
from generation import generate
from model import TinyModel
from paths import CHECKPOINT_PATH
from subword_tokenizer import load_tokenizer


# -----------------------------------
# Load Tokenizer
# -----------------------------------

tokenizer = load_tokenizer()
vocab_size = tokenizer.get_vocab_size()
device = get_device()

print("Device:", device)


# -----------------------------------
# Load Model and Saved Checkpoint
# -----------------------------------

model, checkpoint = load_model_checkpoint(
    path=CHECKPOINT_PATH,
    model_class=TinyModel,
    map_location=device
)
model = model.to(device)

if model.config.vocab_size != vocab_size:
    raise ValueError("Checkpoint and tokenizer vocabulary sizes differ.")


# -----------------------------------
# Evaluation Mode
# -----------------------------------

model.eval()


generated_text = generate(
    model=model,
    tokenizer=tokenizer,
    prompt="i love",
    max_new_tokens=10,
    temperature=0.8,
    top_k=40,
    top_p=0.95
)

print("Generated text:")
print(generated_text)


# -----------------------------------
# Input Context
# -----------------------------------

input_text = "i love"


# -----------------------------------
# Words → Token IDs
# -----------------------------------

input_ids = tokenizer.encode(
    input_text
).ids


input_tensor = torch.tensor(
    [input_ids],
    device=device
)


# -----------------------------------
# Run Model
# -----------------------------------

with torch.no_grad():

    logits = model(
        input_tensor
    )

    next_token_logits = logits[0, -1]


    probabilities = torch.softmax(
        next_token_logits,
        dim=0
    )


# -----------------------------------
# Show Prediction
# -----------------------------------

print(
    "Input:",
    repr(input_text)
)

print()

print(
    "Predictions:"
)


top_probabilities, top_ids = torch.topk(
    probabilities,
    k=min(5, vocab_size)
)

for token_id, probability in zip(
    top_ids.tolist(),
    top_probabilities.tolist()
):

    print(
        repr(tokenizer.id_to_token(token_id)),
        "→",
        round(
            probability * 100,
            2
        ),
        "%"
    )
