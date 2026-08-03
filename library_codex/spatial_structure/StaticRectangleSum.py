"""重み付き点集合に対する静的なoffline矩形和queryを処理する。"""

from bisect import bisect_left

from library_codex.fenwick_tree.FenwickTree import FenwickTree

class StaticRectangleSum:
    __slots__ = ("points", "queries")

    def __init__(self):
        self.points = []
        self.queries = []

    def add(self, x, y, value):
        self.points.append((x, y, value))

    def query(self, left, bottom, right, top):
        self.queries.append((left, bottom, right, top))

    def solve(self):
        ys = sorted(set(y for _, y, _ in self.points))
        points = sorted(self.points)
        events = []
        for index, (left, bottom, right, top) in enumerate(self.queries):
            events.append((left, -1, index, bottom, top))
            events.append((right, 1, index, bottom, top))
        events.sort()
        fenwick = FenwickTree(len(ys))
        result = [0] * len(self.queries)
        point_index = 0
        for x, sign, index, bottom, top in events:
            while point_index < len(points) and points[point_index][0] < x:
                _, y, value = points[point_index]
                fenwick.add(bisect_left(ys, y), value)
                point_index += 1
            result[index] += sign * fenwick.sum(
                bisect_left(ys, bottom), bisect_left(ys, top)
            )
        return result

    run = solve
