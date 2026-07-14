from bisect import bisect_left

from library_codex.data_structure.FenwickTree import FenwickTree


class CumulativeSum2D:
    __slots__ = ("height", "width", "data")

    def __init__(self, matrix):
        matrix = [list(row) for row in matrix]
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        if any(len(row) != width for row in matrix):
            raise ValueError("matrix must be rectangular")
        data = [[0] * (width + 1) for _ in range(height + 1)]
        for row in range(height):
            running = 0
            source = matrix[row]
            previous = data[row]
            target = data[row + 1]
            for column in range(width):
                running += source[column]
                target[column + 1] = previous[column + 1] + running
        self.height = height
        self.width = width
        self.data = data

    def sum(self, top, left, bottom, right):
        data = self.data
        return (
            data[bottom][right]
            - data[top][right]
            - data[bottom][left]
            + data[top][left]
        )

    prod = sum


class SegmentTree2D:
    __slots__ = (
        "height", "width", "row_size", "column_size", "data", "op", "identity"
    )

    def __init__(self, matrix, op, identity):
        matrix = [list(row) for row in matrix]
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        if any(len(row) != width for row in matrix):
            raise ValueError("matrix must be rectangular")
        row_size = 1 << (height - 1).bit_length() if height else 1
        column_size = 1 << (width - 1).bit_length() if width else 1
        data = [
            [identity] * (column_size << 1)
            for _ in range(row_size << 1)
        ]
        for row in range(height):
            target = data[row + row_size]
            target[column_size : column_size + width] = matrix[row]
            for node in range(column_size - 1, 0, -1):
                target[node] = op(target[node << 1], target[node << 1 | 1])
        for row in range(row_size - 1, 0, -1):
            target = data[row]
            first = data[row << 1]
            second = data[row << 1 | 1]
            for column in range(1, column_size << 1):
                target[column] = op(first[column], second[column])
        self.height = height
        self.width = width
        self.row_size = row_size
        self.column_size = column_size
        self.data = data
        self.op = op
        self.identity = identity

    def set(self, row, column, value):
        row_node = row + self.row_size
        column_node = column + self.column_size
        data = self.data
        op = self.op
        data[row_node][column_node] = value
        node = column_node >> 1
        while node:
            data[row_node][node] = op(
                data[row_node][node << 1],
                data[row_node][node << 1 | 1],
            )
            node >>= 1
        row_node >>= 1
        while row_node:
            column_node = column + self.column_size
            data[row_node][column_node] = op(
                data[row_node << 1][column_node],
                data[row_node << 1 | 1][column_node],
            )
            node = column_node >> 1
            while node:
                data[row_node][node] = op(
                    data[row_node][node << 1],
                    data[row_node][node << 1 | 1],
                )
                node >>= 1
            row_node >>= 1

    def get(self, row, column):
        return self.data[row + self.row_size][column + self.column_size]

    def _column_prod(self, row_node, left, right):
        left += self.column_size
        right += self.column_size
        result = self.identity
        op = self.op
        data = self.data[row_node]
        while left < right:
            if left & 1:
                result = op(result, data[left])
                left += 1
            if right & 1:
                right -= 1
                result = op(result, data[right])
            left >>= 1
            right >>= 1
        return result

    def prod(self, top, left, bottom, right):
        top += self.row_size
        bottom += self.row_size
        result = self.identity
        op = self.op
        while top < bottom:
            if top & 1:
                result = op(result, self._column_prod(top, left, right))
                top += 1
            if bottom & 1:
                bottom -= 1
                result = op(result, self._column_prod(bottom, left, right))
            top >>= 1
            bottom >>= 1
        return result

    query = prod


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


class DynamicPointAddRectangleSum:
    __slots__ = ("operations",)

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
        bits = [FenwickTree(len(ys)) for _ in range(4)]
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


class PointUpdateRangeTree2D:
    """Offline-coordinate point update / rectangle monoid fold range tree."""

    __slots__ = ("points", "n", "ys", "sizes", "data", "op", "identity",
                 "update")

    def __init__(self, points=(), op=lambda first, second: first + second,
                 identity=0, update=None):
        self.points = list(points)
        self.n = 0
        self.ys = []
        self.sizes = []
        self.data = []
        self.op = op
        self.identity = identity
        self.update = update or op

    def add_point(self, x, y):
        if self.n:
            raise RuntimeError("points must be registered before build")
        self.points.append((x, y))

    def build(self):
        points = sorted(set(self.points))
        self.points = points
        n = len(points)
        self.n = n
        ys = [[] for _ in range(max(2, n << 1))]
        for index, (_, y) in enumerate(points):
            node = index + n
            while node:
                ys[node].append(y)
                node >>= 1
        sizes = [1] * len(ys)
        data = [None] * len(ys)
        for node in range(1, len(ys)):
            ys[node] = sorted(set(ys[node]))
            size = 1 << (len(ys[node]) - 1).bit_length() if ys[node] else 1
            sizes[node] = size
            data[node] = [self.identity] * (size << 1)
        self.ys = ys
        self.sizes = sizes
        self.data = data
        return self

    def _xid(self, x):
        return bisect_left(self.points, (x,))

    def _inner_update(self, node, y, value, replace):
        index = bisect_left(self.ys[node], y)
        if index == len(self.ys[node]) or self.ys[node][index] != y:
            raise KeyError("point was not registered")
        index += self.sizes[node]
        row = self.data[node]
        row[index] = value if replace else self.update(row[index], value)
        index >>= 1
        while index:
            row[index] = self.op(row[index << 1], row[index << 1 | 1])
            index >>= 1

    def add(self, x, y, value):
        index = bisect_left(self.points, (x, y))
        if index == self.n or self.points[index] != (x, y):
            raise KeyError("point was not registered")
        node = index + self.n
        while node:
            self._inner_update(node, y, value, False)
            node >>= 1

    def set(self, x, y, value):
        index = bisect_left(self.points, (x, y))
        if index == self.n or self.points[index] != (x, y):
            raise KeyError("point was not registered")
        # Recover the old leaf value and apply its replacement at every ancestor.
        leaf = index + self.n
        y_index = bisect_left(self.ys[leaf], y) + self.sizes[leaf]
        old = self.data[leaf][y_index]
        if self.update is not self.op:
            raise ValueError("set is only available through a custom replacement strategy")
        # For additive groups users should call add(delta); generic monoids cannot remove old.
        if old != self.identity:
            raise ValueError("generic set cannot replace an existing nonidentity value")
        node = leaf
        while node:
            self._inner_update(node, y, value, False)
            node >>= 1

    def _inner_query(self, node, bottom, top):
        left = bisect_left(self.ys[node], bottom) + self.sizes[node]
        right = bisect_left(self.ys[node], top) + self.sizes[node]
        row = self.data[node]
        left_value = self.identity
        right_value = self.identity
        while left < right:
            if left & 1:
                left_value = self.op(left_value, row[left])
                left += 1
            if right & 1:
                right -= 1
                right_value = self.op(row[right], right_value)
            left >>= 1
            right >>= 1
        return self.op(left_value, right_value)

    def query(self, left, bottom, right, top):
        first = self._xid(left) + self.n
        last = self._xid(right) + self.n
        left_value = self.identity
        right_value = self.identity
        while first < last:
            if first & 1:
                left_value = self.op(
                    left_value, self._inner_query(first, bottom, top)
                )
                first += 1
            if last & 1:
                last -= 1
                right_value = self.op(
                    self._inner_query(last, bottom, top), right_value
                )
            first >>= 1
            last >>= 1
        return self.op(left_value, right_value)

    sum = query
    prod = query


RangeTree = PointUpdateRangeTree2D
SegmentTreeOnRangeTree = PointUpdateRangeTree2D
SegmentTreeOnWaveletMatrix = PointUpdateRangeTree2D
