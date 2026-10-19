"""平面の点集合を凸包の境界ごとに剥がし、各層や各点の深さを求める。

Adapted from yosupo06/library-checker-problems, revision
1814c4e5205517e368bb57a8d1127eb961cfeaae,
geo/convex_layers/sol/correct.cpp.
Changes: iterative array-backed trees, batched deletion, retained tangents,
duplicate and empty input support, optional strict boundary peeling.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy at https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from library_codex.geometry.ConvexHull import convex_hull


class _DecrementalHull:
    def __init__(self, points):
        n = len(points)
        size = 1 << (n - 1).bit_length()
        self.size = size
        self.xs = [p[0] for p in points]
        self.ys = [p[1] for p in points]
        self.active = [-1] * (size << 1)
        self.left = [0] * size
        self.right = [0] * size
        self.first = [0] * (size << 1)
        self.bl = [-1] * (size << 1)
        self.br = [-1] * (size << 1)
        self.dirty = bytearray(size)
        for i in range(n):
            node = size + i
            self.active[node] = node
            self.first[node] = self.bl[node] = self.br[node] = i
        self._update(range(size - 1, 0, -1))

    def _update(self, nodes):
        active = self.active
        left, right = self.left, self.right
        first = self.first
        xs, ys = self.xs, self.ys
        bl, br = self.bl, self.br
        size = self.size
        for node in nodes:
            l = active[node << 1]
            r = active[node << 1 | 1]
            if l < 0 or r < 0:
                active[node] = max(l, r)
                continue
            active[node] = node
            left[node], right[node] = l, r
            first[node] = first[l]
            if bl[node] >= 0 and active[size + bl[node]] >= 0 and active[size + br[node]] >= 0:
                continue
            split = ys[first[r]]
            while bl[l] != br[l] or bl[r] != br[r]:
                a, b, c, d = bl[l], br[l], bl[r], br[r]
                abx, aby = xs[b] - xs[a], ys[b] - ys[a]
                bcx, bcy = xs[c] - xs[b], ys[c] - ys[b]
                s1 = abx * bcy - aby * bcx
                if a != b and s1 > 0:
                    l = left[l]
                    continue
                s3 = bcx * (ys[d] - ys[c]) - bcy * (xs[d] - xs[c])
                if c != d and s3 > 0:
                    r = right[r]
                elif a == b:
                    r = left[r]
                elif c == d:
                    l = right[l]
                else:
                    s2 = aby * (xs[d] - xs[b]) - abx * (ys[d] - ys[b])
                    if s1 + s2 == 0 or s1 * (ys[d] - split) + s2 * (ys[c] - split) < 0:
                        l = right[l]
                    else:
                        r = left[r]
            bl[node], br[node] = bl[l], bl[r]

    def hull(self):
        root = self.active[1]
        if root < 0:
            return []
        stack = [root, 0, len(self.xs) - 1]
        result = []
        bl, br, left, right = self.bl, self.br, self.left, self.right
        while stack:
            high, low, node = stack.pop(), stack.pop(), stack.pop()
            while bl[node] != br[node]:
                a, b = bl[node], br[node]
                if high <= a:
                    node = left[node]
                elif low >= b:
                    node = right[node]
                else:
                    stack.extend((right[node], b, high))
                    node, high = left[node], a
            result.append(bl[node])
        return result

    def erase(self, indices):
        active, dirty, size = self.active, self.dirty, self.size
        changed = []
        for i in indices:
            node = size + i
            active[node] = -1
            node >>= 1
            while node and not dirty[node]:
                dirty[node] = 1
                changed.append(node)
                node >>= 1
        changed.sort(reverse=True)
        for node in changed:
            dirty[node] = 0
        self._update(changed)


def _layers(points, keep_collinear):
    ordered = sorted(set(points), key=lambda p: (p[1], p[0]))
    n = len(ordered)
    if not n:
        return
    x0, y0 = ordered[0]
    dx, dy = ordered[-1][0] - x0, ordered[-1][1] - y0
    if all(dx * (y - y0) == dy * (x - x0) for x, y in ordered):
        if keep_collinear:
            yield ordered
        else:
            for i in range((n + 1) // 2):
                yield [ordered[i]] if i == n - 1 - i else [ordered[i], ordered[n - 1 - i]]
        return
    left = _DecrementalHull(ordered)
    right = _DecrementalHull([(-x, -y) for x, y in reversed(ordered)])
    positions = {point: i for i, point in enumerate(ordered)} if not keep_collinear else None
    while left.active[1] >= 0:
        indices = set(left.hull())
        indices.update(n - 1 - i for i in right.hull())
        if not keep_collinear:
            indices = [positions[p] for p in convex_hull([ordered[i] for i in indices])]
        yield [ordered[i] for i in indices]
        left.erase(indices)
        right.erase([n - 1 - i for i in indices])


def convex_layers(points, keep_collinear=True):
    """外側から順に各凸包の点列を返す。既定では時間O(N log² N)、追加空間O(N)。

    各層は辞書順最小点から反時計回り。全点が共線の層は辞書順。
    同じ座標は一つにまとめる。keep_collinear=Falseでは辺の途中の点を次の層へ残す。
    Falseの場合の時間は最悪O(N² log N)。
    """
    return [convex_hull(layer, keep_collinear) for layer in _layers(points, keep_collinear)]


def onion_depth(points, keep_collinear=True):
    """入力順に各点の層番号を返す。最外層は0。同じ座標は同じ層になる。

    keep_collinear=Falseでは辺の途中の点を次の層へ残す。
    既定では時間O(N log² N)、Falseなら最悪O(N² log N)。追加空間O(N)。
    """
    depth = {}
    for layer_id, layer in enumerate(_layers(points, keep_collinear)):
        for point in layer:
            depth[point] = layer_id
    return [depth[point] for point in points]
