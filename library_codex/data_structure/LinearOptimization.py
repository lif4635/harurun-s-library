class _StaticUpperHull:
    __slots__ = ("lines",)

    def __init__(self, lines):
        best = {}
        for slope, intercept in lines:
            previous = best.get(slope)
            if previous is None or intercept > previous:
                best[slope] = intercept
        ordered = sorted(best.items())
        hull = []
        for slope, intercept in ordered:
            while len(hull) >= 2:
                m1, b1 = hull[-2]
                m2, b2 = hull[-1]
                if ((b1 - b2) * (slope - m2)
                        < (b2 - intercept) * (m2 - m1)):
                    break
                hull.pop()
            hull.append((slope, intercept))
        self.lines = hull

    def query(self, intercept_coefficient, slope_coefficient):
        lines = self.lines
        left = 0
        right = len(lines) - 1
        while left < right:
            middle = (left + right) >> 1
            slope, intercept = lines[middle]
            first = (intercept_coefficient * intercept
                     + slope_coefficient * slope)
            slope, intercept = lines[middle + 1]
            second = (intercept_coefficient * intercept
                      + slope_coefficient * slope)
            if first >= second:
                right = middle
            else:
                left = middle + 1
        slope, intercept = lines[left]
        return (intercept_coefficient * intercept
                + slope_coefficient * slope)


class LineContainer2D:
    """Insertion-only points and max/min ``a*x+b*y`` queries.

    Each occupied bucket contains a static line hull.  Binary-counter merging
    gives O(log^2 N) amortized insertion and O(log^2 N) query time without a
    pointer-heavy balanced tree.  Integer inputs stay exact.
    """

    __slots__ = ("buckets", "size", "xmin", "xmax", "ymin", "ymax")

    def __init__(self):
        self.buckets = []
        self.size = 0
        self.xmin = self.ymin = None
        self.xmax = self.ymax = None

    def add(self, x, y):
        if self.size == 0:
            self.xmin = self.xmax = x
            self.ymin = self.ymax = y
        else:
            if x < self.xmin:
                self.xmin = x
            if x > self.xmax:
                self.xmax = x
            if y < self.ymin:
                self.ymin = y
            if y > self.ymax:
                self.ymax = y
        points = [(x, y)]
        level = 0
        buckets = self.buckets
        while level < len(buckets) and buckets[level] is not None:
            points += buckets[level][0]
            buckets[level] = None
            level += 1
        lines = [(y0, x0) for x0, y0 in points]
        upper = _StaticUpperHull(lines)
        lower = _StaticUpperHull([(-m, -c) for m, c in lines])
        bucket = (points, upper, lower)
        if level == len(buckets):
            buckets.append(bucket)
        else:
            buckets[level] = bucket
        self.size += 1

    insert = add

    def max_value(self, a, b):
        if self.size == 0:
            raise ValueError("line container is empty")
        if a == 0:
            return b * (self.ymax if b >= 0 else self.ymin)
        answer = None
        if a > 0:
            for bucket in self.buckets:
                if bucket is not None:
                    value = bucket[1].query(a, b)
                    if answer is None or value > answer:
                        answer = value
        else:
            for bucket in self.buckets:
                if bucket is not None:
                    value = bucket[2].query(-a, -b)
                    if answer is None or value > answer:
                        answer = value
        return answer

    def min_value(self, a, b):
        return -self.max_value(-a, -b)

    max_ll = max_value
    min_ll = min_value
    max_ld = max_value
    min_ld = min_value
    get_max = max_value
    get_min = min_value


class RangeLinearAddRangeMin:
    """Add ``a*i+b`` on [left, right), and query the range minimum."""

    __slots__ = ("length", "n", "height", "base", "lazy", "bridges")

    def __init__(self, values, infinity=10 ** 60):
        self.length = len(values)
        n = 1
        height = 0
        while n < len(values):
            n <<= 1
            height += 1
        self.n = n
        self.height = height
        base = [(0, 0)] * (n << 1)
        for index in range(n):
            base[n + index] = (index, values[index]
                               if index < len(values) else infinity)
        self.base = base
        self.lazy = [(0, 0) for _ in range(n << 1)]
        bridges = [((0, 0), (0, 0)) for _ in range(n << 1)]
        for index in range(n, n << 1):
            bridges[index] = (base[index], base[index])
        self.bridges = bridges
        for index in range(n - 1, 0, -1):
            self._find_bridge(index)

    @staticmethod
    def _apply(point, linear):
        x, y = point
        a, b = linear
        return x, y + x * a + b

    @staticmethod
    def _cross(first, second):
        return first[0] * second[1] - first[1] * second[0]

    @staticmethod
    def _add_linear(first, second):
        return first[0] + second[0], first[1] + second[1]

    def _find_bridge(self, node):
        n = self.n
        if node >= n:
            return
        lazy = self.lazy
        offset = (0, 0)
        current = node
        while current:
            offset = self._add_linear(offset, lazy[current])
            current >>= 1

        left = node << 1
        right = left | 1
        border = right
        while border < n:
            border <<= 1
        border -= n
        left_add = lazy[left]
        right_add = lazy[right]
        bridges = self.bridges
        apply = self._apply
        add_linear = self._add_linear
        cross = self._cross
        while left < n or right < n:
            a, b = bridges[left]
            c, d = bridges[right]
            a = apply(apply(a, offset), left_add)
            b = apply(apply(b, offset), left_add)
            c = apply(apply(c, offset), right_add)
            d = apply(apply(d, offset), right_add)
            ba = (b[0] - a[0], b[1] - a[1])
            ca = (c[0] - a[0], c[1] - a[1])
            dc = (d[0] - c[0], d[1] - c[1])
            cb = (c[0] - b[0], c[1] - b[1])
            if a != b and cross(ba, ca) < 0:
                left <<= 1
                left_add = add_linear(left_add, lazy[left])
            elif c != d and cross(cb, dc) < 0:
                right = (right << 1) | 1
                right_add = add_linear(right_add, lazy[right])
            elif a == b:
                right <<= 1
                right_add = add_linear(right_add, lazy[right])
            elif c == d:
                left = (left << 1) | 1
                left_add = add_linear(left_add, lazy[left])
            else:
                c1 = cross(ba, dc)
                c2 = cross(ba, (b[0] - c[0], b[1] - c[1]))
                if c1 == 0 and c2 == 0:
                    side = c[0] < border
                else:
                    side = (c[0] * c1 + (d[0] - c[0]) * c2
                            < c1 * border)
                if side:
                    left = (left << 1) | 1
                    left_add = add_linear(left_add, lazy[left])
                else:
                    right <<= 1
                    right_add = add_linear(right_add, lazy[right])
        self.bridges[node] = (
            apply(self.base[left], left_add),
            apply(self.base[right], right_add),
        )

    def add(self, left, right, slope, intercept):
        if not 0 <= left <= right <= self.length:
            raise IndexError("invalid half-open range")
        n = self.n
        lower = left + n
        upper = right + n
        lazy = self.lazy
        add_linear = self._add_linear
        while lower < upper:
            if lower & 1:
                lazy[lower] = add_linear(lazy[lower], (slope, intercept))
                lower += 1
            lower >>= 1
            if upper & 1:
                upper -= 1
                lazy[upper] = add_linear(lazy[upper], (slope, intercept))
            upper >>= 1
        lower = left + n
        upper = right + n
        for level in range(1, self.height + 1):
            if (lower >> level) << level != lower:
                self._find_bridge(lower >> level)
            if (upper >> level) << level != upper:
                self._find_bridge((upper - 1) >> level)

    update = add
    range_add = add

    def _subtree_minimum(self, node):
        lazy = self.lazy
        add = (0, 0)
        current = node
        while current:
            add = self._add_linear(add, lazy[current])
            current >>= 1
        n = self.n
        apply = self._apply
        while node < n:
            first, second = self.bridges[node]
            if apply(first, add)[1] < apply(second, add)[1]:
                node <<= 1
            else:
                node = (node << 1) | 1
            add = self._add_linear(add, lazy[node])
        return apply(self.base[node], add)[1]

    def query(self, left, right):
        if not 0 <= left < right <= self.length:
            raise IndexError("query range must be nonempty and valid")
        lower = left + self.n
        upper = right + self.n
        answer = None
        while lower < upper:
            if lower & 1:
                value = self._subtree_minimum(lower)
                if answer is None or value < answer:
                    answer = value
                lower += 1
            lower >>= 1
            if upper & 1:
                upper -= 1
                value = self._subtree_minimum(upper)
                if answer is None or value < answer:
                    answer = value
            upper >>= 1
        return answer

    range_min = query

