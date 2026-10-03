class StaticRMQ:
    __slots__ = ('n', 'block_size', 'block_shift', 'block_mask', 'values', 'masks', 'prefix_min', 'suffix_min', 'table')

    def __init__(self, values):
        values = list(values)
        n = len(values)
        logn = max(1, n.bit_length())
        block_size = 1 << (logn - 1).bit_length()
        block_shift = block_size.bit_length() - 1
        masks = [0] * n
        prefix_min = [0] * n
        suffix_min = [0] * n
        block_min = []
        for left in range(0, n, block_size):
            right = min(left + block_size, n)
            mask = 0
            best = left
            for i in range(left, right):
                x = values[i]
                while mask:
                    top = mask.bit_length() - 1
                    if values[left + top] <= x:
                        break
                    mask ^= 1 << top
                mask |= 1 << i - left
                masks[i] = mask
                if values[i] < values[best]:
                    best = i
                prefix_min[i] = best
            block_min.append(best)
            best = right - 1
            for i in range(right - 1, left - 1, -1):
                if values[i] <= values[best]:
                    best = i
                suffix_min[i] = best
        table = []
        if block_min:
            table.append(block_min)
            width = 2
            while width <= len(block_min):
                half = width >> 1
                prev = table[-1]
                cur = [0] * (len(block_min) - width + 1)
                for i in range(len(cur)):
                    x = prev[i]
                    y = prev[i + half]
                    cur[i] = x if values[x] <= values[y] else y
                table.append(cur)
                width <<= 1
        self.n = n
        self.block_size = block_size
        self.block_shift = block_shift
        self.block_mask = block_size - 1
        self.values = values
        self.masks = masks
        self.prefix_min = prefix_min
        self.suffix_min = suffix_min
        self.table = table

    def _small_argmin(self, l, r):
        base = l >> self.block_shift << self.block_shift
        mask = self.masks[r - 1] & ~((1 << (l & self.block_mask)) - 1)
        return base + ((mask & -mask).bit_length() - 1)

    def argmin(self, l, r):
        assert 0 <= l < r <= self.n
        shift = self.block_shift
        left_block = l >> shift
        right_block = r - 1 >> shift
        if left_block == right_block:
            return self._small_argmin(l, r)
        best = self.suffix_min[l]
        first = left_block + 1
        last = right_block
        if first < last:
            level = (last - first).bit_length() - 1
            width = 1 << level
            table = self.table[level]
            x = table[first]
            y = table[last - width]
            middle = x if self.values[x] <= self.values[y] else y
            if self.values[middle] < self.values[best]:
                best = middle
        right = self.prefix_min[r - 1]
        if self.values[right] < self.values[best]:
            best = right
        return best

    def query(self, l, r):
        return self.values[self.argmin(l, r)]
    prod = query

    def __len__(self):
        return self.n

def _string_suffix_array_sa_naive(sequence):
    return sorted(range(len(sequence)), key=lambda i: sequence[i:])

def _string_suffix_array_sa_doubling(sequence):
    n = len(sequence)
    suffix_array = list(range(n))
    rank = list(sequence)
    temporary = [0] * n
    length = 1
    while length < n:
        suffix_array.sort(key=lambda i: (rank[i], rank[i + length] if i + length < n else -1))
        temporary[suffix_array[0]] = 0
        classes = 0
        previous = suffix_array[0]
        for current in suffix_array[1:]:
            if rank[previous] != rank[current] or (rank[previous + length] if previous + length < n else -1) != (rank[current + length] if current + length < n else -1):
                classes += 1
            temporary[current] = classes
            previous = current
        (rank, temporary) = (temporary, rank)
        if classes == n - 1:
            break
        length <<= 1
    return suffix_array

def _string_suffix_array_induce(sequence, is_s, sum_l, sum_s, lms):
    n = len(sequence)
    suffix_array = [-1] * n
    bucket = sum_s.copy()
    for position in lms:
        if position != n:
            symbol = sequence[position]
            suffix_array[bucket[symbol]] = position
            bucket[symbol] += 1
    bucket = sum_l.copy()
    symbol = sequence[n - 1]
    suffix_array[bucket[symbol]] = n - 1
    bucket[symbol] += 1
    for i in range(n):
        position = suffix_array[i]
        if position >= 1 and (not is_s[position - 1]):
            position -= 1
            symbol = sequence[position]
            suffix_array[bucket[symbol]] = position
            bucket[symbol] += 1
    bucket = sum_l.copy()
    for i in range(n - 1, -1, -1):
        position = suffix_array[i]
        if position >= 1 and is_s[position - 1]:
            position -= 1
            symbol = sequence[position] + 1
            bucket[symbol] -= 1
            suffix_array[bucket[symbol]] = position
    return suffix_array

def sa_is(sequence, upper):
    sequence = list(sequence)
    assert upper >= 0 and all((0 <= symbol <= upper for symbol in sequence))
    frames = []
    current = sequence
    current_upper = upper
    while True:
        n = len(current)
        if n == 0:
            result = []
        elif n == 1:
            result = [0]
        elif n == 2:
            result = [0, 1] if current[0] < current[1] else [1, 0]
        elif n < 10:
            result = _string_suffix_array_sa_naive(current)
        elif n < 40:
            result = _string_suffix_array_sa_doubling(current)
        else:
            is_s = [False] * n
            for i in range(n - 2, -1, -1):
                is_s[i] = is_s[i + 1] if current[i] == current[i + 1] else current[i] < current[i + 1]
            sum_l = [0] * (current_upper + 1)
            sum_s = [0] * (current_upper + 1)
            for i in range(n):
                if is_s[i]:
                    sum_l[current[i] + 1] += 1
                else:
                    sum_s[current[i]] += 1
            for i in range(current_upper + 1):
                sum_s[i] += sum_l[i]
                if i < current_upper:
                    sum_l[i + 1] += sum_s[i]
            lms_map = [-1] * (n + 1)
            lms = []
            for i in range(1, n):
                if not is_s[i - 1] and is_s[i]:
                    lms_map[i] = len(lms)
                    lms.append(i)
            result = _string_suffix_array_induce(current, is_s, sum_l, sum_s, lms)
            m = len(lms)
            if m:
                sorted_lms = [position for position in result if lms_map[position] != -1]
                reduced = [0] * m
                reduced_upper = 0
                reduced[lms_map[sorted_lms[0]]] = 0
                for i in range(1, m):
                    left = sorted_lms[i - 1]
                    right = sorted_lms[i]
                    left_index = lms_map[left]
                    right_index = lms_map[right]
                    left_end = lms[left_index + 1] if left_index + 1 < m else n
                    right_end = lms[right_index + 1] if right_index + 1 < m else n
                    same = left_end - left == right_end - right
                    if same:
                        while left < left_end and current[left] == current[right]:
                            left += 1
                            right += 1
                        if left == n or current[left] != current[right]:
                            same = False
                    if not same:
                        reduced_upper += 1
                    reduced[lms_map[sorted_lms[i]]] = reduced_upper
                if reduced_upper + 1 == m:
                    reduced_sa = [0] * m
                    for (i, value) in enumerate(reduced):
                        reduced_sa[value] = i
                    sorted_lms = [lms[i] for i in reduced_sa]
                    result = _string_suffix_array_induce(current, is_s, sum_l, sum_s, sorted_lms)
                else:
                    frames.append((current, is_s, sum_l, sum_s, lms))
                    current = reduced
                    current_upper = reduced_upper
                    continue
        while frames:
            (previous, is_s, sum_l, sum_s, lms) = frames.pop()
            sorted_lms = [lms[i] for i in result]
            result = _string_suffix_array_induce(previous, is_s, sum_l, sum_s, sorted_lms)
        return result

def _string_suffix_array_compress(sequence):
    values = sorted(set(sequence))
    index = {value: i for (i, value) in enumerate(values)}
    return ([index[value] for value in sequence], len(values) - 1)

def suffix_array(sequence, upper=None):
    if isinstance(sequence, str):
        converted = list(map(ord, sequence))
        if not converted:
            return []
        maximum = max(converted)
        if maximum <= 255:
            return sa_is(converted, 255)
        (converted, maximum) = _string_suffix_array_compress(converted)
        return sa_is(converted, maximum)
    if isinstance(sequence, (bytes, bytearray)):
        return sa_is(sequence, 255)
    sequence = list(sequence)
    if not sequence:
        return []
    if upper is not None:
        return sa_is(sequence, upper)
    (converted, maximum) = _string_suffix_array_compress(sequence)
    return sa_is(converted, maximum)

def suffix_array_with_empty(sequence, upper=None):
    return [len(sequence)] + suffix_array(sequence, upper)

def lcp_array(sequence, suffix_array):
    n = len(sequence)
    assert len(suffix_array) == n
    if n == 0:
        return []
    rank = [0] * n
    for (i, suffix) in enumerate(suffix_array):
        rank[suffix] = i
    lcp = [0] * (n - 1)
    height = 0
    for i in range(n):
        if height:
            height -= 1
        position = rank[i]
        if position == 0:
            continue
        j = suffix_array[position - 1]
        while i + height < n and j + height < n and (sequence[i + height] == sequence[j + height]):
            height += 1
        lcp[position - 1] = height
    return lcp

class SuffixArray:
    __slots__ = ('sequence', 's', 'n', 'sa', 'SA', 'rank', 'RSA', 'lcp', 'LCP', '_rmq')

    def __init__(self, sequence, upper=None):
        self.sequence = sequence
        self.s = sequence
        self.n = len(sequence)
        suffixes = suffix_array(sequence, upper)
        rank = [0] * self.n
        for (i, suffix) in enumerate(suffixes):
            rank[suffix] = i
        lcp = lcp_array(sequence, suffixes)
        self.sa = suffixes
        self.SA = suffixes
        self.rank = rank
        self.RSA = rank
        self.lcp = lcp
        self.LCP = lcp
        self._rmq = None

    def __len__(self):
        return self.n

    def __getitem__(self, index):
        return self.sa[index]

    def with_empty(self):
        return [self.n] + self.sa

    def _ensure_rmq(self):
        rmq = self._rmq
        if rmq is None:
            rmq = StaticRMQ(self.lcp)
            self._rmq = rmq
        return rmq

    def lcp_suffix(self, i, j):
        assert 0 <= i < self.n and 0 <= j < self.n
        if i == j:
            return self.n - i
        left = self.rank[i]
        right = self.rank[j]
        if left > right:
            (left, right) = (right, left)
        return self._ensure_rmq().query(left, right)
    longest_common_prefix = lcp_suffix

    def lcp_substring(self, left1, right1, left2, right2):
        assert 0 <= left1 <= right1 <= self.n
        assert 0 <= left2 <= right2 <= self.n
        limit = min(right1 - left1, right2 - left2)
        if limit == 0:
            return 0
        value = self.lcp_suffix(left1, left2)
        return value if value < limit else limit

    def compare_suffix(self, i, j):
        assert 0 <= i < self.n and 0 <= j < self.n
        if i == j:
            return 0
        return -1 if self.rank[i] < self.rank[j] else 1

    def compare_substring(self, left1, right1, left2, right2):
        common = self.lcp_substring(left1, right1, left2, right2)
        end1 = left1 + common == right1
        end2 = left2 + common == right2
        if end1:
            return 0 if end2 else -1
        if end2:
            return 1
        return -1 if self.sequence[left1 + common] < self.sequence[left2 + common] else 1

    def _compare_pattern(self, suffix, pattern, common):
        sequence = self.sequence
        n = self.n
        m = len(pattern)
        i = suffix + common
        j = common
        while i < n and j < m and (sequence[i] == pattern[j]):
            i += 1
            j += 1
        if j == m:
            return (0, j)
        if i == n or sequence[i] < pattern[j]:
            return (-1, j)
        return (1, j)

    def _bound(self, pattern, upper):
        left = -1
        right = self.n
        left_lcp = 0
        right_lcp = 0
        suffixes = self.sa
        while right - left > 1:
            middle = left + right >> 1
            common = left_lcp if left_lcp < right_lcp else right_lcp
            (comparison, matched) = self._compare_pattern(suffixes[middle], pattern, common)
            if comparison < 0 or (upper and comparison == 0):
                left = middle
                left_lcp = matched
            else:
                right = middle
                right_lcp = matched
        return right

    def search(self, pattern):
        if not hasattr(pattern, '__len__'):
            pattern = list(pattern)
        return (self._bound(pattern, False), self._bound(pattern, True))
    find_range = search

    def count(self, pattern):
        (left, right) = self.search(pattern)
        return right - left

    def occurrences(self, pattern, sort_positions=False):
        (left, right) = self.search(pattern)
        result = self.sa[left:right]
        return sorted(result) if sort_positions else result

    def distinct_substrings(self):
        n = self.n
        return n * (n + 1) // 2 - sum(self.lcp)
    number_of_substrings = distinct_substrings

    def substring(self, left=0, right=None):
        if right is None:
            right = self.n
        assert 0 <= left <= right <= self.n
        return StaticSubstring(self, left, right)

class StaticSubstring:
    __slots__ = ('base', 'left', 'right', 'l', 'r')

    def __init__(self, base, left, right):
        self.base = base
        self.left = left
        self.right = right
        self.l = left
        self.r = right

    def __len__(self):
        return self.right - self.left

    def __getitem__(self, index):
        if isinstance(index, slice):
            (start, stop, step) = index.indices(len(self))
            if step != 1:
                return self.base.sequence[self.left:self.right][index]
            return StaticSubstring(self.base, self.left + start, self.left + stop)
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError('substring index out of range')
        return self.base.sequence[self.left + index]

    def __str__(self):
        return str(self.base.sequence[self.left:self.right])

    def lcp(self, other):
        assert self.base is other.base
        return self.base.lcp_substring(self.left, self.right, other.left, other.right)

    def compare(self, other):
        assert self.base is other.base
        return self.base.compare_substring(self.left, self.right, other.left, other.right)
    cmp = compare

    def startswith(self, other):
        return len(self) >= len(other) and self.lcp(other) == len(other)
    starts_with = startswith

    def __eq__(self, other):
        return isinstance(other, StaticSubstring) and self.base is other.base and (self.compare(other) == 0)

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0
import sys
print(*suffix_array(sys.stdin.buffer.readline().strip()))
