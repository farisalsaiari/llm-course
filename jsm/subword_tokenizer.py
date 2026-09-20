import json
from dataclasses import dataclass
from pathlib import Path

from paths import RAW_DATA_DIR, TOKENIZER_PATH


BOS_TOKEN = "<BOS>"
EOS_TOKEN = "<EOS>"
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"
SPECIAL_TOKENS = [BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN]


@dataclass
class Encoding:
    ids: list[int]


class ByteLevelBPETokenizer:

    def __init__(self, merges=None):
        self.merges = merges or []
        self.special_to_id = {
            token: index for index, token in enumerate(SPECIAL_TOKENS)
        }
        base_tokens = [bytes([value]) for value in range(256)]
        merged_tokens = [left + right for left, right in self.merges]
        self.byte_tokens = base_tokens + merged_tokens
        self.bytes_to_id = {
            token: len(SPECIAL_TOKENS) + index
            for index, token in enumerate(self.byte_tokens)
        }

    @staticmethod
    def _merge_pair(sequence, pair):
        result = []
        index = 0
        while index < len(sequence):
            if (
                index + 1 < len(sequence)
                and sequence[index] == pair[0]
                and sequence[index + 1] == pair[1]
            ):
                result.append(pair[0] + pair[1])
                index += 2
            else:
                result.append(sequence[index])
                index += 1
        return result

    def train(self, documents, vocab_size=300):
        minimum_size = len(SPECIAL_TOKENS) + 256
        if vocab_size < minimum_size:
            raise ValueError(f"vocab_size must be at least {minimum_size}.")

        sequences = [
            [bytes([value]) for value in document.encode("utf-8")]
            for document in documents
        ]
        known_tokens = set(self.byte_tokens)

        while minimum_size + len(self.merges) < vocab_size:
            pair_counts = {}
            for sequence in sequences:
                for pair in zip(sequence, sequence[1:]):
                    pair_counts[pair] = pair_counts.get(pair, 0) + 1

            candidates = sorted(
                pair_counts,
                key=lambda pair: (-pair_counts[pair], pair[0], pair[1])
            )
            selected_pair = next(
                (pair for pair in candidates if pair[0] + pair[1] not in known_tokens),
                None
            )
            if selected_pair is None:
                break

            self.merges.append(selected_pair)
            known_tokens.add(selected_pair[0] + selected_pair[1])
            sequences = [
                self._merge_pair(sequence, selected_pair)
                for sequence in sequences
            ]

        self.__init__(self.merges)

    def encode(self, text):
        sequence = [bytes([value]) for value in text.encode("utf-8")]
        for pair in self.merges:
            sequence = self._merge_pair(sequence, pair)
        return Encoding([self.bytes_to_id[token] for token in sequence])

    def decode(self, token_ids, skip_special_tokens=True):
        pieces = []
        for token_id in token_ids:
            if token_id < len(SPECIAL_TOKENS):
                if not skip_special_tokens:
                    pieces.append(SPECIAL_TOKENS[token_id].encode("utf-8"))
                continue
            pieces.append(self.byte_tokens[token_id - len(SPECIAL_TOKENS)])
        return b"".join(pieces).decode("utf-8", errors="replace")

    def token_to_id(self, token):
        return self.special_to_id.get(token)

    def id_to_token(self, token_id):
        if token_id < len(SPECIAL_TOKENS):
            return SPECIAL_TOKENS[token_id]
        return self.byte_tokens[
            token_id - len(SPECIAL_TOKENS)
        ].decode("utf-8", errors="replace")

    def get_vocab_size(self):
        return len(SPECIAL_TOKENS) + len(self.byte_tokens)

    def save(self, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "type": "byte_level_bpe_from_scratch",
            "special_tokens": SPECIAL_TOKENS,
            "merges": [
                [left.hex(), right.hex()] for left, right in self.merges
            ]
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, tokenizer_path):
        payload = json.loads(Path(tokenizer_path).read_text(encoding="utf-8"))
        if payload.get("type") != "byte_level_bpe_from_scratch":
            raise ValueError("Tokenizer artifact is not the from-scratch format.")
        merges = [
            (bytes.fromhex(left), bytes.fromhex(right))
            for left, right in payload["merges"]
        ]
        return cls(merges=merges)


def train_tokenizer(
    raw_folder=RAW_DATA_DIR,
    output_path=TOKENIZER_PATH,
    vocab_size=300
):
    raw_paths = sorted(Path(raw_folder).glob("*.txt"))
    if not raw_paths:
        raise ValueError(f"No .txt files found in {raw_folder}.")
    documents = [path.read_text(encoding="utf-8").strip() for path in raw_paths]
    tokenizer = ByteLevelBPETokenizer()
    tokenizer.train(documents, vocab_size=vocab_size)
    tokenizer.save(output_path)
    return tokenizer


def load_tokenizer(tokenizer_path=TOKENIZER_PATH):
    return ByteLevelBPETokenizer.load(tokenizer_path)


def load_or_train_tokenizer(
    tokenizer_path=TOKENIZER_PATH,
    raw_folder=RAW_DATA_DIR,
    vocab_size=300
):
    if Path(tokenizer_path).exists():
        try:
            return load_tokenizer(tokenizer_path)
        except (KeyError, TypeError, ValueError):
            pass
    return train_tokenizer(raw_folder, tokenizer_path, vocab_size)


def encode_documents(tokenizer, documents):
    bos_id = tokenizer.token_to_id(BOS_TOKEN)
    eos_id = tokenizer.token_to_id(EOS_TOKEN)
    return [
        [bos_id, *tokenizer.encode(document).ids, eos_id]
        for document in documents
    ]
