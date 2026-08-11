"""groupの静的列で半開区間積をO(1)取得する。"""


class StaticRangeGroup:
    """prefix積と逆元を使う静的な半開区間積query。"""

    __slots__ = ("size", "op", "inverse", "identity", "prefix_values")

    def __init__(self, values, op, inverse, identity):
        self.op = op
        self.inverse = inverse
        self.identity = identity
        prefix_values = [identity]
        current = identity
        for value in values:
            current = op(current, value)
            prefix_values.append(current)
        self.prefix_values = prefix_values
        self.size = len(prefix_values) - 1

    def prod(self, left, right):
        """半開区間[left, right)の積を返す。"""
        if not 0 <= left <= right <= self.size:
            raise IndexError("range is outside the sequence")
        return self.op(self.inverse(self.prefix_values[left]),
                       self.prefix_values[right])

    def prefix(self, right):
        """半開prefix [0, right)の積を返す。"""
        if not 0 <= right <= self.size:
            raise IndexError("right is outside the sequence")
        return self.prefix_values[right]
