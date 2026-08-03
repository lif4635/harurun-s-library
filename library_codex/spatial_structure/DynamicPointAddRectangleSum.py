"""点の重み追加と矩形和queryが混ざる列をofflineで処理する。"""

from library_codex.spatial_structure.CompressedFenwick2D import CompressedFenwick2D

class DynamicPointAddRectangleSum:
    __slots__ = ("operations",)

    def __init__(self):
        self.operations = []

    def add(self, x, y, value):
        self.operations.append((0, x, y, value))

    def query(self, left, bottom, right, top):
        self.operations.append((1, left, bottom, right, top))

    def solve(self):
        points = [(op[1], op[2]) for op in self.operations if op[0] == 0]
        fenwick = CompressedFenwick2D(points)
        result = []
        for operation in self.operations:
            if operation[0] == 0:
                fenwick.add(operation[1], operation[2], operation[3])
            else:
                result.append(fenwick.sum(*operation[1:]))
        return result

    run = solve
