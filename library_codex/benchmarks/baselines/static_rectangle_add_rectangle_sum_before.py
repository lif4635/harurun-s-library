"""一点加算・prefix和・区間和を対数時間で扱うBIT。"""

class BIT:
    __slots__ = ('n', 'bit')

    def __init__(self, values):
        if isinstance(values, int):
            if values < 0:
                raise ValueError('size must be nonnegative')
            self.n = values
            self.bit = [0] * (values + 1)
        else:
            values = list(values)
            n = len(values)
            bit = [0] + values
            for index in range(1, n + 1):
                parent = index + (index & -index)
                if parent <= n:
                    bit[parent] += bit[index]
            self.n = n
            self.bit = bit

    def add(self, index, value):
        """a[index]へvalueを加える。"""
        index += 1
        bit = self.bit
        while index <= self.n:
            bit[index] += value
            index += index & -index

    def prefix_sum(self, right):
        """半開区間[0, right)の和を返す。"""
        result = 0
        bit = self.bit
        while right:
            result += bit[right]
            right &= right - 1
        return result

    def sum(self, left, right=None):
        """[left, right)の和を返す。right省略時は[0, left)の和。"""
        if right is None:
            return self.prefix_sum(left)
        return self.prefix_sum(right) - self.prefix_sum(left)

    def get(self, index):
        """a[index]を返す。"""
        return self.sum(index, index + 1)

    def set(self, index, value):
        """a[index]をvalueへ置き換える。"""
        self.add(index, value - self.get(index))

    def lower_bound(self, target):
        """prefix和がtarget以上になる最小の右端を返す。"""
        if target <= 0:
            return 0
        index = 0
        step = 1 << self.n.bit_length() - 1 if self.n else 0
        bit = self.bit
        while step:
            next_index = index + step
            if next_index <= self.n and bit[next_index] < target:
                target -= bit[next_index]
                index = next_index
            step >>= 1
        return index if index < self.n else self.n

    def __len__(self):
        return self.n

    def tolist(self):
        """現在の要素列をlistで返す。O(N)。"""
        values = self.bit[1:]
        for index in range(self.n, 0, -1):
            parent = index + (index & -index)
            if parent <= self.n:
                values[parent - 1] -= values[index - 1]
        return values

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'BIT(%r)' % self.tolist()
'矩形への一括加算後に別の矩形和をofflineで求める。'
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

    def solve(self):
        events = []
        ys = []
        for (left, bottom, right, top, value) in self.rectangles:
            events.append((left, bottom, value))
            events.append((left, top, -value))
            events.append((right, bottom, -value))
            events.append((right, top, value))
            ys.append(bottom)
            ys.append(top)
        requests = []
        for (index, (left, bottom, right, top)) in enumerate(self.queries):
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
        for (x, y, sign, query_index) in requests:
            while event_index < len(events) and events[event_index][0] < x:
                (event_x, event_y, value) = events[event_index]
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
    sys.stdout.write('\n'.join((str(value % 998244353) for value in solver.solve())))
if __name__ == '__main__':
    main()
