"""傾きとquery位置が単調な直線集合の最適値を求める。"""

class MonotoneConvexHullTrick:
    __slots__ = ("lines", "direction", "sign")

    def __init__(self, minimize=True, increasing_slopes=True):
        self.lines = []
        self.direction = 1 if increasing_slopes else -1
        self.sign = 1 if minimize else -1

    @staticmethod
    def _obsolete(first, second, third):
        return (
            (first[1] - second[1]) * (third[0] - second[0])
            <= (second[1] - third[1]) * (second[0] - first[0])
        )

    def add_line(self, slope, intercept):
        slope *= self.direction
        intercept *= self.sign
        lines = self.lines
        if lines and slope < lines[-1][0]:
            raise ValueError("slopes must be added in the declared order")
        if lines and slope == lines[-1][0]:
            if lines[-1][1] <= intercept:
                return
            lines.pop()
        line = (slope, intercept)
        while len(lines) >= 2 and self._obsolete(
            lines[-2], lines[-1], line
        ):
            lines.pop()
        lines.append(line)

    add = add_line

    def query(self, point):
        lines = self.lines
        if not lines:
            raise ValueError("line container is empty")
        point *= self.direction * self.sign
        left = 0
        right = len(lines) - 1
        while left < right:
            middle = (left + right) >> 1
            first = lines[middle][0] * point + lines[middle][1]
            second = lines[middle + 1][0] * point + lines[middle + 1][1]
            if first <= second:
                right = middle
            else:
                left = middle + 1
        line = lines[left]
        return (line[0] * point + line[1]) * self.sign

    get = query

