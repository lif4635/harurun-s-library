"""整数の半開区間へ値を代入し、隣接する同値区間をまとめて保持する。"""

from library_codex.ordered_set.TreapSet import TreapSet


class IntervalMap:
    """未登録の隙間を残せる区間map。座標の大きさに比例する配列は作らない。"""

    __slots__ = ("_starts", "_segments", "covered_length")

    def __init__(self):
        self._starts = TreapSet()
        self._segments = {}
        self.covered_length = 0

    def _split(self, point):
        start = self._starts.le(point)
        if start is not None and start < point:
            end, value = self._segments[start]
            if point < end:
                self._segments[start] = point, value
                self._segments[point] = end, value
                self._starts.add(point)

    def _erase(self, left, right):
        self._split(left)
        self._split(right)
        removed = 0
        start = self._starts.ge(left)
        while start is not None and start < right:
            end, _ = self._segments.pop(start)
            removed += end - start
            self._starts.discard(start)
            start = self._starts.ge(left)
        self.covered_length -= removed
        return removed

    def _compact(self):
        if len(self._starts.key) > 2 * len(self._segments) + 64:
            self._starts = TreapSet(self._starts)

    def assign(self, left, right, value):
        """半開区間[left, right)をvalueで上書きし、隣接する同値区間を結合する。"""
        if left > right:
            raise ValueError("left must not exceed right")
        if left == right:
            return
        start = self._starts.le(left)
        if start is not None:
            end, old = self._segments[start]
            if right <= end and old == value:
                return
        self._erase(left, right)
        self.covered_length += right - left
        start = self._starts.lt(left)
        if start is not None:
            end, old = self._segments[start]
            if end == left and old == value:
                left = start
                self._starts.discard(start)
                del self._segments[start]
        if right in self._segments:
            end, old = self._segments[right]
            if old == value:
                self._starts.discard(right)
                del self._segments[right]
                right = end
        self._starts.add(left)
        self._segments[left] = right, value
        self._compact()

    def erase(self, left, right):
        """半開区間[left, right)の登録を消し、実際に消した整数座標の個数を返す。"""
        if left > right:
            raise ValueError("left must not exceed right")
        if left == right:
            return 0
        removed = self._erase(left, right)
        self._compact()
        return removed

    def get(self, point, default=None):
        """pointに割り当てた値を返す。未登録ならdefaultを返す。"""
        start = self._starts.le(point)
        if start is not None:
            end, value = self._segments[start]
            if point < end:
                return value
        return default

    def items(self, left=None, right=None):
        """登録された半開区間と値を左端順に返す。指定範囲があれば交差部分に切る。"""
        if left is not None and right is not None:
            if left > right:
                raise ValueError("left must not exceed right")
            if left == right:
                return []
        result = []
        if left is None and right is None:
            return [(start, *self._segments[start]) for start in self._starts]
        if left is None:
            start = self._starts.kth(0) if self._segments else None
        else:
            start = self._starts.le(left)
            if start is None or self._segments[start][0] <= left:
                start = self._starts.ge(left)
        while start is not None and (right is None or start < right):
            end, value = self._segments[start]
            result.append((start if left is None else max(left, start), end if right is None else min(right, end), value))
            start = self._starts.gt(start)
        return result

    def __len__(self):
        return len(self._segments)

    def __str__(self):
        return str(self.items())

    def __repr__(self):
        return "IntervalMap(%r)" % self.items()
