"""indexの一次式を区間加算し、区間最小値を求める構造。"""

class RangeLinearAddRangeMin:
    """各位置iへ一次式を区間加算し、空でない区間の最小値を取得する。"""
    __slots__ = ('length', 'n', 'height', 'base', 'lazy_a', 'lazy_b', 'left_x', 'left_y', 'right_x', 'right_y')

    def __init__(self, values):
        values = list(values)
        self.length = len(values)
        n = 1 << (len(values) - 1).bit_length() if values else 1
        self.n = n
        self.height = n.bit_length() - 1
        self.base = values + [0] * (n - len(values))
        self.lazy_a = [0] * (n << 1)
        self.lazy_b = [0] * (n << 1)
        self.left_x = [0] * n + list(range(n))
        self.right_x = self.left_x[:]
        self.left_y = [0] * n + self.base
        self.right_y = self.left_y[:]
        for node in range(n - 1, 0, -1):
            self._find_bridge(node)

    def _find_bridge(self, node):
        n = self.n
        (lazy_a, lazy_b) = (self.lazy_a, self.lazy_b)
        (lx, ly) = (self.left_x, self.left_y)
        (rx, ry) = (self.right_x, self.right_y)
        left = node << 1
        right = left | 1
        border = (right << self.height + 1 - right.bit_length()) - n
        (la, lb) = (lazy_a[left], lazy_b[left])
        (ra, rb) = (lazy_a[right], lazy_b[right])
        while left < n or right < n:
            (ax, ay, bx, by) = (lx[left], ly[left], rx[left], ry[left])
            (cx, cy, dx, dy) = (lx[right], ly[right], rx[right], ry[right])
            ay += ax * la + lb
            by += bx * la + lb
            cy += cx * ra + rb
            dy += dx * ra + rb
            (bax, bay) = (bx - ax, by - ay)
            (dcx, dcy) = (dx - cx, dy - cy)
            if left < n and bax * (cy - ay) - bay * (cx - ax) < 0:
                left <<= 1
                (a, b) = (lazy_a[left], lazy_b[left])
                la += a
                lb += b
            elif right < n and (cx - bx) * dcy - (cy - by) * dcx < 0:
                right = right << 1 | 1
                (a, b) = (lazy_a[right], lazy_b[right])
                ra += a
                rb += b
            elif left >= n:
                right <<= 1
                (a, b) = (lazy_a[right], lazy_b[right])
                ra += a
                rb += b
            elif right >= n:
                left = left << 1 | 1
                (a, b) = (lazy_a[left], lazy_b[left])
                la += a
                lb += b
            else:
                c1 = bax * dcy - bay * dcx
                c2 = bax * (by - cy) - bay * (bx - cx)
                side = cx < border if c1 == 0 and c2 == 0 else cx * c1 + dcx * c2 < c1 * border
                if side:
                    left = left << 1 | 1
                    (a, b) = (lazy_a[left], lazy_b[left])
                    la += a
                    lb += b
                else:
                    right <<= 1
                    (a, b) = (lazy_a[right], lazy_b[right])
                    ra += a
                    rb += b
        (x, u) = (left - n, right - n)
        (lx[node], rx[node]) = (x, u)
        ly[node] = self.base[x] + x * la + lb
        ry[node] = self.base[u] + u * ra + rb

    def add(self, left, right, slope, intercept):
        """半開区間[left, right)の各値へslope*i+interceptを加える。"""
        if not 0 <= left <= right <= self.length:
            raise IndexError('invalid half-open range')
        if left == right or slope == intercept == 0:
            return
        n = self.n
        lower = left + n
        upper = right + n
        (lazy_a, lazy_b) = (self.lazy_a, self.lazy_b)
        while lower < upper:
            if lower & 1:
                lazy_a[lower] += slope
                lazy_b[lower] += intercept
                lower += 1
            lower >>= 1
            if upper & 1:
                upper -= 1
                lazy_a[upper] += slope
                lazy_b[upper] += intercept
            upper >>= 1
        lower = left + n
        upper = right + n
        for level in range(1, self.height + 1):
            first = lower >> level if lower >> level << level != lower else 0
            second = upper - 1 >> level if upper >> level << level != upper else 0
            if first:
                self._find_bridge(first)
            if second and second != first:
                self._find_bridge(second)
    update = add
    range_add = add

    def _subtree_minimum(self, node):
        (lazy_a, lazy_b) = (self.lazy_a, self.lazy_b)
        a = b = 0
        current = node
        while current:
            a += lazy_a[current]
            b += lazy_b[current]
            current >>= 1
        n = self.n
        (lx, ly) = (self.left_x, self.left_y)
        (rx, ry) = (self.right_x, self.right_y)
        while node < n:
            if ly[node] - ry[node] < (rx[node] - lx[node]) * a:
                node <<= 1
            else:
                node = node << 1 | 1
            a += lazy_a[node]
            b += lazy_b[node]
        index = node - n
        return self.base[index] + index * a + b

    def query(self, left, right):
        """空でない半開区間[left, right)の最小値を返す。"""
        if not 0 <= left < right <= self.length:
            raise IndexError('query range must be nonempty and valid')
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

    def tolist(self):
        """保留中の一次式加算を含む現在の列を、状態を変えずに返す。"""
        n = self.n
        (a, b) = (self.lazy_a[:], self.lazy_b[:])
        for node in range(1, n):
            left = node << 1
            a[left] += a[node]
            a[left | 1] += a[node]
            b[left] += b[node]
            b[left | 1] += b[node]
        return [self.base[i] + i * a[n + i] + b[n + i] for i in range(self.length)]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'RangeLinearAddRangeMin(%r)' % self.tolist()
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    table = RangeLinearAddRangeMin(list(map(int, read().split())))
    result = []
    for _ in range(q):
        row = list(map(int, read().split()))
        if row[0] == 0:
            table.add(*row[1:])
        else:
            result.append(str(table.query(row[1], row[2])))
    sys.stdout.write('\n'.join(result))
if __name__ == '__main__':
    main()
