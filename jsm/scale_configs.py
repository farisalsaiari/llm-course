from dataclasses import dataclass

from scaling import estimate_decoder_parameters


@dataclass(frozen=True)
class ScaleConfig:
    name: str
    vocab_size: int
    max_seq_len: int
    embedding_dim: int
    num_heads: int
    num_layers: int
    ffn_multiplier: int = 4
    executable_locally: bool = False

    def parameter_estimate(self):
        return estimate_decoder_parameters(
            self.vocab_size,
            self.max_seq_len,
            self.embedding_dim,
            self.num_layers,
            self.ffn_multiplier,
            tie_embeddings=True,
            learned_positions=True
        )["total"]


SCALE_CONFIGS = (
    ScaleConfig("tiny", 300, 16, 32, 4, 2, executable_locally=True),
    ScaleConfig("mini", 8_000, 256, 256, 8, 6, executable_locally=True),
    ScaleConfig("conceptual_100m", 32_000, 1_024, 768, 12, 10),
    ScaleConfig("conceptual_1b", 32_000, 4_096, 2_048, 16, 18)
)
