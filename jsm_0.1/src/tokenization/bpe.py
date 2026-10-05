from collections import Counter


def get_pair_counts(words: list[list[str]]) -> Counter:
    pair_counts = Counter()

    for word in words:
        for left, right in zip(word, word[1:]):
            pair_counts[(left, right)] += 1

    return pair_counts