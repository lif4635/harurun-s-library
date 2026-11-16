"""過去の森から分岐して辺を変更し、向き付きの経路積を求める。"""

from operator import add
from library_codex.sequence_structure.PersistentArray import PersistentArray


class PersistentLinkCutTree:
    __slots__ = ("n", "op", "identity", "_storage", "_roots", "_snapshots", "_fields", "_loaded", "_touched", "_version_root")

    def __init__(self, values, op=add, identity=0, edges=()):
        values = list(values)
        self.n, self.op, self.identity = n, op, identity = len(values), op, identity
        degree, neighbors = [0] * n, [0] * n
        for u, v in edges:
            if not 0 <= u < n or not 0 <= v < n or u == v:
                raise ValueError("invalid forest edge")
            degree[u] += 1
            degree[v] += 1
            neighbors[u] ^= v
            neighbors[v] ^= u
        order = [v for v in range(n) if degree[v] <= 1]
        parent = [0] * (n + 1)
        for v in order:
            if degree[v]:
                p = neighbors[v]
                parent[v + 1] = p + 1
                degree[v] = 0
                neighbors[p] ^= v
                degree[p] -= 1
                if degree[p] == 1:
                    order.append(p)
        if len(order) != n:
            raise ValueError("edges must form a forest")
        self._snapshots = [[0] * (n + 1), [0] * (n + 1), parent, [0] + [1] * n, [0] * (n + 1), [identity] + values, [identity] + values, [identity] + values]
        self._fields = [field.copy() for field in self._snapshots]
        self._storage = PersistentArray(range(1, n + 1))
        self._roots = [self._storage.roots[0]]
        self._loaded = bytearray(n + 1)
        self._touched = []
        self._version_root = self._roots[0]

    def _vertex(self, vertex):
        if not 0 <= vertex < self.n:
            raise IndexError(vertex)
        return vertex + 1

    def _begin(self, version):
        root = self._roots[version]
        for v in self._touched:
            self._loaded[v] = 0
        self._touched.clear()
        self._version_root = root

    def _load(self, v):
        if v and not self._loaded[v]:
            record = self._storage.get_root(self._version_root, v - 1)
            for field, snapshots in zip(self._fields, self._snapshots):
                field[v] = snapshots[record]
            self._loaded[v] = 1
            self._touched.append(v)

    def _save(self):
        root = self._version_root
        for v in self._touched:
            record = len(self._snapshots[0])
            for field, snapshots in zip(self._fields, self._snapshots):
                snapshots.append(field[v])
            root = self._storage.update_root(root, v - 1, record)
        self._roots.append(root)
        return len(self._roots) - 1

    def _is_root(self, v):
        self._load(v)
        left, right, parent = self._fields[:3]
        p = parent[v]
        self._load(p)
        return not p or left[p] != v and right[p] != v

    def _flip(self, v):
        if v:
            self._load(v)
            left, right, _, _, reverse, _, forward, backward = self._fields
            left[v], right[v] = right[v], left[v]
            forward[v], backward[v] = backward[v], forward[v]
            reverse[v] ^= 1

    def _push(self, v):
        self._load(v)
        left, right, _, _, reverse, _, _, _ = self._fields
        if reverse[v]:
            self._flip(left[v])
            self._flip(right[v])
            reverse[v] = 0

    def _pull(self, v):
        left, right, _, size, _, value, forward, backward = self._fields
        a, b = left[v], right[v]
        self._load(a)
        self._load(b)
        size[v] = size[a] + size[b] + 1
        forward[v] = self.op(self.op(forward[a], value[v]), forward[b])
        backward[v] = self.op(self.op(backward[b], value[v]), backward[a])

    def _rotate(self, v):
        left, right, parent = self._fields[:3]
        p = parent[v]
        root = self._is_root(p)
        g = parent[p]
        d = right[p] == v
        child = left[v] if d else right[v]
        if not root:
            (right if right[g] == p else left)[g] = v
        parent[v] = g
        (right if d else left)[p] = child
        if child:
            self._load(child)
            parent[child] = p
        (left if d else right)[v] = p
        parent[p] = v
        self._pull(p)
        self._pull(v)

    def _splay(self, v):
        path, x = [v], v
        parent = self._fields[2]
        while not self._is_root(x):
            x = parent[x]
            path.append(x)
        for x in reversed(path):
            self._push(x)
        left = self._fields[0]
        while not self._is_root(v):
            p, g = parent[v], parent[parent[v]]
            if not self._is_root(p):
                self._rotate(p if (left[p] == v) == (left[g] == p) else v)
            self._rotate(v)

    def _access(self, v):
        last, x = 0, v
        right, parent = self._fields[1:3]
        while x:
            self._splay(x)
            right[x] = last
            if last:
                parent[last] = x
            self._pull(x)
            last = x
            x = parent[x]
        self._splay(v)
        return last

    def _make_root(self, v):
        self._access(v)
        self._flip(v)

    def _expose(self, u, v):
        self._make_root(u)
        self._access(v)
        if u != v and self._fields[2][u] == 0:
            raise ValueError("vertices are disconnected")

    def get(self, vertex, version=-1):
        v = self._vertex(vertex)
        record = self._storage.get_root(self._roots[version], v - 1)
        return self._snapshots[5][record]

    def set(self, vertex, value, version=-1):
        v = self._vertex(vertex)
        self._begin(version)
        self._access(v)
        self._fields[5][v] = value
        self._pull(v)
        return self._save()

    def link(self, u, v, version=-1):
        u, v = self._vertex(u), self._vertex(v)
        self._begin(version)
        self._make_root(u)
        self._access(v)
        success = u != v and self._fields[2][u] == 0
        if success:
            self._fields[2][u] = v
        return self._save(), success

    def cut(self, u, v, version=-1):
        u, v = self._vertex(u), self._vertex(v)
        self._begin(version)
        self._make_root(u)
        self._access(v)
        left, right, parent = self._fields[:3]
        success = u != v and left[v] == u and right[u] == 0
        if success:
            left[v] = parent[u] = 0
            self._pull(v)
        return self._save(), success

    def same(self, u, v, version=-1):
        u, v = self._vertex(u), self._vertex(v)
        self._begin(version)
        self._access(u)
        self._access(v)
        answer = u == v or self._fields[2][u] != 0
        return self._save(), answer

    def prod(self, u, v, version=-1):
        u, v = self._vertex(u), self._vertex(v)
        self._begin(version)
        self._expose(u, v)
        answer = self._fields[6][v]
        return self._save(), answer

    def path_size(self, u, v, version=-1):
        u, v = self._vertex(u), self._vertex(v)
        self._begin(version)
        self._expose(u, v)
        answer = self._fields[3][v]
        return self._save(), answer

    def jump(self, u, v, k, version=-1):
        u, v = self._vertex(u), self._vertex(v)
        self._begin(version)
        self._expose(u, v)
        left, right, _, size, _, _, _, _ = self._fields
        answer = -1
        if 0 <= k < size[v]:
            while True:
                self._push(v)
                self._load(left[v])
                count = size[left[v]]
                if k == count:
                    break
                if k < count:
                    v = left[v]
                else:
                    k -= count + 1
                    v = right[v]
            self._splay(v)
            answer = v - 1
        return self._save(), answer

    def tolist(self, version=-1):
        root = self._roots[version]
        return [self._snapshots[5][self._storage.get_root(root, v)] for v in range(self.n)]

    def node_count(self):
        return self._storage.node_count(), len(self._snapshots[0]) - 1

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "PersistentLinkCutTree(%r)" % self.tolist()
