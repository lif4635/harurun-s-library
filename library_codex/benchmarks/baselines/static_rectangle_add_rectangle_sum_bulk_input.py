"""矩形への一括加算後に別の矩形和をofflineで求める。"""
from bisect import bisect_left

class RectangleAddRectangleSum:
    __slots__ = ('rectangles', 'queries')

    def __init__(self):
        self.rectangles = []
        self.queries = []

    def add(self, left, bottom, right, top, value):
        self.rectangles.append((left, bottom, right, top, value))
    add_rectangle = add

    def query(self, left, bottom, right, top):
        self.queries.append((left, bottom, right, top))
    add_query = query

    def solve(self, mod=None):
        """各queryの長方形和を登録順に返す。mod指定時はその剰余。"""
        if mod is not None and mod <= 0:
            raise ValueError('mod must be positive')
        events = []
        ys = []
        for (left, bottom, right, top, value) in self.rectangles:
            if left >= right or bottom >= top:
                continue
            events.append((left, bottom, top, value))
            events.append((right, bottom, top, -value))
            ys.append(bottom)
            ys.append(top)
        requests = []
        for (index, (left, bottom, right, top)) in enumerate(self.queries):
            if left < right and bottom < top:
                requests.append((left, bottom, top, ~index))
                requests.append((right, bottom, top, index))
        events.sort()
        requests.sort()
        ys = sorted(set(ys))
        n = len(ys)
        b0 = [0] * (n + 1)
        bx = [0] * (n + 1)
        by = [0] * (n + 1)
        bxy = [0] * (n + 1)
        result = [0] * len(self.queries)
        event_index = 0
        for (x, bottom, top, query_index) in requests:
            while event_index < len(events) and events[event_index][0] < x:
                (event_x, low, high, value) = events[event_index]
                vx = value * event_x
                if mod is not None:
                    value %= mod
                    vx %= mod
                for (y, sign) in ((low, 1), (high, -1)):
                    vy = value * y
                    vxy = vx * y
                    if mod is not None:
                        vy %= mod
                        vxy %= mod
                    (v0, v1, v2, v3) = (sign * value, sign * vx, sign * vy, sign * vxy)
                    index = bisect_left(ys, y) + 1
                    while index <= n:
                        b0[index] += v0
                        bx[index] += v1
                        by[index] += v2
                        bxy[index] += v3
                        index += index & -index
                event_index += 1
            total = 0
            for (y, sign) in ((bottom, -1), (top, 1)):
                index = bisect_left(ys, y)
                s0 = sx = sy = sxy = 0
                while index:
                    s0 += b0[index]
                    sx += bx[index]
                    sy += by[index]
                    sxy += bxy[index]
                    index &= index - 1
                if mod is not None:
                    s0 %= mod
                    sx %= mod
                    sy %= mod
                    sxy %= mod
                total += sign * (x * (y * s0 - sy) - y * sx + sxy)
            if query_index < 0:
                result[~query_index] -= total
            else:
                result[query_index] += total
        if mod is not None:
            return [value % mod for value in result]
        return result
    run = solve
import sys

def main():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n = next(data)
    q = next(data)
    solver = RectangleAddRectangleSum()
    for _ in range(n):
        solver.add(next(data), next(data), next(data), next(data), next(data))
    for _ in range(q):
        solver.query(next(data), next(data), next(data), next(data))
    sys.stdout.write('\n'.join(map(str, solver.solve(998244353))))
if __name__ == '__main__':
    main()
