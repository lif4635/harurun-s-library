from bisect import bisect_left


INF = float("inf")


class LiChaoTree:
    __slots__ = ("xs", "n", "size", "slope", "intercept", "sign")

    def __init__(self, xs, minimize=True):
        xs = sorted(set(xs))
        assert xs
        n = len(xs)
        size = 1 << (n - 1).bit_length()
        self.xs = xs
        self.n = n
        self.size = size
        self.slope = [0] * (size << 1)
        self.intercept = [INF] * (size << 1)
        self.sign = 1 if minimize else -1

    def _add_node(self, k, a, b):
        size = self.size
        depth = k.bit_length() - 1
        width = size >> depth
        left = (k - (1 << depth)) * width
        right = left + width
        xs = self.xs
        n = self.n
        slope = self.slope
        intercept = self.intercept

        while True:
            mid = (left + right) >> 1
            xl = xs[left if left < n else n - 1]
            xm = xs[mid if mid < n else n - 1]
            xr = xs[right - 1 if right <= n else n - 1]
            ak = slope[k]
            bk = intercept[k]
            left_better = a * xl + b < ak * xl + bk
            right_better = a * xr + b < ak * xr + bk
            if left_better and right_better:
                slope[k] = a
                intercept[k] = b
                return
            if not left_better and not right_better:
                return
            mid_better = a * xm + b < ak * xm + bk
            if mid_better:
                slope[k], a = a, ak
                intercept[k], b = b, bk
            if right - left == 1:
                return
            if left_better != mid_better:
                k <<= 1
                right = mid
            else:
                k = k << 1 | 1
                left = mid

    def add_line(self, a, b):
        sign = self.sign
        self._add_node(1, a * sign, b * sign)

    add = add_line
    update = add_line

    def add_segment_index(self, a, b, l, r):
        assert 0 <= l <= r <= self.n
        if l == r:
            return
        sign = self.sign
        a *= sign
        b *= sign
        l += self.size
        r += self.size
        while l < r:
            if l & 1:
                self._add_node(l, a, b)
                l += 1
            if r & 1:
                r -= 1
                self._add_node(r, a, b)
            l >>= 1
            r >>= 1

    def add_segment(self, a, b, left, right):
        l = bisect_left(self.xs, left)
        r = bisect_left(self.xs, right)
        self.add_segment_index(a, b, l, r)

    update_segment = add_segment

    def query_index(self, i):
        assert 0 <= i < self.n
        x = self.xs[i]
        k = i + self.size
        res = INF
        slope = self.slope
        intercept = self.intercept
        while k:
            y = slope[k] * x + intercept[k]
            if y < res:
                res = y
            k >>= 1
        return res * self.sign

    def query(self, x):
        i = bisect_left(self.xs, x)
        assert i < self.n and self.xs[i] == x
        return self.query_index(i)

    get = query
    get_min = query


class DynamicLiChaoTree:
    __slots__ = ("left", "right", "lines", "sign")

    def __init__(self, left, right, minimize=True):
        assert left < right
        self.left = left
        self.right = right
        self.lines = {}
        self.sign = 1 if minimize else -1

    def _add_node(self, k, left, right, a, b):
        lines = self.lines
        while True:
            old = lines.get(k)
            if old is None:
                lines[k] = (a, b)
                return
            old_a, old_b = old
            mid = (left + right) >> 1
            xl = left
            xm = mid
            xr = right - 1
            left_better = a * xl + b < old_a * xl + old_b
            right_better = a * xr + b < old_a * xr + old_b
            if left_better and right_better:
                lines[k] = (a, b)
                return
            if not left_better and not right_better:
                return
            mid_better = a * xm + b < old_a * xm + old_b
            if mid_better:
                lines[k] = (a, b)
                a, b = old_a, old_b
            if right - left == 1:
                return
            if left_better != mid_better:
                k <<= 1
                right = mid
            else:
                k = k << 1 | 1
                left = mid

    def add_line(self, a, b):
        sign = self.sign
        self._add_node(1, self.left, self.right, a * sign, b * sign)

    add = add_line
    update = add_line

    def add_segment(self, a, b, ql, qr):
        assert self.left <= ql <= qr <= self.right
        if ql == qr:
            return
        sign = self.sign
        a *= sign
        b *= sign
        stack = [(1, self.left, self.right)]
        while stack:
            k, left, right = stack.pop()
            if qr <= left or right <= ql:
                continue
            if ql <= left and right <= qr:
                self._add_node(k, left, right, a, b)
                continue
            mid = (left + right) >> 1
            stack.append((k << 1 | 1, mid, right))
            stack.append((k << 1, left, mid))

    update_segment = add_segment

    def query(self, x):
        assert self.left <= x < self.right
        k = 1
        left = self.left
        right = self.right
        res = INF
        lines = self.lines
        while True:
            line = lines.get(k)
            if line is not None:
                y = line[0] * x + line[1]
                if y < res:
                    res = y
            if right - left == 1:
                break
            mid = (left + right) >> 1
            if x < mid:
                k <<= 1
                right = mid
            else:
                k = k << 1 | 1
                left = mid
        return res * self.sign

    get = query
    get_min = query
