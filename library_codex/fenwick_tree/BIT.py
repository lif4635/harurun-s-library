"""一点加算・prefix和・区間和を対数時間で扱うBIT。"""

class BIT:
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
        """a[index]へvalueを加える。"""
        index += 1
        bit = self.bit
        while index <= self.n:
            bit[index] += value
            index += index & -index

    def prefix_sum(self, right):
        """半開区間[0, right)の和を返す。"""
        result = 0
        bit = self.bit
        while right:
            result += bit[right]
            right &= right - 1
        return result

    def sum(self, left, right=None):
        """[left, right)の和を返す。right省略時は[0, left)の和。"""
        if right is None:
            return self.prefix_sum(left)
        return self.prefix_sum(right) - self.prefix_sum(left)

    def get(self, index):
        """a[index]を返す。"""
        return self.sum(index, index + 1)

    def set(self, index, value):
        """a[index]をvalueへ置き換える。"""
        self.add(index, value - self.get(index))

    def lower_bound(self, target):
        """prefix和がtarget以上になる最小の右端を返す。"""
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

    def __len__(self):
        return self.n

    def tolist(self):
        """現在の要素列をlistで返す。O(N)。"""
        values = self.bit[1:]
        for index in range(self.n, 0, -1):
            parent = index + (index & -index)
            if parent <= self.n:
                values[parent - 1] -= values[index - 1]
        return values

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "BIT(%r)" % self.tolist()
