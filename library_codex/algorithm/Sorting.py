"""Selection-free integer sorting and permutation utilities."""


def radix_sort_nonnegative(values, bits=64, digit_bits=11):
    """Sort nonnegative integers by stable least-significant-digit passes."""
    values = list(values)
    if any(value < 0 for value in values):
        raise ValueError("radix sort requires nonnegative integers")
    base = 1 << digit_bits
    mask = base - 1
    output = [0] * len(values)
    for shift in range(0, bits, digit_bits):
        count = [0] * base
        for value in values:
            count[value >> shift & mask] += 1
        total = 0
        for i, amount in enumerate(count):
            count[i] = total
            total += amount
        for value in values:
            digit = value >> shift & mask
            output[count[digit]] = value
            count[digit] += 1
        values, output = output, values
    return values


def ensure_permutation(permutation):
    """Return whether permutation contains each integer in [0, n) once."""
    size = len(permutation)
    seen = bytearray(size)
    for value in permutation:
        if not 0 <= value < size or seen[value]:
            return False
        seen[value] = 1
    return True


def permute(values, permutation):
    """Return values reordered as values[permutation[i]]."""
    if len(values) != len(permutation) or not ensure_permutation(permutation):
        raise ValueError("invalid permutation")
    return [values[index] for index in permutation]


def permute_in_place(values, permutation):
    """Apply the same ordering as permute while mutating values."""
    if len(values) != len(permutation) or not ensure_permutation(permutation):
        raise ValueError("invalid permutation")
    permutation = list(permutation)
    for start in range(len(values)):
        current = start
        while permutation[current] != start:
            target = permutation[current]
            values[current], values[target] = values[target], values[current]
            permutation[current], current = current, target
        permutation[current] = current
    return values


def bucket_sort_permutation(keys, maximum=None):
    """Return original indices in stable nonnegative-integer-key order."""
    keys = list(keys)
    if not keys:
        return []
    if maximum is None:
        maximum = max(keys)
    if maximum < 0 or any(key < 0 or key > maximum for key in keys):
        raise ValueError("bucket keys are outside the declared range")
    count = [0] * (maximum + 2)
    for key in keys:
        count[key + 1] += 1
    for index in range(maximum + 1):
        count[index + 1] += count[index]
    result = [0] * len(keys)
    for index, key in enumerate(keys):
        result[count[key]] = index
        count[key] += 1
    return result


def bucket_sort(values, key=lambda value: value, maximum=None):
    """Stable-sort values by nonnegative integer keys."""
    values = list(values)
    keys = [key(value) for value in values]
    return permute(values, bucket_sort_permutation(keys, maximum))


def inverse_permutation(permutation):
    """Return ``inverse[permutation[i]] == i`` for a permutation."""
    if not ensure_permutation(permutation):
        raise ValueError("invalid permutation")
    inverse = [0] * len(permutation)
    for index, value in enumerate(permutation):
        inverse[value] = index
    return inverse


def compose_permutations(first, second):
    """Return the composition ``first[second[i]]``."""
    if len(first) != len(second):
        raise ValueError("permutations have different sizes")
    if not ensure_permutation(first) or not ensure_permutation(second):
        raise ValueError("invalid permutation")
    return [first[second[index]] for index in range(len(first))]


def permutation_cycles(permutation, include_fixed=False):
    """Return disjoint cycles in increasing order of their first vertex."""
    if not ensure_permutation(permutation):
        raise ValueError("invalid permutation")
    used = bytearray(len(permutation))
    result = []
    for start in range(len(permutation)):
        if used[start]:
            continue
        cycle = []
        vertex = start
        while not used[vertex]:
            used[vertex] = 1
            cycle.append(vertex)
            vertex = permutation[vertex]
        if include_fixed or len(cycle) > 1:
            result.append(cycle)
    return result


def permutation_power(permutation, exponent):
    """Return the signed integer power of a permutation in O(N)."""
    if not ensure_permutation(permutation):
        raise ValueError("invalid permutation")
    result = list(range(len(permutation)))
    for cycle in permutation_cycles(permutation, include_fixed=True):
        size = len(cycle)
        shift = exponent % size
        for index, vertex in enumerate(cycle):
            result[vertex] = cycle[(index + shift) % size]
    return result
