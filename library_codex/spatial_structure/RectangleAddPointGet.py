"""長方形へ加算し、事前登録した点の現在値を求める。"""

from bisect import bisect_left

from library_codex.spatial_structure.CompressedFenwick2D import CompressedFenwick2D


class RectangleAddPointGet:
    __slots__ = ("_fenwick",)

    def __init__(self, points):
        self._fenwick = CompressedFenwick2D(points)

    def add(self, left, bottom, right, top, value):
        """[left, right) × [bottom, top) の登録点へvalueを加える。"""
        if left >= right or bottom >= top:
            return
        fenwick = self._fenwick
        left = bisect_left(fenwick.xs, left)
        right = bisect_left(fenwick.xs, right)
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
            low = bisect_left(coordinates, bottom)
            high = bisect_left(coordinates, top)
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
        index = fenwick._points[(x, y)]
        result = 0
        while index <= len(fenwick.xs):
            position = bisect_left(fenwick.ys[index], y) + 1
            row = fenwick.bit[index]
            while position < len(row):
                result += row[position]
                position += position & -position
            index += index & -index
        return result

    def items(self):
        return [(x, y, self.get(x, y)) for x, y in sorted(self._fenwick._points)]

    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return f"RectangleAddPointGet({self.items()!r})"
