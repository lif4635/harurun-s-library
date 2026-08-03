"""二次元gridの一点加算と半開矩形和を扱うFenwick Tree。"""

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
