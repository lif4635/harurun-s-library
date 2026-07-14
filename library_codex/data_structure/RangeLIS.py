from bisect import bisect_left

from library_codex.data_structure.WaveletMatrix import WaveletMatrix


def _squaredot(first, second):
    results = []
    tasks = [(0, first, second)]
    while tasks:
        kind, *payload = tasks.pop()
        if kind == 0:
            left, right = payload
            n = len(left)
            if n == 1:
                results.append([0])
                continue
            half = n >> 1
            inverse = [0] * n
            for index, value in enumerate(left):
                inverse[value] = index
            lower_left = []
            upper_left = []
            lower_right = []
            upper_right = []
            lower_values = []
            upper_values = []
            zipped = [0] * n
            lower_index = upper_index = 0
            for value in range(n):
                position = inverse[value]
                if position < half:
                    zipped[position] = lower_index
                    lower_index += 1
                    lower_values.append(value)
                else:
                    zipped[position] = upper_index
                    upper_index += 1
                    upper_values.append(value)
                if right[value] < half:
                    lower_right.append(right[value])
                else:
                    upper_right.append(right[value] - half)
            lower_left = zipped[:half]
            upper_left = zipped[half:]
            tasks.append((1, n, right, lower_values, upper_values))
            tasks.append((0, upper_left, upper_right))
            tasks.append((0, lower_left, lower_right))
        else:
            n, right, lower_values, upper_values = payload
            upper_result = results.pop()
            lower_result = results.pop()
            infinity = n
            lower = [infinity] * n
            upper = [infinity] * n
            lower_index = upper_index = 0
            for index in range(n):
                if right[index] < n // 2:
                    lower[index] = lower_values[lower_result[lower_index]]
                    lower_index += 1
                else:
                    upper[index] = upper_values[upper_result[upper_index]]
                    upper_index += 1
            inverse_lower = [infinity] * n
            inverse_upper = [infinity] * n
            for index in range(n):
                if lower[index] != infinity:
                    inverse_lower[lower[index]] = index
                if upper[index] != infinity:
                    inverse_upper[upper[index]] = index
            result = [infinity] * n
            lower_i, lower_j = n, -1
            upper_i, upper_j = n, -1
            lower_delta = upper_delta = 0
            while not (lower_i < 0 and upper_j >= n):
                if lower_delta > 0:
                    lower_j += 1
                    if (lower_j < n and upper[lower_j] != infinity
                            and upper[lower_j] < lower_i):
                        lower_delta -= 1
                    if (lower_j < n and lower[lower_j] != infinity
                            and lower[lower_j] >= lower_i):
                        lower_delta -= 1
                else:
                    lower_i -= 1
                    if (lower_i >= 0 and inverse_upper[lower_i] != infinity
                            and inverse_upper[lower_i] <= lower_j):
                        lower_delta += 1
                    if (lower_i >= 0 and inverse_lower[lower_i] != infinity
                            and inverse_lower[lower_i] > lower_j):
                        lower_delta += 1
                if (0 <= lower_j < n and lower[lower_j] != infinity
                        and lower[lower_j] <= lower_i):
                    result[lower_j] = lower[lower_j]
                if upper_delta >= 0:
                    upper_j += 1
                    if (upper_j < n and upper[upper_j] != infinity
                            and upper[upper_j] < upper_i):
                        upper_delta -= 1
                    if (upper_j < n and lower[upper_j] != infinity
                            and lower[upper_j] >= upper_i):
                        upper_delta -= 1
                else:
                    upper_i -= 1
                    if (upper_i >= 0 and inverse_upper[upper_i] != infinity
                            and inverse_upper[upper_i] <= upper_j):
                        upper_delta += 1
                    if (upper_i >= 0 and inverse_lower[upper_i] != infinity
                            and inverse_lower[upper_i] > upper_j):
                        upper_delta += 1
                if (0 <= upper_j < n and upper[upper_j] != infinity
                        and upper[upper_j] >= upper_i):
                    result[upper_j] = upper[upper_j]
                if (0 <= lower_j < n and lower_i == upper_i
                        and lower_j == upper_j):
                    result[lower_j] = lower_i
            results.append(result)
    return results[0]


def _seaweed(permutation):
    results = []
    tasks = [(0, permutation)]
    while tasks:
        kind, *payload = tasks.pop()
        if kind == 0:
            values = payload[0]
            n = len(values)
            if n == 1:
                results.append([n])
                continue
            half = n >> 1
            lower = []
            upper = []
            lower_positions = []
            upper_positions = []
            for index, value in enumerate(values):
                if value < half:
                    lower.append(value)
                    lower_positions.append(index)
                else:
                    upper.append(value - half)
                    upper_positions.append(index)
            tasks.append((1, values, lower_positions, upper_positions))
            tasks.append((0, upper))
            tasks.append((0, lower))
        elif kind == 1:
            values, lower_positions, upper_positions = payload
            upper_result = results.pop()
            lower_result = results.pop()
            n = len(values)
            infinity = n
            first = list(range(n))
            second = list(range(n))
            lower_index = upper_index = 0
            for index, value in enumerate(values):
                if value < n // 2:
                    mapped = lower_result[lower_index]
                    first[index] = (infinity if mapped == n // 2
                                    else lower_positions[mapped])
                    lower_index += 1
                else:
                    mapped = upper_result[upper_index]
                    second[index] = (infinity if mapped == n - n // 2
                                     else upper_positions[mapped])
                    upper_index += 1
            a = [infinity] * n
            reverse_first = [infinity] * n
            for index, value in enumerate(first):
                if value != infinity:
                    reverse_first[value] = index
            position = n - 1
            to_source = [infinity] * n
            for index in range(n - 1, -1, -1):
                if reverse_first[index] != infinity:
                    a[reverse_first[index]] = position
                    to_source[position] = index
                    position -= 1
            for index in range(n):
                if a[index] == infinity:
                    a[index] = position
                    position -= 1
            b = [0] * n
            to_target = [infinity] * n
            used = bytearray(n)
            position = 0
            for index, value in enumerate(second):
                if value != infinity:
                    b[position] = value
                    to_target[position] = index
                    position += 1
                    used[value] = 1
            for value in range(n):
                if not used[value]:
                    b[position] = value
                    position += 1
            tasks.append((2, n, to_source, to_target))
            tasks.append((3, a, b))
        elif kind == 3:
            results.append(_squaredot(payload[0], payload[1]))
        else:
            n, to_source, to_target = payload
            composed = results.pop()
            infinity = n
            result = [infinity] * n
            for index in range(n):
                if (to_target[index] != infinity
                        and to_source[composed[index]] != infinity):
                    result[to_target[index]] = to_source[composed[index]]
            results.append(result)
    return results[0]


class RangeLIS:
    __slots__ = ("length", "size", "matrix")

    def __init__(self, sequence):
        self.length = len(sequence)
        size = 1
        while size < len(sequence):
            size <<= 1
        self.size = size
        order = list(range(len(sequence) - 1, -1, -1))
        order.sort(key=sequence.__getitem__)
        permutation = [0] * size
        for rank, position in enumerate(order):
            permutation[position] = rank
        for position in range(len(sequence), size):
            permutation[position] = position
        table = _seaweed(permutation) if size else []
        self.matrix = WaveletMatrix(table)

    def query(self, left, right):
        if not 0 <= left <= right <= self.length:
            raise IndexError("invalid half-open range")
        if left == right:
            return 0
        greater_equal = self.matrix.range_freq(
            0, right, left, self.size
        )
        return right - left - greater_equal

    lis = query


def lis_brute(sequence):
    tails = []
    for value in sequence:
        position = bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    return len(tails)
