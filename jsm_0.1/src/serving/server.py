import torch
from fastapi import FastAPI
from pydantic import BaseModel

from paths import CHECKPOINT_PATH, TOKENIZER_PATH
from src.inference.generator import generate
from src.model.config import ModelConfig
from src.model.model import TinyLLM
from src.tokenization.tokenizer import Tokenizer
from src.training.trainer import get_device


class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 50
    temperature: float = 0.0


class GenerateResponse(BaseModel):
    text: str


device = get_device()

tokenizer = Tokenizer.load(
    TOKENIZER_PATH
)

checkpoint = torch.load(
    CHECKPOINT_PATH,
    map_location=device,
)

config = ModelConfig(
    **checkpoint["config"]
)

model = TinyLLM(config)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.to(device)
model.eval()


app = FastAPI(
    title="JSM API",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "device": str(device),
    }


@app.post(
    "/generate",
    response_model=GenerateResponse,
)
def generate_text(
    request: GenerateRequest,
):
    text = generate(
        model=model,
        tokenizer=tokenizer,
        prompt=request.prompt,
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
    )

    return GenerateResponse(
        text=text
    )