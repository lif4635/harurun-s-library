"""巨大な添字範囲で触れたnodeだけを持つ疎なFenwick Tree。"""

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
