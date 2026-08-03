"""整数列の区間affine変換と区間和を扱う専用lazy tree。"""

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
