"""重みなし木で、距離が指定範囲に入る頂点へ加算し、頂点値を取得する。"""

from bisect import bisect_left

from library_codex.tree.CentroidDecomposition import CentroidDecomposition


class CentroidDistanceAdd:
    __slots__ = ("decomposition", "bits", "branch_bits", "values")

    def __init__(self, tree, values=None):
        decomposition = CentroidDecomposition(tree)
        n = decomposition.n
        values = [0] * n if values is None else list(values)
        if len(values) != n:
            raise ValueError("values has wrong length")
        lengths = [2] * n
        branch_lengths = [1] * n
        for path in decomposition.paths:
            child = -1
            for centroid, distance, _ in reversed(path):
                if lengths[centroid] < distance + 2:
                    lengths[centroid] = distance + 2
                if child >= 0 and branch_lengths[child] < distance + 2:
                    branch_lengths[child] = distance + 2
                child = centroid
        self.decomposition = decomposition
        self.bits = [[0] * length for length in lengths]
        self.branch_bits = [[0] * length for length in branch_lengths]
        self.values = values

    def add(self, vertex, lower, upper, delta):
        if upper is None:
            upper = self.decomposition.n + 1
        if not isinstance(lower, int):
            lower = bisect_left(range(self.decomposition.n + 1), lower)
        if not isinstance(upper, int):
            upper = bisect_left(range(self.decomposition.n + 1), upper)
        if lower >= upper:
            return
        child = -1
        for centroid, distance, _ in reversed(self.decomposition.paths[vertex]):
            left = max(0, lower - distance)
            right = upper - distance
            if left < right:
                bit = self.bits[centroid]
                index = left + 1
                while index < len(bit):
                    bit[index] += delta
                    index += index & -index
                index = right + 1
                while index < len(bit):
                    bit[index] -= delta
                    index += index & -index
                if child >= 0:
                    bit = self.branch_bits[child]
                    index = left + 1
                    while index < len(bit):
                        bit[index] += delta
                        index += index & -index
                    index = right + 1
                    while index < len(bit):
                        bit[index] -= delta
                        index += index & -index
            child = centroid

    def get(self, vertex):
        result = self.values[vertex]
        child = -1
        for centroid, distance, _ in reversed(self.decomposition.paths[vertex]):
            bit = self.bits[centroid]
            index = distance + 1
            while index:
                result += bit[index]
                index &= index - 1
            if child >= 0:
                bit = self.branch_bits[child]
                index = distance + 1
                while index:
                    result -= bit[index]
                    index &= index - 1
            child = centroid
        return result

    def tolist(self):
        return [self.get(vertex) for vertex in range(self.decomposition.n)]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "CentroidDistanceAdd(%r)" % self.tolist()
