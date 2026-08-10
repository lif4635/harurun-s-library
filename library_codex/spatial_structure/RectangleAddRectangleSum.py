"""矩形への一括加算後に別の矩形和をofflineで求める。"""

from bisect import bisect_left

from library_codex.fenwick_tree.BIT import BIT

class RectangleAddRectangleSum:
    __slots__ = ("rectangles", "queries")

    def __init__(self):
        self.rectangles = []
        self.queries = []

    def add(self, left, bottom, right, top, value):
        self.rectangles.append((left, bottom, right, top, value))

    add_rectangle = add

    def query(self, left, bottom, right, top):
        self.queries.append((left, bottom, right, top))

    add_query = query

    def solve(self):
        events = []
        ys = []
        for left, bottom, right, top, value in self.rectangles:
            events.append((left, bottom, value))
            events.append((left, top, -value))
            events.append((right, bottom, -value))
            events.append((right, top, value))
            ys.append(bottom)
            ys.append(top)
        requests = []
        for index, (left, bottom, right, top) in enumerate(self.queries):
            requests.append((left, bottom, 1, index))
            requests.append((left, top, -1, index))
            requests.append((right, bottom, -1, index))
            requests.append((right, top, 1, index))
        events.sort()
        requests.sort()
        ys = sorted(set(ys))
        bits = [BIT(len(ys)) for _ in range(4)]
        result = [0] * len(self.queries)
        event_index = 0
        for x, y, sign, query_index in requests:
            while event_index < len(events) and events[event_index][0] < x:
                event_x, event_y, value = events[event_index]
                index = bisect_left(ys, event_y)
                bits[0].add(index, value)
                bits[1].add(index, value * event_x)
                bits[2].add(index, value * event_y)
                bits[3].add(index, value * event_x * event_y)
                event_index += 1
            index = bisect_left(ys, y)
            s00 = bits[0].prefix_sum(index)
            sx = bits[1].prefix_sum(index)
            sy = bits[2].prefix_sum(index)
            sxy = bits[3].prefix_sum(index)
            prefix = x * y * s00 - y * sx - x * sy + sxy
            result[query_index] += sign * prefix
        return result

    run = solve
