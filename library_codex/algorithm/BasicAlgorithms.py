"""Frequently reused iterative contest algorithms."""

from bisect import bisect_left, bisect_right


def fibonacci(index, mod=None):
    """Return F(index) by iterative fast doubling in O(log index)."""
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


def inversion_count(values):
    values = list(values)
    compressed = {value: i for i, value in enumerate(sorted(set(values)))}
    bit = [0] * (len(compressed) + 1)
    answer = 0
    for seen, value in enumerate(values):
        index = compressed[value] + 1
        prefix = 0
        i = index
        while i:
            prefix += bit[i]
            i &= i - 1
        answer += seen - prefix
        i = index
        while i < len(bit):
            bit[i] += 1
            i += i & -i
    return answer


def longest_increasing_subsequence(values, strict=True, restore=False):
    """Return LIS length, or ``(length, indices, subsequence)``."""
    values = list(values)
    tails = []
    tail_index = []
    parent = [-1] * len(values)
    search = bisect_left if strict else bisect_right
    for index, value in enumerate(values):
        position = search(tails, value)
        if position:
            parent[index] = tail_index[position - 1]
        if position == len(tails):
            tails.append(value)
            tail_index.append(index)
        else:
            tails[position] = value
            tail_index[position] = index
    if not restore:
        return len(tails)
    indices = []
    index = tail_index[-1] if tail_index else -1
    while index >= 0:
        indices.append(index)
        index = parent[index]
    indices.reverse()
    return len(tails), indices, [values[index] for index in indices]


def knapsack_01(weights, values, capacity):
    """Maximum value for every capacity up to ``capacity``."""
    if len(weights) != len(values):
        raise ValueError("weights and values have different lengths")
    unreachable = None
    dp = [unreachable] * (capacity + 1)
    dp[0] = 0
    for weight, value in zip(weights, values):
        if weight < 0:
            raise ValueError("weights must be nonnegative")
        for total in range(capacity, weight - 1, -1):
            previous = dp[total - weight]
            if previous is not None:
                candidate = previous + value
                if dp[total] is None or candidate > dp[total]:
                    dp[total] = candidate
    return dp


def knapsack_01_max(weights, values, capacity):
    return max(value for value in knapsack_01(weights, values, capacity)
               if value is not None)


def subset_sum_possible(values, limit=None):
    """Bitset subset-sum; return bit i iff sum i is reachable."""
    bits = 1
    mask = None if limit is None else (1 << (limit + 1)) - 1
    for value in values:
        if value < 0:
            raise ValueError("values must be nonnegative")
        bits |= bits << value
        if mask is not None:
            bits &= mask
    return bits


def subset_sum_restore(values, target):
    """Return indices of one subset totaling target, or None."""
    values = list(values)
    reachable = 1
    previous_item = [-1] * (target + 1)
    previous_sum = [-1] * (target + 1)
    mask = (1 << (target + 1)) - 1
    for item, value in enumerate(values):
        if value < 0:
            raise ValueError("values must be nonnegative")
        new = (reachable << value) & ~reachable & mask
        bits = new
        while bits:
            bit = bits & -bits
            total = bit.bit_length() - 1
            previous_item[total] = item
            previous_sum[total] = total - value
            bits ^= bit
        reachable |= new
    if not reachable >> target & 1:
        return None
    result = []
    while target:
        result.append(previous_item[target])
        target = previous_sum[target]
    result.reverse()
    return result


class Mo:
    """Offline range-query ordering with optional Hilbert-style alternation."""

    __slots__ = ("n", "queries", "block_size")

    def __init__(self, n, query_count=0, block_size=None):
        self.n = n
        self.queries = []
        self.block_size = block_size or max(1, int(n / max(1, query_count) ** 0.5))

    def add_query(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open query")
        self.queries.append((left, right, len(self.queries)))
        return len(self.queries) - 1

    def order(self):
        width = self.block_size
        return sorted(
            self.queries,
            key=lambda query: (
                query[0] // width,
                query[1] if (query[0] // width) & 1 == 0 else -query[1],
            ),
        )

    def run(self, add_left, add_right, remove_left, remove_right, get):
        answer = [None] * len(self.queries)
        left = right = 0
        for ql, qr, query_id in self.order():
            while ql < left:
                left -= 1
                add_left(left)
            while right < qr:
                add_right(right)
                right += 1
            while left < ql:
                remove_left(left)
                left += 1
            while qr < right:
                right -= 1
                remove_right(right)
            answer[query_id] = get()
        return answer


class Doubling:
    """Binary lifting for a functional graph, with optional additive values."""

    __slots__ = ("table", "sums")

    def __init__(self, successor, max_steps, values=None):
        levels = max(1, max_steps.bit_length())
        self.table = [list(successor)]
        self.sums = [list(values)] if values is not None else None
        for _ in range(1, levels):
            previous = self.table[-1]
            self.table.append([previous[previous[v]] for v in range(len(previous))])
            if values is not None:
                old = self.sums[-1]
                self.sums.append([old[v] + old[previous[v]]
                                  for v in range(len(previous))])

    def jump(self, vertex, steps):
        level = 0
        while steps:
            if steps & 1:
                vertex = self.table[level][vertex]
            steps >>= 1
            level += 1
        return vertex

    def jump_with_sum(self, vertex, steps):
        if self.sums is None:
            raise ValueError("values were not supplied")
        total = 0
        level = 0
        while steps:
            if steps & 1:
                total += self.sums[level][vertex]
                vertex = self.table[level][vertex]
            steps >>= 1
            level += 1
        return vertex, total


def coordinate_compress(values):
    ordered = sorted(set(values))
    mapping = {value: i for i, value in enumerate(ordered)}
    return ordered, mapping


def merge_intervals(intervals, merge_adjacent=True):
    intervals = sorted(intervals)
    result = []
    for left, right in intervals:
        if left > right:
            raise ValueError("interval endpoints are reversed")
        separated = (result and (
            left > result[-1][1] if merge_adjacent else left >= result[-1][1]
        ))
        if not result or separated:
            result.append([left, right])
        elif right > result[-1][1]:
            result[-1][1] = right
    return [tuple(interval) for interval in result]


def binary_search_int(predicate, false_value, true_value):
    """Boundary search with known false/true endpoints (either direction)."""
    while abs(true_value - false_value) > 1:
        middle = (true_value + false_value) // 2
        if predicate(middle):
            true_value = middle
        else:
            false_value = middle
    return true_value


def binary_search_float(predicate, false_value, true_value, iterations=80):
    for _ in range(iterations):
        middle = (false_value + true_value) * 0.5
        if predicate(middle):
            true_value = middle
        else:
            false_value = middle
    return true_value


def bit_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def submasks(mask, include_zero=True):
    submask = mask
    while submask:
        yield submask
        submask = (submask - 1) & mask
    if include_zero:
        yield 0


def supermasks(mask, bit_count):
    if mask < 0 or mask >= 1 << bit_count:
        raise ValueError("mask is outside the universe")
    current = mask
    limit = 1 << bit_count
    while current < limit:
        yield current
        current = (current + 1) | mask


def kth_element(values, index):
    """In-place-style iterative quickselect on a private list copy."""
    values = list(values)
    if not 0 <= index < len(values):
        raise IndexError("index out of range")
    left = 0
    right = len(values) - 1
    while left < right:
        pivot = values[(left + right) >> 1]
        lower = left
        current = left
        upper = right
        while current <= upper:
            if values[current] < pivot:
                values[lower], values[current] = values[current], values[lower]
                lower += 1
                current += 1
            elif values[current] > pivot:
                values[current], values[upper] = values[upper], values[current]
                upper -= 1
            else:
                current += 1
        if index < lower:
            right = lower - 1
        elif index > upper:
            left = upper + 1
        else:
            return pivot
    return values[left]


def radix_sort_nonnegative(values, bits=64, digit_bits=11):
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


def popcount(value):
    if value < 0:
        raise ValueError("popcount expects a nonnegative integer")
    return value.bit_count()


def most_significant_bit_index(value):
    if value <= 0:
        raise ValueError("value must be positive")
    return value.bit_length() - 1


def least_significant_bit_index(value):
    if value <= 0:
        raise ValueError("value must be positive")
    return (value & -value).bit_length() - 1


def ensure_permutation(permutation):
    size = len(permutation)
    seen = bytearray(size)
    for value in permutation:
        if not 0 <= value < size or seen[value]:
            return False
        seen[value] = 1
    return True


def permute(values, permutation):
    if len(values) != len(permutation) or not ensure_permutation(permutation):
        raise ValueError("invalid permutation")
    return [values[index] for index in permutation]


def permute_in_place(values, permutation):
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
    values = list(values)
    keys = [key(value) for value in values]
    return permute(values, bucket_sort_permutation(keys, maximum))


Popcount = popcount
MsbIndex = most_significant_bit_index
LsbIndex = least_significant_bit_index
