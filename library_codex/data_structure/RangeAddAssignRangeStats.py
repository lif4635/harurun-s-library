"""整数列の区間加算・代入と区間sum/min/maxを扱う専用lazy tree。"""

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
