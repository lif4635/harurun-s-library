"""直線を追加し、任意のxで最小値または最大値を求める。"""

class LineContainer:
    __slots__ = ("tree",)

    def __init__(
        self, minimize=True, left=-(1 << 63), right=1 << 63
    ):
        from library_codex.spatial_structure.DynamicLiChaoTree import DynamicLiChaoTree

        self.tree = DynamicLiChaoTree(left, right, minimize)

    def add_line(self, slope, intercept):
        self.tree.add_line(slope, intercept)

    add = add_line

    def query(self, point):
        return self.tree.query(point)

    get = query

