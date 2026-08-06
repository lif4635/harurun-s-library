"""Bit positions, submasks, and supermasks."""


def bit_indices(mask):
    """Yield the set-bit positions in increasing order."""
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def submasks(mask, include_zero=True):
    """Yield every submask in decreasing order."""
    submask = mask
    while submask:
        yield submask
        submask = (submask - 1) & mask
    if include_zero:
        yield 0


def supermasks(mask, bit_count):
    """Yield every bit_count-wide mask containing mask."""
    if mask < 0 or mask >= 1 << bit_count:
        raise ValueError("mask is outside the universe")
    current = mask
    limit = 1 << bit_count
    while current < limit:
        yield current
        current = (current + 1) | mask


def popcount(value):
    if value < 0:
        raise ValueError("popcount expects a nonnegative integer")
    return value.bit_count()


def msb_index(value):
    if value <= 0:
        raise ValueError("value must be positive")
    return value.bit_length() - 1


def lsb_index(value):
    if value <= 0:
        raise ValueError("value must be positive")
    return (value & -value).bit_length() - 1
