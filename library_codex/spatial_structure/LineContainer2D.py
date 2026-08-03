"""二変数一次式を追加し、指定点での最大値・最小値を求める構造。"""

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
