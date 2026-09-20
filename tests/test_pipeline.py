import sys
import tempfile
import unittest
from pathlib import Path

import torch


JSM_DIR = Path(__file__).resolve().parents[1] / "jsm"
sys.path.insert(0, str(JSM_DIR))

from attention import SelfAttention
from checkpoint import load_model_checkpoint, save_training_checkpoint
from config import ModelConfig
from generation import generate
from model import TinyModel
from subword_tokenizer import ByteLevelBPETokenizer
from transformer_block import TransformerBlock


class TokenizerTests(unittest.TestCase):

    def test_encode_decode_and_persistence(self):
        tokenizer = ByteLevelBPETokenizer()
        tokenizer.train(["hello world", "hello model"], vocab_size=270)

        for text in ("hello world", "unseen!", "مرحبا"):
            self.assertEqual(tokenizer.decode(tokenizer.encode(text).ids), text)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tokenizer.json"
            tokenizer.save(path)
            loaded = ByteLevelBPETokenizer.load(path)
            self.assertEqual(loaded.merges, tokenizer.merges)


class ArchitectureTests(unittest.TestCase):

    def test_gqa_shape_and_causal_mask(self):
        torch.manual_seed(1)
        attention = SelfAttention(16, num_heads=4, num_kv_heads=2).eval()
        vectors = torch.randn(2, 5, 16)
        changed = vectors.clone()
        changed[:, -1] += 100

        with torch.no_grad():
            output = attention(vectors)
            changed_output = attention(changed)

        self.assertEqual(output.shape, vectors.shape)
        self.assertTrue(torch.allclose(
            output[:, :-1], changed_output[:, :-1], atol=1e-5
        ))

    def test_block_and_model_shapes(self):
        block = TransformerBlock(16, num_heads=4, num_kv_heads=2)
        vectors = torch.randn(2, 5, 16)
        self.assertEqual(block(vectors).shape, vectors.shape)

        model = TinyModel(ModelConfig(
            vocab_size=40,
            max_seq_len=8,
            embedding_dim=16,
            num_heads=4,
            num_kv_heads=2
        ))
        logits = model(torch.randint(40, (2, 5)))
        self.assertEqual(logits.shape, (2, 5, 40))

    def test_cached_logits_match_full_logits(self):
        torch.manual_seed(2)
        model = TinyModel(ModelConfig(
            vocab_size=40,
            max_seq_len=8,
            embedding_dim=16,
            num_heads=4,
            num_kv_heads=2
        )).eval()
        tokens = torch.tensor([[4, 5, 6, 7]])

        with torch.no_grad():
            full_logits = model(tokens)
            caches = None
            pieces = []

            for index in range(tokens.shape[1]):
                logits, caches = model(
                    tokens[:, index:index + 1],
                    caches=caches,
                    use_cache=True
                )
                pieces.append(logits)

        cached_logits = torch.cat(pieces, dim=1)
        self.assertTrue(torch.allclose(
            full_logits, cached_logits, atol=1e-5
        ))


class WorkflowTests(unittest.TestCase):

    def test_generation_and_checkpoint_round_trip(self):
        tokenizer = ByteLevelBPETokenizer()
        tokenizer.train(["small generation test"], vocab_size=270)
        config = ModelConfig(
            vocab_size=tokenizer.get_vocab_size(),
            max_seq_len=8,
            embedding_dim=16,
            num_heads=4,
            num_layers=1
        )
        model = TinyModel(config)
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.LambdaLR(
            optimizer, lambda _: 1.0
        )

        self.assertEqual(
            generate(model, tokenizer, "small", max_new_tokens=0),
            "small"
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.pt"
            save_training_checkpoint(
                path, model, optimizer, scheduler, epoch=2, global_step=9
            )
            loaded, checkpoint = load_model_checkpoint(path, TinyModel)
            self.assertEqual(loaded.config, model.config)
            self.assertEqual(checkpoint["epoch"], 2)
            self.assertEqual(checkpoint["global_step"], 9)


if __name__ == "__main__":
    unittest.main()
