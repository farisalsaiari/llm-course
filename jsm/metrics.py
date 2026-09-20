import math


def perplexity(loss):

    try:
        return math.exp(float(loss))
    except OverflowError:
        return float("inf")
