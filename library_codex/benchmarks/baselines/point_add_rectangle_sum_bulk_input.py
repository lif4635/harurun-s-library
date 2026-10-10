"""事前に与えた疎な座標だけを保持する二次元Fenwick Tree。"""
from bisect import bisect_left

class CompressedFenwick2D:
    """Point add / rectangle sum; every update coordinate is preregistered."""
    __slots__ = ('xs', 'ys', 'bit', '_points')

    def __init__(self, points):
        points = {(x, y) for (x, y) in points}
        xs = sorted(set((x for (x, _) in points)))
        ranks = {x: i + 1 for (i, x) in enumerate(xs)}
        self._points = {(x, y): ranks[x] for (x, y) in points}
        ys = [[] for _ in range(len(xs) + 1)]
        for (y, x) in sorted(((y, x) for (x, y) in points)):
            index = ranks[x]
            while index <= len(xs):
                row = ys[index]
                if not row or row[-1] != y:
                    row.append(y)
                index += index & -index
        self.xs = xs
        self.ys = ys
        self.bit = [[0] * (len(row) + 1) for row in ys]

    def add(self, x, y, value):
        x_index = self._points[x, y]
        while x_index <= len(self.xs):
            row_coordinates = self.ys[x_index]
            y_index = bisect_left(row_coordinates, y) + 1
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
        if left >= right or bottom >= top:
            return 0
        left = bisect_left(self.xs, left)
        right = bisect_left(self.xs, right)
        result = 0
        while left != right:
            if left < right:
                index = right
                right &= right - 1
                sign = 1
            else:
                index = left
                left &= left - 1
                sign = -1
            coordinates = self.ys[index]
            low = bisect_left(coordinates, bottom)
            high = bisect_left(coordinates, top)
            row = self.bit[index]
            total = 0
            while low != high:
                if low < high:
                    total += row[high]
                    high &= high - 1
                else:
                    total -= row[low]
                    low &= low - 1
            result += sign * total
        return result
    prod = sum
'点の重み追加と矩形和queryが混ざる列をofflineで処理する。'

class DynamicPointAddRectangleSum:
    __slots__ = ('operations',)

    def __init__(self):
        self.operations = []

    def add(self, x, y, value):
        self.operations.append((0, x, y, value))

    def query(self, left, bottom, right, top):
        self.operations.append((1, left, bottom, right, top))

    def solve(self):
        points = [(op[1], op[2]) for op in self.operations if op[0] == 0]
        fenwick = CompressedFenwick2D(points)
        result = []
        for operation in self.operations:
            if operation[0] == 0:
                fenwick.add(operation[1], operation[2], operation[3])
            else:
                result.append(fenwick.sum(*operation[1:]))
        return result
    run = solve
import sys

def main():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n = next(data)
    q = next(data)
    solver = DynamicPointAddRectangleSum()
    for _ in range(n):
        solver.add(next(data), next(data), next(data))
    for _ in range(q):
        if next(data) == 0:
            solver.add(next(data), next(data), next(data))
        else:
            solver.query(next(data), next(data), next(data), next(data))
    sys.stdout.write('\n'.join(map(str, solver.solve())))
if __name__ == '__main__':
    main()
