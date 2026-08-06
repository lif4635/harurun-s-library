"""Split a modular arithmetic progression into ordinary arithmetic runs."""

from math import isqrt


def split_mod_progression(multiplier, addend, count, modulus):
    """Split (multiplier*k+addend)%modulus into O(sqrt(count)) runs."""
    if count < 0 or modulus <= 0:
        raise ValueError("count must be nonnegative and modulus positive")
    if count == 0:
        return []
    multiplier %= modulus
    addend %= modulus
    bound = isqrt(count)
    best_index = 1
    best_value = modulus
    for index in range(1, bound + 1):
        value = multiplier * index % modulus
        value = min(value, modulus - value)
        if value < best_value:
            best_value = value
            best_index = index
    flipped = multiplier * best_index % modulus > modulus - (
        multiplier * best_index % modulus
    )
    if flipped:
        multiplier = (-multiplier) % modulus
        addend = modulus - 1 - addend
    result = []
    delta = multiplier * best_index % modulus
    for group in range(best_index):
        length = (count - group + best_index - 1) // best_index
        if length <= 0:
            continue
        start_value = (multiplier * group + addend) % modulus
        crossings = (delta * (length - 1) + start_value) // modulus + 1
        left = 0
        for crossing in range(crossings):
            if crossing + 1 == crossings:
                right = length
            else:
                right = (
                    modulus * (crossing + 1) - start_value + delta - 1
                ) // delta
            value = (delta * left + start_value) % modulus
            if flipped:
                value = modulus - 1 - value
                value_delta = -best_index * multiplier
            else:
                value_delta = best_index * multiplier
            result.append(
                (
                    best_index * left + group,
                    value,
                    best_index,
                    value_delta,
                    right - left,
                )
            )
            left = right
    return result
