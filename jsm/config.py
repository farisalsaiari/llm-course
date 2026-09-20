from dataclasses import asdict
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:

    vocab_size: int
    max_seq_len: int = 16
    embedding_dim: int = 32
    num_heads: int = 4
    num_kv_heads: int | None = None
    num_layers: int = 2
    ffn_multiplier: int = 4
    dropout: float = 0.0
    tie_embeddings: bool = True


    def __post_init__(self):

        positive_fields = {
            name: value
            for name, value in asdict(self).items()
            if name not in ("dropout", "num_kv_heads", "tie_embeddings")
        }

        for name, value in positive_fields.items():
            if value < 1:
                raise ValueError(f"{name} must be positive.")

        if self.embedding_dim % self.num_heads != 0:
            raise ValueError(
                "embedding_dim must be divisible by num_heads."
            )

        kv_heads = self.num_kv_heads or self.num_heads

        if kv_heads < 1 or self.num_heads % kv_heads != 0:
            raise ValueError(
                "num_kv_heads must be positive and divide num_heads."
            )

        if not 0 <= self.dropout < 1:
            raise ValueError("dropout must be in the interval [0, 1).")
