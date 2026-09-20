import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument("prompt", nargs="?", default="i love")
parser.add_argument("--interactive", action="store_true")
parser.add_argument("--max-new-tokens", type=int, default=20)
parser.add_argument("--temperature", type=float, default=0.8)
parser.add_argument("--top-k", type=int, default=40)
parser.add_argument("--top-p", type=float, default=0.95)
args = parser.parse_args()

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


def run_prompt(input_text):

    generated_text = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=input_text,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p
    )

    input_ids = tokenizer.encode(input_text).ids

    if not input_ids:
        print("Enter at least one character.")
        return

    input_tensor = torch.tensor(
        [input_ids[-model.max_seq_len:]],
        device=device
    )

    with torch.no_grad():
        logits = model(input_tensor)
        probabilities = torch.softmax(logits[0, -1], dim=0)

    top_probabilities, top_ids = torch.topk(
        probabilities,
        k=min(5, vocab_size)
    )

    print("Generated continuation:")
    print(generated_text)
    print("Top next-token predictions:")

    for token_id, probability in zip(
        top_ids.tolist(),
        top_probabilities.tolist()
    ):
        print(
            repr(tokenizer.id_to_token(token_id)),
            "→",
            round(probability * 100, 2),
            "%"
        )


if args.interactive:
    print("Enter text for continuation. Type 'exit' to stop.")

    while True:
        prompt = input("You> ").strip()

        if prompt.lower() in {"exit", "quit"}:
            break

        run_prompt(prompt)
        print()
else:
    run_prompt(args.prompt)
