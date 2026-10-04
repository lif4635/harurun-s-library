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
            tree = positions.get(value)
            if tree is None:
                tree = positions[value] = TreapSet()
            tree.add(index)
        self.values = values
        self.positions = positions

    def set(self, index, value):
        old = self.values[index]
        if old == value:
            return
        positions = self.positions
        tree = positions[old]
        tree.discard(index)
        if not tree:
            del positions[old]
        tree = positions.get(value)
        if tree is None:
            tree = positions[value] = TreapSet()
        tree.add(index)
        self.values[index] = value

    def query(self, left, right, value):
        positions = self.positions.get(value)
        if positions is None:
            return 0
        return positions.bisect_left(right) - positions.bisect_left(left)

    def tolist(self):
        return self.values.copy()

    def __str__(self):
        return str(self.values)

    def __repr__(self):
        return "PointSetRangeFrequency(%r)" % self.values
