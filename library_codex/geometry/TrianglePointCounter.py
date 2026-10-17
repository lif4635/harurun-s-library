"""固定した点集合について、指定した三角形の内部にある点をO(1)で数える。"""

from bisect import bisect_left, bisect_right
from functools import cmp_to_key


def _angle_compare(first, second):
    cross = first[0] * second[1] - first[1] * second[0]
    if cross:
        return -1 if cross < 0 else 1
    return first[2] - second[2]


class TrianglePointCounter:
    """三角形の頂点候補と数える点を前計算し、辺上を除いた点数を返す。"""

    __slots__ = ("_vertices", "_left", "_on", "_point_left", "_point_on")

    def __init__(self, vertices, points):
        vertices = tuple((y, x) for x, y in vertices)
        points = tuple((x, y) for x, y in points)
        n = len(vertices)
        left = [[0] * n for _ in range(n)]
        on = [[0] * n for _ in range(n)]
        point_left = [0] * n
        point_on = [0] * n
        rows = {}
        for x, y in points:
            rows.setdefault(y, []).append(x)
        for row in rows.values():
            row.sort()
        angle_key = cmp_to_key(_angle_compare)
        for a, (ay, ax) in enumerate(vertices):
            row = rows.get(ay, ())
            point_left[a] = bisect_left(row, ax)
            point_on[a] = bisect_right(row, ax) - point_left[a]
            events = []
            for b, (by, bx) in enumerate(vertices):
                if by > ay:
                    events.append((bx - ax, by - ay, 0, b))
                    events.append((bx - ax, by - ay, 2, b))
            for bx, by in points:
                if by > ay:
                    events.append((bx - ax, by - ay, 1, 0))
            events.sort(key=angle_key)
            order = sorted(range(len(events)), key=lambda i: (events[i][1], events[i][2] & 1))
            bit = [0] * (len(events) + 1)
            left_row = left[a]
            on_row = on[a]
            for i in order:
                kind = events[i][2]
                position = i + 1
                if kind == 1:
                    while position < len(bit):
                        bit[position] += 1
                        position += position & -position
                else:
                    total = 0
                    while position:
                        total += bit[position]
                        position &= position - 1
                    target = events[i][3]
                    if kind == 0:
                        left_row[target] = total
                    else:
                        on_row[target] = total - left_row[target]
        self._vertices = vertices
        self._left = left
        self._on = on
        self._point_left = point_left
        self._point_on = point_on

    def count(self, a, b, c):
        """verticesのa・b・c番目で作る三角形の内部の点数。辺上は除く。O(1)。"""
        vertices = self._vertices
        if not (0 <= a < len(vertices) and 0 <= b < len(vertices) and 0 <= c < len(vertices)):
            raise IndexError("vertex index out of range")
        if vertices[b] < vertices[a]:
            a, b = b, a
        if vertices[c] < vertices[b]:
            b, c = c, b
        if vertices[b] < vertices[a]:
            a, b = b, a
        ay, ax = vertices[a]
        by, bx = vertices[b]
        cy, cx = vertices[c]
        cross = (ax - cx) * (by - cy) - (ay - cy) * (bx - cx)
        if cross == 0:
            return 0
        left = self._left
        on = self._on
        if ay == by:
            return left[b][c] - left[a][c] - on[a][c]
        if by == cy:
            return left[a][c] - left[a][b] - on[a][b]
        if cross < 0:
            return (left[a][c] - left[b][c] - on[b][c] - left[a][b]
                    - on[a][b] - self._point_left[b] - self._point_on[b])
        return left[a][b] + left[b][c] + self._point_left[b] - left[a][c] - on[a][c]
