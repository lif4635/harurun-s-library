"""x座標を固定した点のy座標を更新し、xの範囲とyの上限で点を列挙する。"""

from bisect import bisect_left


class PrioritySearchTree:
    """点は入力順の整数IDで扱う。y=Noneの点は無効とする。"""

    __slots__ = ("_xs", "_ys", "_sorted_x", "_rank", "_position", "_heap", "_base", "_count")

    def __init__(self, xs, ys=None):
        self._xs = xs = list(xs)
        n = len(xs)
        values = [None] * n if ys is None else list(ys)
        if len(values) != n:
            raise ValueError("coordinate lengths differ")
        self._ys = [0 if y is None else y for y in values]
        order = sorted(range(n), key=xs.__getitem__)
        self._sorted_x = [xs[i] for i in order]
        self._rank = rank = [0] * n
        self._position = position = [0] * n
        self._base = base = 1 << max(0, n - 1).bit_length()
        self._heap = heap = [-1] * (2 * base)
        self._count = 0
        for r, i in enumerate(order):
            rank[i] = r
            if values[i] is not None:
                heap[base + r] = i
                position[i] = base + r
                self._count += 1
        for v in range(base - 1, 0, -1):
            self._fill(v)

    def _fill(self, v):
        heap, ys, position = self._heap, self._ys, self._position
        base = self._base
        while v < base:
            child = v << 1
            a, b = heap[child], heap[child + 1]
            if b >= 0 and (a < 0 or ys[b] < ys[a] or (ys[b] == ys[a] and b < a)):
                child += 1
                a = b
            heap[v] = a
            if a < 0:
                return
            position[a] = v
            v = child
        heap[v] = -1

    def set(self, index, y):
        """指定IDのy座標を代入して有効にする。Noneなら無効にする。"""
        if not 0 <= index < len(self._xs):
            raise IndexError(index)
        if self._position[index]:
            self.erase(index)
        if y is None:
            return
        heap, ys, rank, position = self._heap, self._ys, self._rank, self._position
        ys[index] = y
        v, left, right = 1, 0, self._base
        while heap[v] >= 0:
            other = heap[v]
            if ys[index] < ys[other] or (ys[index] == ys[other] and index < other):
                heap[v] = index
                position[index] = v
                index = other
            middle = (left + right) >> 1
            if rank[index] < middle:
                v <<= 1
                right = middle
            else:
                v = v * 2 + 1
                left = middle
        heap[v] = index
        position[index] = v
        self._count += 1

    def erase(self, index):
        """指定IDを無効にする。有効な点を消した場合だけTrueを返す。"""
        if not 0 <= index < len(self._xs):
            raise IndexError(index)
        v = self._position[index]
        if not v:
            return False
        self._fill(v)
        self._position[index] = 0
        self._ys[index] = 0
        self._count -= 1
        return True

    def get(self, index):
        """指定IDの現在のy座標を返す。無効ならNone。"""
        if not 0 <= index < len(self._xs):
            raise IndexError(index)
        return self._ys[index] if self._position[index] else None

    def _range_nodes(self, lo, hi):
        if lo == 0 and hi == len(self._xs):
            return [], [1]
        left, right = self._base + lo, self._base + hi - 1
        boundary, whole = [], []
        while left < right:
            boundary.append(left)
            boundary.append(right)
            if left & 1 == 0 and left + 1 < right:
                whole.append(left + 1)
            if right & 1 and left < right - 1:
                whole.append(right - 1)
            left >>= 1
            right >>= 1
        while left:
            boundary.append(left)
            left >>= 1
        return boundary, whole

    def report(self, left, right, upper):
        """left <= x < rightかつy < upperを満たす有効な点のIDを返す。"""
        if left > right:
            raise ValueError("left must not exceed right")
        lo, hi = bisect_left(self._sorted_x, left), bisect_left(self._sorted_x, right)
        if lo == hi:
            return []
        heap, ys, rank, base = self._heap, self._ys, self._rank, self._base
        boundary, whole = self._range_nodes(lo, hi)
        result = []
        for v in boundary:
            index = heap[v]
            if index >= 0 and lo <= rank[index] < hi and ys[index] < upper:
                result.append(index)
        while whole:
            v = whole.pop()
            index = heap[v]
            if index < 0 or not ys[index] < upper:
                continue
            result.append(index)
            if v < base:
                whole.append(v * 2)
                whole.append(v * 2 + 1)
        return result

    def min_y(self, left, right):
        """半開区間内でy最小の有効な点のIDを返す。同値ならID最小。なければNone。"""
        if left > right:
            raise ValueError("left must not exceed right")
        lo, hi = bisect_left(self._sorted_x, left), bisect_left(self._sorted_x, right)
        if lo == hi:
            return None
        heap, ys, rank = self._heap, self._ys, self._rank
        best = -1
        boundary, whole = self._range_nodes(lo, hi)
        for v in boundary + whole:
            index = heap[v]
            if index < 0:
                continue
            if lo <= rank[index] < hi:
                if best < 0 or ys[index] < ys[best] or (ys[index] == ys[best] and index < best):
                    best = index
        return None if best < 0 else best

    def items(self):
        """有効な点を(index, x, y)のlistで、ID順に返す。"""
        return [(i, self._xs[i], y) for i, y in enumerate(self._ys) if self._position[i]]

    def __len__(self):
        return self._count

    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return "PrioritySearchTree(%r)" % self.items()
