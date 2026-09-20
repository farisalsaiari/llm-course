import torch

from checkpoint import load_model_checkpoint
from device import get_device
from model import TinyModel
from paths import CHECKPOINT_PATH
from shape_debug import inspect_shapes
from subword_tokenizer import load_tokenizer


device = get_device()
tokenizer = load_tokenizer()
model, _ = load_model_checkpoint(
    CHECKPOINT_PATH,
    TinyModel,
    map_location=device
)
model = model.to(device).eval()
encoded_ids = tokenizer.encode("language models learn").ids
token_ids = torch.tensor(
    [encoded_ids[-model.max_seq_len:]],
    device=device
)

for name, shape in inspect_shapes(model, token_ids).items():
    print(f"{name:20} {shape}")
