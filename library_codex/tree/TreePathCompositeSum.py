"""辺の一次関数を通して各頂点の値を集めた総和を、更新と根の変更に対応して求める。"""

from library_codex.tree.StaticTopTree import StaticTopTree


class TreePathCompositeSum:
    """固定された木で、頂点値・辺の一次関数を置換し、任意の頂点への合成和を求める。"""

    __slots__ = ("n", "mod", "_tree", "_values", "_edges", "_child",
                 "_a", "_bf", "_br", "_sf", "_sr", "_count")

    def __init__(self, values, edges, mod=998244353):
        if mod < 1:
            raise ValueError("mod must be positive")
        self.n = n = len(values)
        if n == 0:
            raise ValueError("tree must be nonempty")
        edges = list(edges)
        if len(edges) != n - 1:
            raise ValueError("a tree must have n - 1 edges")
        graph = [[] for _ in range(n)]
        for u, v, b, c in edges:
            if not (0 <= u < n and 0 <= v < n):
                raise IndexError("vertex out of range")
            graph[u].append(v)
            graph[v].append(u)
        self.mod = mod
        self._tree = tree = StaticTopTree(graph)
        self._values = [value % mod for value in values]
        self._edges = [(u, v, b % mod, c % mod) for u, v, b, c in edges]
        self._child = [v if tree.tree_parent[v] == u else u for u, v, b, c in edges]
        size = len(tree.parent)
        self._a = [1 % mod] * size
        self._bf = [0] * size
        self._br = [0] * size
        self._sf = self._values + [0] * (size - n)
        self._sr = self._sf[:]
        self._count = [1] * size
        for i, node in enumerate(self._child):
            _, _, b, c = self._edges[i]
            self._a[node] = b
            self._bf[node] = self._br[node] = c
            self._sf[node] = (b * self._values[node] + c) % mod
        for node in range(n, size):
            self._pull(node)

    def _pull(self, node):
        tree = self._tree
        left, right = tree.left[node], tree.right[node]
        a, bf, br, sf, sr, count = self._a, self._bf, self._br, self._sf, self._sr, self._count
        mod = self.mod
        count[node] = count[left] + count[right]
        if tree.type[node] == 1:
            a[node] = a[left] * a[right] % mod
            bf[node] = (a[left] * bf[right] + bf[left]) % mod
            br[node] = (a[right] * br[left] + br[right]) % mod
            sf[node] = (sf[left] + a[left] * sf[right] + bf[left] * count[right]) % mod
            sr[node] = (sr[right] + a[right] * sr[left] + br[right] * count[left]) % mod
        else:
            a[node], bf[node], br[node] = a[left], bf[left], br[left]
            sf[node] = (sf[left] + sf[right]) % mod
            sr[node] = (sr[left] + a[left] * sf[right] + br[left] * count[right]) % mod

    def _update(self, node):
        self._sr[node] = self._values[node]
        self._sf[node] = (self._a[node] * self._values[node] + self._bf[node]) % self.mod
        parent = self._tree.parent
        node = parent[node]
        while node >= 0:
            self._pull(node)
            node = parent[node]

    def set(self, vertex, value):
        """vertexの値をvalueへ置き換える。"""
        if not 0 <= vertex < self.n:
            raise IndexError("vertex out of range")
        self._values[vertex] = value % self.mod
        self._update(vertex)

    def set_edge(self, edge, b, c):
        """入力順のedge番目の辺を、両方向ともxをb*x+cへ写す一次関数に置き換える。"""
        if not 0 <= edge < self.n - 1:
            raise IndexError("edge out of range")
        u, v, _, _ = self._edges[edge]
        b, c = b % self.mod, c % self.mod
        self._edges[edge] = u, v, b, c
        node = self._child[edge]
        self._a[node] = b
        self._bf[node] = self._br[node] = c
        self._update(node)

    def query(self, root):
        """各頂点からrootへ向かう経路の順に辺の一次関数を適用し、その結果を合計する。"""
        if not 0 <= root < self.n:
            raise IndexError("vertex out of range")
        tree = self._tree
        a, bf, br, sf, sr, count = self._a, self._bf, self._br, self._sf, self._sr, self._count
        mod = self.mod
        current = root
        fa, fb, fs, fc = a[root], br[root], sr[root], 1
        sa, sb, ss, sc = 1, 0, 0, 0
        ta, tb, ts = 1, 0, 0
        while tree.parent[current] >= 0:
            parent = tree.parent[current]
            left, right = tree.left[parent], tree.right[parent]
            if tree.type[parent] == 1:
                if current == left:
                    ss = (ss + sa * sf[right] + sb * count[right]) % mod
                    sb = (sa * bf[right] + sb) % mod
                    sa = sa * a[right] % mod
                    sc += count[right]
                else:
                    fs = (fs + fa * sr[left] + fb * count[left]) % mod
                    fb = (fa * br[left] + fb) % mod
                    fa = fa * a[left] % mod
                    fc += count[left]
            elif current == left:
                fs = (fs + fa * sf[right] + fb * count[right]) % mod
                fc += count[right]
            else:
                ts = (ts + ta * (fs + ss) + tb * (fc + sc)) % mod
                tb = (ta * fb + tb) % mod
                ta = ta * fa % mod
                fa, fb, fs, fc = 1, 0, 0, 0
                sa, sb, ss, sc = a[left], bf[left], sf[left], count[left]
            current = parent
        return (ts + ta * (fs + ss) + tb * (fc + sc)) % mod

    def tolist(self):
        """現在の頂点値を頂点番号順の新しいlistで返す。"""
        return self._values[:]

    def edges(self):
        """入力順の(u, v, b, c)を並べた新しいlistを返す。"""
        return self._edges[:]

    def __str__(self):
        return str((self.tolist(), self.edges()))

    def __repr__(self):
        return "TreePathCompositeSum(%r, %r, mod=%r)" % (self.tolist(), self.edges(), self.mod)
