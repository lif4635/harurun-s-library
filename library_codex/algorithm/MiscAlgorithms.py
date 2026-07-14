from math import isqrt
from array import array


def integer_partitions(number):
    """All partitions in nonincreasing order, generated without recursion."""
    if number < 0:
        raise ValueError("number must be nonnegative")
    if number == 0:
        return [()]
    result = []
    partition = [number]
    while True:
        result.append(tuple(partition))
        remainder = 0
        while partition and partition[-1] == 1:
            remainder += partition.pop()
        if not partition:
            break
        partition[-1] -= 1
        remainder += 1
        while remainder > partition[-1]:
            remainder -= partition[-1]
            partition.append(partition[-1])
        partition.append(remainder)
    return result


def integer_partitions_up_to(limit):
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    return [integer_partitions(number) for number in range(limit + 1)]


def nearest_congruent_at_least(value, lower_bound, modulus):
    modulus = abs(modulus)
    if modulus == 0:
        raise ValueError("modulus must be nonzero")
    return value + ((lower_bound - value + modulus - 1) // modulus) * modulus \
        if value < lower_bound else value - (value - lower_bound) // modulus * modulus


def modular_power(base, exponent, modulus):
    if exponent < 0 or modulus == 0:
        raise ValueError("exponent must be nonnegative and modulus nonzero")
    return pow(base, exponent, modulus)


def exact_square_root(number):
    if number < 0:
        return -1
    root = isqrt(number)
    return root if root * root == number else -1


def decimal_digit_count(number, zero=1):
    if number == 0:
        return zero
    return len(str(abs(number)))


def erdos_ginzburg_ziv_indices(order, values):
    """Choose ``order`` of 2*order-1 values whose sum is 0 mod order."""
    if order <= 0 or len(values) < 2 * order - 1:
        raise ValueError("EGZ needs at least 2*order-1 values")
    if order == 1:
        return [0]
    values = [value % order for value in values[:2 * order - 1]]
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


def split_modular_arithmetic_progression(multiplier, addend, count, modulus):
    """Split (multiplier*k+addend)%modulus into O(sqrt(count)) arithmetic runs."""
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
                right = (modulus * (crossing + 1) - start_value + delta - 1) // delta
            value = (delta * left + start_value) % modulus
            if flipped:
                value = modulus - 1 - value
                value_delta = -best_index * multiplier
            else:
                value_delta = best_index * multiplier
            result.append((best_index * left + group, value,
                           best_index, value_delta, right - left))
            left = right
    return result


EnumeratePartitions = integer_partitions_up_to
nearest_equiv = nearest_congruent_at_least
powmod = modular_power
sqrt_heuristic_for_floor_sum = split_modular_arithmetic_progression
SqrtInt = exact_square_root
isDigit = decimal_digit_count
ErdosGinzburgZivTask = erdos_ginzburg_ziv_indices
