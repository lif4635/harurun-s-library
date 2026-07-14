class FenwickTree:
    __slots__ = ("n", "bit")

    def __init__(self, values):
        if isinstance(values, int):
            if values < 0:
                raise ValueError("size must be nonnegative")
            self.n = values
            self.bit = [0] * (values + 1)
        else:
            values = list(values)
            n = len(values)
            bit = [0] + values
            for index in range(1, n + 1):
                parent = index + (index & -index)
                if parent <= n:
                    bit[parent] += bit[index]
            self.n = n
            self.bit = bit

    def add(self, index, value):
        index += 1
        bit = self.bit
        while index <= self.n:
            bit[index] += value
            index += index & -index

    def prefix_sum(self, right):
        result = 0
        bit = self.bit
        while right:
            result += bit[right]
            right &= right - 1
        return result

    sum0 = prefix_sum

    def sum(self, left, right=None):
        if right is None:
            return self.prefix_sum(left)
        return self.prefix_sum(right) - self.prefix_sum(left)

    prod = sum

    def get(self, index):
        return self.sum(index, index + 1)

    def set(self, index, value):
        self.add(index, value - self.get(index))

    def lower_bound(self, target):
        if target <= 0:
            return 0
        index = 0
        step = 1 << (self.n.bit_length() - 1) if self.n else 0
        bit = self.bit
        while step:
            next_index = index + step
            if next_index <= self.n and bit[next_index] < target:
                target -= bit[next_index]
                index = next_index
            step >>= 1
        return index if index < self.n else self.n

    bisect_left = lower_bound

    def __len__(self):
        return self.n


class RangeAddRangeSum:
    __slots__ = ("n", "first", "second")

    def __init__(self, values):
        if isinstance(values, int):
            n = values
            values = None
        else:
            values = list(values)
            n = len(values)
        self.n = n
        self.first = FenwickTree(n + 1)
        self.second = FenwickTree(n + 1)
        if values is not None:
            previous = 0
            for index, value in enumerate(values):
                delta = value - previous
                self.first.add(index, delta)
                self.second.add(index, delta * index)
                previous = value

    def add(self, left, right, value):
        if left >= right:
            return
        self.first.add(left, value)
        self.first.add(right, -value)
        self.second.add(left, value * left)
        self.second.add(right, -value * right)

    range_add = add

    def prefix_sum(self, right):
        return (
            self.first.prefix_sum(right) * right
            - self.second.prefix_sum(right)
        )

    def sum(self, left, right):
        return self.prefix_sum(right) - self.prefix_sum(left)

    prod = sum

    def get(self, index):
        return self.sum(index, index + 1)


class DynamicFenwickTree:
    __slots__ = ("n", "bit")

    def __init__(self, size):
        if size < 0:
            raise ValueError("size must be nonnegative")
        self.n = size
        self.bit = {}

    def add(self, index, value):
        index += 1
        bit = self.bit
        n = self.n
        while index <= n:
            next_value = bit.get(index, 0) + value
            if next_value:
                bit[index] = next_value
            elif index in bit:
                del bit[index]
            index += index & -index

    def prefix_sum(self, right):
        result = 0
        bit = self.bit
        while right:
            result += bit.get(right, 0)
            right &= right - 1
        return result

    def sum(self, left, right):
        return self.prefix_sum(right) - self.prefix_sum(left)

    prod = sum


class FenwickTree2D:
    __slots__ = ("height", "width", "bit")

    def __init__(self, height, width):
        if height < 0 or width < 0:
            raise ValueError("dimensions must be nonnegative")
        self.height = height
        self.width = width
        self.bit = [[0] * (width + 1) for _ in range(height + 1)]

    def add(self, row, column, value):
        i = row + 1
        height = self.height
        width = self.width
        bit = self.bit
        while i <= height:
            line = bit[i]
            j = column + 1
            while j <= width:
                line[j] += value
                j += j & -j
            i += i & -i

    def prefix_sum(self, bottom, right):
        result = 0
        bit = self.bit
        i = bottom
        while i:
            line = bit[i]
            j = right
            while j:
                result += line[j]
                j &= j - 1
            i &= i - 1
        return result

    def sum(self, top, left, bottom, right):
        return (
            self.prefix_sum(bottom, right)
            - self.prefix_sum(top, right)
            - self.prefix_sum(bottom, left)
            + self.prefix_sum(top, left)
        )

    prod = sum
