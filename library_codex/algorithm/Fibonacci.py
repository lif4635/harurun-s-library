"""Fibonacci numbers by iterative fast doubling."""


def fibonacci(index, mod=None):
    """Return the 0-indexed Fibonacci number in O(log index)."""
    if index < 0:
        raise ValueError("index must be nonnegative")
    first, second = 0, 1
    for bit in bin(index)[2:]:
        doubled = first * ((second << 1) - first)
        next_value = first * first + second * second
        if mod is not None:
            doubled %= mod
            next_value %= mod
        if bit == "0":
            first, second = doubled, next_value
        else:
            first, second = next_value, doubled + next_value
            if mod is not None:
                second %= mod
    return first
