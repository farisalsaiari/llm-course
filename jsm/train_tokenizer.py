import argparse

from subword_tokenizer import train_tokenizer


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--vocab-size", type=int, default=300)
    args = parser.parse_args()
    tokenizer = train_tokenizer(vocab_size=args.vocab_size)

    print("Tokenizer trained from local corpus.")
    print("Vocabulary size:", tokenizer.get_vocab_size())
    print("Learned merges:", len(tokenizer.merges))


if __name__ == "__main__":
    main()
