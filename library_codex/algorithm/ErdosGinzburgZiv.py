"""Constructive Erdős–Ginzburg–Ziv subset selection."""

from array import array


def erdos_ginzburg_ziv_indices(order, values):
    """Choose order of 2*order-1 values whose sum is 0 modulo order."""
    if order <= 0 or len(values) < 2 * order - 1:
        raise ValueError("EGZ needs at least 2*order-1 values")
    if order == 1:
        return [0]
    values = [value % order for value in values[: 2 * order - 1]]
    mask = (1 << order) - 1
    reachable = [0] * (order + 1)
    reachable[0] = 1
    total = (order + 1) * order
    parent_item = array("i", [-1]) * total
    parent_residue = array("i", [-1]) * total
    for item, shift in enumerate(values):
        upper = min(order, item + 1)
        for count in range(upper, 0, -1):
            previous = reachable[count - 1]
            if shift:
                rotated = ((previous << shift) | (previous >> (order - shift))) & mask
            else:
                rotated = previous
            new = rotated & ~reachable[count]
            reachable[count] |= rotated
            bits = new
            while bits:
                bit = bits & -bits
                residue = bit.bit_length() - 1
                index = count * order + residue
                parent_item[index] = item
                parent_residue[index] = (residue - shift) % order
                bits ^= bit
        if reachable[order] & 1:
            break
    if reachable[order] & 1 == 0:
        raise ArithmeticError("EGZ theorem invariant failed")
    result = []
    count = order
    residue = 0
    while count:
        index = count * order + residue
        result.append(parent_item[index])
        residue = parent_residue[index]
        count -= 1
    result.reverse()
    return result
