"""事前に与えた疎な座標だけを保持する二次元Fenwick Tree。"""

from bisect import bisect_left

class CompressedFenwick2D:
    """Point add / rectangle sum; every update coordinate is preregistered."""

    __slots__ = ("xs", "ys", "bit")

    def __init__(self, points):
        points = list(points)
        xs = sorted(set(x for x, _ in points))
        ys = [[] for _ in range(len(xs) + 1)]
        for x, y in points:
            index = bisect_left(xs, x) + 1
            while index <= len(xs):
                ys[index].append(y)
                index += index & -index
        for index in range(1, len(ys)):
            ys[index] = sorted(set(ys[index]))
        self.xs = xs
        self.ys = ys
        self.bit = [[0] * (len(row) + 1) for row in ys]

    def add(self, x, y, value):
        x_index = bisect_left(self.xs, x)
        if x_index == len(self.xs) or self.xs[x_index] != x:
            raise KeyError("update coordinate was not registered")
        x_index += 1
        while x_index <= len(self.xs):
            row_coordinates = self.ys[x_index]
            y_index = bisect_left(row_coordinates, y)
            if y_index == len(row_coordinates) or row_coordinates[y_index] != y:
                raise KeyError("update coordinate was not registered")
            y_index += 1
            row = self.bit[x_index]
            while y_index < len(row):
                row[y_index] += value
                y_index += y_index & -y_index
            x_index += x_index & -x_index

    def prefix_sum(self, x, y):
        x_index = bisect_left(self.xs, x)
        result = 0
        while x_index:
            y_index = bisect_left(self.ys[x_index], y)
            row = self.bit[x_index]
            while y_index:
                result += row[y_index]
                y_index &= y_index - 1
            x_index &= x_index - 1
        return result

    def sum(self, left, bottom, right, top):
        return (
            self.prefix_sum(right, top)
            - self.prefix_sum(left, top)
            - self.prefix_sum(right, bottom)
            + self.prefix_sum(left, bottom)
        )

    prod = sum
