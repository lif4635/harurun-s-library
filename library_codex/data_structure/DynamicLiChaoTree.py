"""整数座標区間でnodeを動的生成するLi Chao Tree。"""

INF = float("inf")

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
