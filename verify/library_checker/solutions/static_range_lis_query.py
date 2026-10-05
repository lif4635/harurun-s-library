_range_query_wavelet_matrix_MASK = [(1 << i) - 1 for i in range(64)]

class WaveletMatrix:
    __slots__ = ('n', 'log', 'mid', 'blocks', 'prefix')

    def __init__(self, a):
        n = len(a)
        if n:
            assert min(a) >= 0
            log = max(1, max(a).bit_length())
        else:
            log = 1
        mid = [0] * log
        blocks = [None] * log
        prefix = [None] * log
        cur = list(a)
        block_count = (n >> 6) + 1
        for h in range(log - 1, -1, -1):
            block = [0] * block_count
            zero = []
            one = []
            bit = 1 << h
            for (i, x) in enumerate(cur):
                if x & bit:
                    block[i >> 6] |= 1 << (i & 63)
                    one.append(x)
                else:
                    zero.append(x)
            pref = [0] * (block_count + 1)
            for (i, x) in enumerate(block):
                pref[i + 1] = pref[i] + x.bit_count()
            mid[h] = len(zero)
            blocks[h] = block
            prefix[h] = pref
            cur = zero + one
        self.n = n
        self.log = log
        self.mid = mid
        self.blocks = blocks
        self.prefix = prefix

    def access(self, k):
        assert 0 <= k < self.n
        res = 0
        mask = _range_query_wavelet_matrix_MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            b = k >> 6
            o = k & 63
            ones = prefix[h][b] + (block[b] & mask[o]).bit_count()
            if block[b] >> o & 1:
                res |= 1 << h
                k = mid[h] + ones
            else:
                k -= ones
        return res
    __getitem__ = access

    def rank(self, l, r, x):
        assert 0 <= l <= r <= self.n
        if x < 0 or x >= 1 << self.log:
            return 0
        mask = _range_query_wavelet_matrix_MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            pref = prefix[h]
            lb = l >> 6
            rb = r >> 6
            lo = l & 63
            ro = r & 63
            l1 = pref[lb] + (block[lb] & mask[lo]).bit_count()
            r1 = pref[rb] + (block[rb] & mask[ro]).bit_count()
            if x >> h & 1:
                l = mid[h] + l1
                r = mid[h] + r1
            else:
                l -= l1
                r -= r1
        return r - l
    count = rank

    def kth_smallest(self, l, r, k):
        assert 0 <= l <= r <= self.n and 0 <= k < r - l
        res = 0
        mask = _range_query_wavelet_matrix_MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            pref = prefix[h]
            lb = l >> 6
            rb = r >> 6
            lo = l & 63
            ro = r & 63
            l1 = pref[lb] + (block[lb] & mask[lo]).bit_count()
            r1 = pref[rb] + (block[rb] & mask[ro]).bit_count()
            zeros = r - l - r1 + l1
            if k < zeros:
                l -= l1
                r -= r1
            else:
                k -= zeros
                res |= 1 << h
                l = mid[h] + l1
                r = mid[h] + r1
        return res
    quantile = kth_smallest

    def kth_largest(self, l, r, k):
        assert 0 <= k < r - l
        return self.kth_smallest(l, r, r - l - k - 1)

    def count_lt(self, l, r, upper):
        assert 0 <= l <= r <= self.n
        if upper <= 0:
            return 0
        if upper >= 1 << self.log:
            return r - l
        res = 0
        mask = _range_query_wavelet_matrix_MASK
        blocks = self.blocks
        prefix = self.prefix
        mid = self.mid
        for h in range(self.log - 1, -1, -1):
            block = blocks[h]
            pref = prefix[h]
            lb = l >> 6
            rb = r >> 6
            lo = l & 63
            ro = r & 63
            l1 = pref[lb] + (block[lb] & mask[lo]).bit_count()
            r1 = pref[rb] + (block[rb] & mask[ro]).bit_count()
            if upper >> h & 1:
                res += r - l - r1 + l1
                l = mid[h] + l1
                r = mid[h] + r1
            else:
                l -= l1
                r -= r1
        return res
    range_lowerbound = count_lt

    def count_le(self, l, r, upper):
        return self.count_lt(l, r, upper + 1)
    range_upperbound = count_le

    def range_freq(self, l, r, lower, upper=None):
        if upper is None:
            return self.count_lt(l, r, lower)
        return self.count_lt(l, r, upper) - self.count_lt(l, r, lower)

    def prev_value(self, l, r, upper, default=-1):
        k = self.count_lt(l, r, upper)
        return default if k == 0 else self.kth_smallest(l, r, k - 1)

    def next_value(self, l, r, lower, default=-1):
        k = self.count_lt(l, r, lower)
        return default if k == r - l else self.kth_smallest(l, r, k)

    def max_le(self, l, r, x, default=-1):
        k = self.count_le(l, r, x)
        return default if k == 0 else self.kth_smallest(l, r, k - 1)

    def min_ge(self, l, r, x, default=-1):
        return self.next_value(l, r, x, default)
from bisect import bisect_left

def _segment_tree_range_lis_squaredot(first, second):
    results = []
    tasks = [(0, first, second)]
    while tasks:
        (kind, *payload) = tasks.pop()
        if kind == 0:
            (left, right) = payload
            n = len(left)
            if n == 1:
                results.append([0])
                continue
            half = n >> 1
            inverse = [0] * n
            for (index, value) in enumerate(left):
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
            (n, right, lower_values, upper_values) = payload
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
            (lower_i, lower_j) = (n, -1)
            (upper_i, upper_j) = (n, -1)
            lower_delta = upper_delta = 0
            while not (lower_i < 0 and upper_j >= n):
                if lower_delta > 0:
                    lower_j += 1
                    if lower_j < n and upper[lower_j] != infinity and (upper[lower_j] < lower_i):
                        lower_delta -= 1
                    if lower_j < n and lower[lower_j] != infinity and (lower[lower_j] >= lower_i):
                        lower_delta -= 1
                else:
                    lower_i -= 1
                    if lower_i >= 0 and inverse_upper[lower_i] != infinity and (inverse_upper[lower_i] <= lower_j):
                        lower_delta += 1
                    if lower_i >= 0 and inverse_lower[lower_i] != infinity and (inverse_lower[lower_i] > lower_j):
                        lower_delta += 1
                if 0 <= lower_j < n and lower[lower_j] != infinity and (lower[lower_j] <= lower_i):
                    result[lower_j] = lower[lower_j]
                if upper_delta >= 0:
                    upper_j += 1
                    if upper_j < n and upper[upper_j] != infinity and (upper[upper_j] < upper_i):
                        upper_delta -= 1
                    if upper_j < n and lower[upper_j] != infinity and (lower[upper_j] >= upper_i):
                        upper_delta -= 1
                else:
                    upper_i -= 1
                    if upper_i >= 0 and inverse_upper[upper_i] != infinity and (inverse_upper[upper_i] <= upper_j):
                        upper_delta += 1
                    if upper_i >= 0 and inverse_lower[upper_i] != infinity and (inverse_lower[upper_i] > upper_j):
                        upper_delta += 1
                if 0 <= upper_j < n and upper[upper_j] != infinity and (upper[upper_j] >= upper_i):
                    result[upper_j] = upper[upper_j]
                if 0 <= lower_j < n and lower_i == upper_i and (lower_j == upper_j):
                    result[lower_j] = lower_i
            results.append(result)
    return results[0]

def _segment_tree_range_lis_seaweed(permutation):
    results = []
    tasks = [(0, permutation)]
    while tasks:
        (kind, *payload) = tasks.pop()
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
            for (index, value) in enumerate(values):
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
            (values, lower_positions, upper_positions) = payload
            upper_result = results.pop()
            lower_result = results.pop()
            n = len(values)
            infinity = n
            first = list(range(n))
            second = list(range(n))
            lower_index = upper_index = 0
            for (index, value) in enumerate(values):
                if value < n // 2:
                    mapped = lower_result[lower_index]
                    first[index] = infinity if mapped == n // 2 else lower_positions[mapped]
                    lower_index += 1
                else:
                    mapped = upper_result[upper_index]
                    second[index] = infinity if mapped == n - n // 2 else upper_positions[mapped]
                    upper_index += 1
            a = [infinity] * n
            reverse_first = [infinity] * n
            for (index, value) in enumerate(first):
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
            for (index, value) in enumerate(second):
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
            results.append(_segment_tree_range_lis_squaredot(payload[0], payload[1]))
        else:
            (n, to_source, to_target) = payload
            composed = results.pop()
            infinity = n
            result = [infinity] * n
            for index in range(n):
                if to_target[index] != infinity and to_source[composed[index]] != infinity:
                    result[to_target[index]] = to_source[composed[index]]
            results.append(result)
    return results[0]

class RangeLIS:
    __slots__ = ('length', 'size', 'matrix')

    def __init__(self, sequence):
        self.length = len(sequence)
        size = 1
        while size < len(sequence):
            size <<= 1
        self.size = size
        order = list(range(len(sequence) - 1, -1, -1))
        order.sort(key=sequence.__getitem__)
        permutation = [0] * size
        for (rank, position) in enumerate(order):
            permutation[position] = rank
        for position in range(len(sequence), size):
            permutation[position] = position
        table = _segment_tree_range_lis_seaweed(permutation) if size else []
        self.matrix = WaveletMatrix(table)

    def query(self, left, right):
        if not 0 <= left <= right <= self.length:
            raise IndexError('invalid half-open range')
        if left == right:
            return 0
        greater_equal = self.matrix.range_freq(0, right, left, self.size)
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
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    table = RangeLIS(list(map(int, read().split())))
    result = []
    for _ in range(q):
        (left, right) = map(int, read().split())
        result.append(str(table.query(left, right)))
    sys.stdout.write('\n'.join(result))
if __name__ == '__main__':
    main()
