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
'長方形へ加算し、事前登録した点の現在値を求める。'
from bisect import bisect_left as _spatial_structure_rectangle_add_point_get_bisect_left

class RectangleAddPointGet:
    __slots__ = ('_fenwick',)

    def __init__(self, points):
        self._fenwick = CompressedFenwick2D(points)

    def add(self, left, bottom, right, top, value):
        """[left, right) × [bottom, top) の登録点へvalueを加える。"""
        if left >= right or bottom >= top:
            return
        fenwick = self._fenwick
        left = _spatial_structure_rectangle_add_point_get_bisect_left(fenwick.xs, left)
        right = _spatial_structure_rectangle_add_point_get_bisect_left(fenwick.xs, right)
        while left != right:
            if left < right:
                index = right
                right &= right - 1
                delta = value
            else:
                index = left
                left &= left - 1
                delta = -value
            coordinates = fenwick.ys[index]
            low = _spatial_structure_rectangle_add_point_get_bisect_left(coordinates, bottom)
            high = _spatial_structure_rectangle_add_point_get_bisect_left(coordinates, top)
            row = fenwick.bit[index]
            while low != high:
                if low < high:
                    row[high] += delta
                    high &= high - 1
                else:
                    row[low] -= delta
                    low &= low - 1

    def get(self, x, y):
        """登録点(x, y)に、それまでのaddで加えた値の合計を返す。"""
        fenwick = self._fenwick
        index = fenwick._points[x, y]
        result = 0
        while index <= len(fenwick.xs):
            position = _spatial_structure_rectangle_add_point_get_bisect_left(fenwick.ys[index], y) + 1
            row = fenwick.bit[index]
            while position < len(row):
                result += row[position]
                position += position & -position
            index += index & -index
        return result

    def items(self):
        return [(x, y, self.get(x, y)) for (x, y) in sorted(self._fenwick._points)]

    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return f'RectangleAddPointGet({self.items()!r})'
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    initial = [tuple(map(int, read().split())) for _ in range(n)]
    operations = [tuple(map(int, read().split())) for _ in range(q)]
    solver = RectangleAddPointGet(((op[1], op[2]) for op in operations if op[0]))
    for rectangle in initial:
        solver.add(*rectangle)
    answers = []
    for operation in operations:
        if operation[0] == 0:
            solver.add(*operation[1:])
        else:
            answers.append(solver.get(operation[1], operation[2]))
    sys.stdout.write('\n'.join(map(str, answers)))
if __name__ == '__main__':
    main()
