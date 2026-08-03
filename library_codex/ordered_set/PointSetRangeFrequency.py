"""一点変更される列で、区間内の指定値の出現回数を数える構造。"""

from library_codex.ordered_set.TreapSet import TreapSet

class PointSetRangeFrequency:
    __slots__ = ("values", "positions")

    def __init__(self, values):
        if isinstance(values, int):
            values = [0] * values
        else:
            values = list(values)
        positions = {}
        for index, value in enumerate(values):
            positions.setdefault(value, TreapSet()).add(index)
        self.values = values
        self.positions = positions

    def set(self, index, value):
        old = self.values[index]
        if old == value:
            return
        self.positions[old].discard(index)
        self.positions.setdefault(value, TreapSet()).add(index)
        self.values[index] = value

    def query(self, left, right, value):
        positions = self.positions.get(value)
        if positions is None:
            return 0
        return positions.bisect_left(right) - positions.bisect_left(left)
