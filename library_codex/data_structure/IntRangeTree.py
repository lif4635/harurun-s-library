"""Callback-free iterative lazy segment trees for common integer workloads."""


INF = float("inf")


class RangeAddAssignRangeStats:
    """Range add/assign with range sum/minimum/maximum queries."""

    __slots__ = (
        "n", "size", "log", "sum", "minimum", "maximum", "length",
        "lazy_add", "lazy_assign",
    )

    def __init__(self, values):
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            n = values
            values = [0] * n
        else:
            values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        count = size << 1
        total = [0] * count
        minimum = [INF] * count
        maximum = [-INF] * count
        length = [0] * count
        total[size:size + n] = values
        minimum[size:size + n] = values
        maximum[size:size + n] = values
        for node in range(size, size + n):
            length[node] = 1
        for node in range(size - 1, 0, -1):
            left = node << 1
            right = left | 1
            total[node] = total[left] + total[right]
            minimum[node] = min(minimum[left], minimum[right])
            maximum[node] = max(maximum[left], maximum[right])
            length[node] = length[left] + length[right]
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.sum = total
        self.minimum = minimum
        self.maximum = maximum
        self.length = length
        self.lazy_add = [0] * size
        self.lazy_assign = [None] * size

    def _pull(self, node):
        left = node << 1
        right = left | 1
        self.sum[node] = self.sum[left] + self.sum[right]
        self.minimum[node] = min(self.minimum[left], self.minimum[right])
        self.maximum[node] = max(self.maximum[left], self.maximum[right])

    def _apply_add(self, node, value):
        length = self.length[node]
        if not length:
            return
        self.sum[node] += value * length
        self.minimum[node] += value
        self.maximum[node] += value
        if node < self.size:
            assigned = self.lazy_assign[node]
            if assigned is None:
                self.lazy_add[node] += value
            else:
                self.lazy_assign[node] = assigned + value

    def _apply_assign(self, node, value):
        length = self.length[node]
        if not length:
            return
        self.sum[node] = value * length
        self.minimum[node] = value
        self.maximum[node] = value
        if node < self.size:
            self.lazy_assign[node] = value
            self.lazy_add[node] = 0

    def _push(self, node):
        assigned = self.lazy_assign[node]
        if assigned is not None:
            self._apply_assign(node << 1, assigned)
            self._apply_assign(node << 1 | 1, assigned)
            self.lazy_assign[node] = None
        added = self.lazy_add[node]
        if added:
            self._apply_add(node << 1, added)
            self._apply_add(node << 1 | 1, added)
            self.lazy_add[node] = 0

    def _prepare(self, left, right):
        for shift in range(self.log, 0, -1):
            if left >> shift << shift != left:
                self._push(left >> shift)
            if right >> shift << shift != right:
                self._push((right - 1) >> shift)

    def _rebuild(self, left, right):
        for shift in range(1, self.log + 1):
            if left >> shift << shift != left:
                self._pull(left >> shift)
            if right >> shift << shift != right:
                self._pull((right - 1) >> shift)

    def _range_apply(self, left, right, value, assign):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return
        left += self.size
        right += self.size
        self._prepare(left, right)
        original_left = left
        original_right = right
        if assign:
            while left < right:
                if left & 1:
                    self._apply_assign(left, value)
                    left += 1
                if right & 1:
                    right -= 1
                    self._apply_assign(right, value)
                left >>= 1
                right >>= 1
        else:
            while left < right:
                if left & 1:
                    self._apply_add(left, value)
                    left += 1
                if right & 1:
                    right -= 1
                    self._apply_add(right, value)
                left >>= 1
                right >>= 1
        self._rebuild(original_left, original_right)

    def range_add(self, left, right, value):
        self._range_apply(left, right, value, False)

    add = range_add

    def range_assign(self, left, right, value):
        self._range_apply(left, right, value, True)

    range_update = range_assign

    def _range_query(self, left, right, command):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return 0 if command == 0 else (INF if command == 1 else -INF)
        left += self.size
        right += self.size
        self._prepare(left, right)
        if command == 0:
            result = 0
            data = self.sum
            while left < right:
                if left & 1:
                    result += data[left]
                    left += 1
                if right & 1:
                    right -= 1
                    result += data[right]
                left >>= 1
                right >>= 1
            return result
        if command == 1:
            result = INF
            data = self.minimum
            while left < right:
                if left & 1:
                    result = min(result, data[left])
                    left += 1
                if right & 1:
                    right -= 1
                    result = min(result, data[right])
                left >>= 1
                right >>= 1
            return result
        result = -INF
        data = self.maximum
        while left < right:
            if left & 1:
                result = max(result, data[left])
                left += 1
            if right & 1:
                right -= 1
                result = max(result, data[right])
            left >>= 1
            right >>= 1
        return result

    def range_sum(self, left, right):
        return self._range_query(left, right, 0)

    query_sum = range_sum

    def range_min(self, left, right):
        return self._range_query(left, right, 1)

    query_min = range_min

    def range_max(self, left, right):
        return self._range_query(left, right, 2)

    query_max = range_max

    def get(self, index):
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        node = index + self.size
        for shift in range(self.log, 0, -1):
            self._push(node >> shift)
        return self.sum[node]

    def set(self, index, value):
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        self.range_assign(index, index + 1, value)

    def all_sum(self):
        return self.sum[1]

    def all_min(self):
        return self.minimum[1]

    def all_max(self):
        return self.maximum[1]

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)

    def __len__(self):
        return self.n


class RangeAffineRangeSum:
    """Range ``x = multiplier*x + addend`` and range-sum queries."""

    __slots__ = (
        "n", "size", "log", "sum", "length", "lazy_multiplier",
        "lazy_addend", "mod",
    )

    def __init__(self, values, mod=None):
        if mod is not None and mod <= 0:
            raise ValueError("modulus must be positive")
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            n = values
            values = [0] * n
        else:
            values = list(values)
            n = len(values)
        if mod is not None:
            values = [value % mod for value in values]
        size = 1 << (n - 1).bit_length() if n else 1
        count = size << 1
        total = [0] * count
        length = [0] * count
        total[size:size + n] = values
        for node in range(size, size + n):
            length[node] = 1
        for node in range(size - 1, 0, -1):
            total[node] = total[node << 1] + total[node << 1 | 1]
            if mod is not None:
                total[node] %= mod
            length[node] = length[node << 1] + length[node << 1 | 1]
        self.n = n
        self.size = size
        self.log = size.bit_length() - 1
        self.sum = total
        self.length = length
        self.lazy_multiplier = [1] * size
        self.lazy_addend = [0] * size
        self.mod = mod

    def _pull(self, node):
        value = self.sum[node << 1] + self.sum[node << 1 | 1]
        if self.mod is not None:
            value %= self.mod
        self.sum[node] = value

    def _apply(self, node, multiplier, addend):
        mod = self.mod
        value = multiplier * self.sum[node] + addend * self.length[node]
        if mod is not None:
            value %= mod
        self.sum[node] = value
        if node < self.size:
            lazy_multiplier = multiplier * self.lazy_multiplier[node]
            lazy_addend = multiplier * self.lazy_addend[node] + addend
            if mod is not None:
                lazy_multiplier %= mod
                lazy_addend %= mod
            self.lazy_multiplier[node] = lazy_multiplier
            self.lazy_addend[node] = lazy_addend

    def _push(self, node):
        multiplier = self.lazy_multiplier[node]
        addend = self.lazy_addend[node]
        if multiplier != 1 or addend:
            self._apply(node << 1, multiplier, addend)
            self._apply(node << 1 | 1, multiplier, addend)
            self.lazy_multiplier[node] = 1
            self.lazy_addend[node] = 0

    def _prepare(self, left, right):
        for shift in range(self.log, 0, -1):
            if left >> shift << shift != left:
                self._push(left >> shift)
            if right >> shift << shift != right:
                self._push((right - 1) >> shift)

    def apply(self, left, right, multiplier, addend):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return
        mod = self.mod
        if mod is not None:
            multiplier %= mod
            addend %= mod
        left += self.size
        right += self.size
        self._prepare(left, right)
        original_left = left
        original_right = right
        while left < right:
            if left & 1:
                self._apply(left, multiplier, addend)
                left += 1
            if right & 1:
                right -= 1
                self._apply(right, multiplier, addend)
            left >>= 1
            right >>= 1
        for shift in range(1, self.log + 1):
            if original_left >> shift << shift != original_left:
                self._pull(original_left >> shift)
            if original_right >> shift << shift != original_right:
                self._pull((original_right - 1) >> shift)

    range_affine = apply

    def range_add(self, left, right, value):
        self.apply(left, right, 1, value)

    def range_multiply(self, left, right, value):
        self.apply(left, right, value, 0)

    def range_sum(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        if left == right:
            return 0
        left += self.size
        right += self.size
        self._prepare(left, right)
        result = 0
        data = self.sum
        while left < right:
            if left & 1:
                result += data[left]
                left += 1
            if right & 1:
                right -= 1
                result += data[right]
            left >>= 1
            right >>= 1
        return result if self.mod is None else result % self.mod

    query = range_sum
    prod = range_sum

    def get(self, index):
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        return self.range_sum(index, index + 1)

    def set(self, index, value):
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        self.apply(index, index + 1, 0, value)

    def all_sum(self):
        return self.sum[1]

    def __getitem__(self, index):
        return self.get(index)

    def __setitem__(self, index, value):
        self.set(index, value)

    def __len__(self):
        return self.n


IntLazySegmentTree = RangeAddAssignRangeStats
AffineLazySegmentTree = RangeAffineRangeSum

