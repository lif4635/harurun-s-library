"""平面の整数座標からドロネー三角形分割の辺を求める。

Adapted from yosupo06/library-checker-problems, revision
1814c4e5205517e368bb57a8d1127eb961cfeaae,
geo/euclidean_mst/sol/correct.cpp.
Changes: iterative Python implementation, flat half-edge arrays, paired edge
reuse, empty input support and original-index duplicate connections.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy at https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

class _geometry_delaunay_Triangulation:

    def __init__(self, points):
        self.x = [p[0] for p in points]
        self.y = [p[1] for p in points]
        self.to = []
        self.cw = []
        self.ccw = []
        self.alive = bytearray()
        self.free = []

    def _new(self, u, v):
        if self.free:
            e = self.free.pop()
            (self.to[e], self.to[e ^ 1]) = (v, u)
            self.cw[e] = self.ccw[e] = e
            self.cw[e ^ 1] = self.ccw[e ^ 1] = e ^ 1
            self.alive[e >> 1] = 1
        else:
            e = len(self.to)
            self.to.extend((v, u))
            self.cw.extend((e, e + 1))
            self.ccw.extend((e, e + 1))
            self.alive.append(1)
        return (e, e ^ 1)

    def _erase(self, e):
        (cw, ccw) = (self.cw, self.ccw)
        for edge in (e, e ^ 1):
            cw[ccw[edge]] = cw[edge]
            ccw[cw[edge]] = ccw[edge]
        self.alive[e >> 1] = 0
        self.free.append(e & -2)

    def _after_ccw(self, e, at):
        (cw, ccw) = (self.cw, self.ccw)
        ccw[e] = ccw[at]
        cw[ccw[at]] = e
        cw[e] = at
        ccw[at] = e

    def _after_cw(self, e, at):
        (cw, ccw) = (self.cw, self.ccw)
        cw[e] = cw[at]
        ccw[cw[at]] = e
        ccw[e] = at
        cw[at] = e

    def _cross(self, a, b, c):
        (x, y) = (self.x, self.y)
        return (x[b] - x[a]) * (y[c] - y[a]) - (y[b] - y[a]) * (x[c] - x[a])

    def _inside(self, a, b, c, d):
        (x, y) = (self.x, self.y)
        (ax, ay) = (x[a] - x[d], y[a] - y[d])
        (bx, by) = (x[b] - x[d], y[b] - y[d])
        (cx, cy) = (x[c] - x[d], y[c] - y[d])
        return (bx * cy - by * cx) * (ax * ax + ay * ay) + (cx * ay - cy * ax) * (bx * bx + by * by) + (ax * by - ay * bx) * (cx * cx + cy * cy) > 0

    def _extreme(self, a, ea, minimum):
        (best, edge) = (a, ea)
        (p, ep) = (self.to[ea], self.ccw[ea ^ 1])
        while ep != ea:
            if p < best if minimum else p > best:
                (best, edge) = (p, ep)
            (p, ep) = (self.to[ep], self.ccw[ep ^ 1])
        return (best, edge)

    def _bottom(self, a, ea, b, eb):
        (to, cw, ccw) = (self.to, self.cw, self.ccw)
        while True:
            ap = to[cw[ea]]
            if self._cross(b, a, ap) > 0:
                (a, ea) = (ap, cw[ea] ^ 1)
                continue
            bp = to[eb]
            if self._cross(a, b, bp) < 0:
                (b, eb) = (bp, ccw[eb ^ 1])
                continue
            return (a, ea, b, eb)

    def _merge(self, a, ea, b, eb):
        (to, cw, ccw) = (self.to, self.cw, self.ccw)
        (a, ea) = self._extreme(a, ea, False)
        (b, eb) = self._extreme(b, eb, True)
        (al, eal, bl, ebl) = self._bottom(a, ea, b, eb)
        (bu, ebu, au, eau) = self._bottom(b, eb, a, ea)
        (ebl, ebu) = (cw[ebl], cw[ebu])
        (abl, bal) = self._new(al, bl)
        self._after_cw(abl, eal)
        self._after_ccw(bal, ebl)
        if al == au:
            eau = abl
        if bl == bu:
            ebu = bal
        (ap, eap, bp, ebp) = (al, eal, bl, ebl)
        while ap != au or bp != bu:
            (a2, b2) = (to[eap], to[ebp])
            (na, nb) = (ccw[eap], cw[ebp])
            if eap != eau and na != abl and self._inside(ap, bp, a2, to[na]):
                self._erase(eap)
                eap = na
                continue
            if ebp != ebu and nb != bal and self._inside(b2, ap, bp, to[nb]):
                self._erase(ebp)
                ebp = nb
                continue
            choose_a = ebp == ebu
            if eap != eau and ebp != ebu:
                if self._cross(ap, bp, b2) < 0:
                    choose_a = True
                elif self._cross(a2, ap, bp) < 0:
                    choose_a = False
                else:
                    choose_a = self._inside(ap, bp, b2, a2)
            if choose_a:
                na = ccw[eap ^ 1]
                (ab, ba) = self._new(a2, bp)
                self._after_cw(ab, na)
                self._after_ccw(ba, ebp)
                (ap, eap) = (a2, na)
            else:
                nb = cw[ebp ^ 1]
                (ba, ab) = self._new(b2, ap)
                self._after_ccw(ba, nb)
                self._after_cw(ab, eap)
                (bp, ebp) = (b2, nb)
        return (al, abl)

    def build(self):
        tasks = [(0, len(self.x), False)]
        results = []
        while tasks:
            (l, r, merge) = tasks.pop()
            if merge:
                (b, eb) = results.pop()
                (a, ea) = results.pop()
                results.append(self._merge(a, ea, b, eb))
            elif r - l <= 3:
                (uv, vu) = self._new(l, l + 1)
                if r - l == 2:
                    results.append((l, uv))
                    continue
                (vw, wv) = self._new(l + 1, l + 2)
                cross = self._cross(l, l + 1, l + 2)
                if cross == 0:
                    self._after_ccw(vu, vw)
                else:
                    (uw, wu) = self._new(l, l + 2)
                    insert = self._after_cw if cross > 0 else self._after_ccw
                    insert(uv, uw)
                    insert(vw, vu)
                    insert(wu, wv)
                results.append((l + 1, vu) if cross < 0 else (l, uv))
            else:
                m = l + r >> 1
                tasks.extend(((l, r, True), (m, r, False), (l, m, False)))

def delaunay_edges(points):
    """整数座標のドロネー分割の辺を入力点の番号の組で返す。時間O(N log N)、空間O(N)。"""
    order = sorted(range(len(points)), key=points.__getitem__)
    (unique, ids, result) = ([], [], [])
    for i in order:
        point = points[i]
        if unique and point == unique[-1]:
            result.append((ids[-1], i))
        else:
            unique.append(point)
            ids.append(i)
    if len(unique) >= 2:
        tree = _geometry_delaunay_Triangulation(unique)
        tree.build()
        to = tree.to
        result.extend(((ids[to[e]], ids[to[e ^ 1]]) for e in range(0, len(to), 2) if tree.alive[e >> 1]))
    return result
'平面上の点をユークリッド距離の合計が最小になる木で結ぶ。'

def euclidean_mst(points):
    """最小全域木の辺を入力点の番号の組で返す。時間O(N log N)、追加空間O(N)。"""
    edges = delaunay_edges(points)
    (x, y) = ([p[0] for p in points], [p[1] for p in points])
    edges.sort(key=lambda e: (x[e[0]] - x[e[1]]) ** 2 + (y[e[0]] - y[e[1]]) ** 2)
    parent = [-1] * len(points)
    result = []
    for (u, v) in edges:
        (a, b) = (u, v)
        while parent[a] >= 0:
            if parent[parent[a]] >= 0:
                parent[a] = parent[parent[a]]
            a = parent[a]
        while parent[b] >= 0:
            if parent[parent[b]] >= 0:
                parent[b] = parent[parent[b]]
            b = parent[b]
        if a == b:
            continue
        if parent[a] > parent[b]:
            (a, b) = (b, a)
        parent[a] += parent[b]
        parent[b] = a
        result.append((u, v))
        if len(result) == len(points) - 1:
            break
    return result
import sys
input = sys.stdin.buffer.readline
n = int(input())
points = [tuple(map(int, input().split())) for _ in range(n)]
sys.stdout.write('\n'.join((str(u) + ' ' + str(v) for (u, v) in euclidean_mst(points))))
