"""静的な頂点値について、木のpath・部分木内の順位と値域個数を求める。"""

from bisect import bisect_left

from library_codex.range_query.WaveletMatrix import WaveletMatrix
from library_codex.tree.HeavyLightDecomposition import HeavyLightDecomposition


class TreeWaveletMatrix:
    __slots__ = ("hld", "wm", "sorted_values", "_values")

    def __init__(self, tree, values, root=0):
        n = len(tree)
        values = list(values)
        if len(values) != n:
            raise ValueError("values must contain one value for each vertex")
        adjacency = [
            [edge if isinstance(edge, int) else edge[0] for edge in row]
            for row in tree
        ]
        hld = HeavyLightDecomposition(adjacency, root)
        sorted_values = sorted(set(values))
        index = {value: rank for rank, value in enumerate(sorted_values)}
        ordered = [index[values[hld.rev[position]]] for position in range(n)]
        self.hld = hld
        self.wm = WaveletMatrix(ordered)
        self.sorted_values = sorted_values
        self._values = values

    @staticmethod
    def _ones(wm, level, position):
        block = wm.blocks[level]
        block_index = position >> 6
        offset = position & 63
        mask = (1 << offset) - 1
        return (
            wm.prefix[level][block_index]
            + (block[block_index] & mask).bit_count()
        )

    def _count_lt(self, segments, upper):
        wm = self.wm
        if upper <= 0:
            return 0
        total = sum(right - left for left, right in segments)
        if upper >= len(self.sorted_values):
            return total
        result = 0
        current = segments
        for level in range(wm.log - 1, -1, -1):
            following = []
            one = upper >> level & 1
            middle = wm.mid[level]
            for left, right in current:
                left_one = self._ones(wm, level, left)
                right_one = self._ones(wm, level, right)
                if one:
                    result += right - left - right_one + left_one
                    following.append((middle + left_one, middle + right_one))
                else:
                    following.append((left - left_one, right - right_one))
            current = following
        return result

    def _kth(self, segments, k):
        wm = self.wm
        total = sum(right - left for left, right in segments)
        if not 0 <= k < total:
            raise IndexError("k is outside the selected vertices")
        rank = 0
        current = segments
        for level in range(wm.log - 1, -1, -1):
            zeros = 0
            counts = []
            for left, right in current:
                left_one = self._ones(wm, level, left)
                right_one = self._ones(wm, level, right)
                counts.append((left, right, left_one, right_one))
                zeros += right - left - right_one + left_one
            following = []
            if k < zeros:
                for left, right, left_one, right_one in counts:
                    following.append((left - left_one, right - right_one))
            else:
                k -= zeros
                rank |= 1 << level
                middle = wm.mid[level]
                for _left, _right, left_one, right_one in counts:
                    following.append((middle + left_one, middle + right_one))
            current = following
        return self.sorted_values[rank]

    def kth_path(self, first, second, k):
        """firstからsecondまでの頂点値で、k番目に小さい値を返す。"""
        return self._kth(self.hld.path(first, second), k)

    def count_path(self, first, second, lower, upper):
        """path上でlower以上upper未満の値を持つ頂点数を返す。"""
        segments = self.hld.path(first, second)
        values = self.sorted_values
        return (
            self._count_lt(segments, bisect_left(values, upper))
            - self._count_lt(segments, bisect_left(values, lower))
        )

    def kth_subtree(self, vertex, k):
        """rooted treeのvertex部分木で、k番目に小さい頂点値を返す。"""
        return self._kth([self.hld.subtree(vertex)], k)

    def count_subtree(self, vertex, lower, upper):
        """vertex部分木でlower以上upper未満の値を持つ頂点数を返す。"""
        segments = [self.hld.subtree(vertex)]
        values = self.sorted_values
        return (
            self._count_lt(segments, bisect_left(values, upper))
            - self._count_lt(segments, bisect_left(values, lower))
        )

    def tolist(self):
        return list(self._values)

    def __str__(self):
        return str(self._values)

    def __repr__(self):
        return "TreeWaveletMatrix(%r)" % self._values
