from library_codex.data_structure.PersistentArray import PersistentArray


class PersistentUnionFind:
    __slots__ = ("n", "data", "roots", "component_count")

    def __init__(self, n):
        assert n >= 0
        data = PersistentArray(n, -1, 2)
        self.n = n
        self.data = data
        self.roots = [data.roots[0]]
        self.component_count = [n]

    def _leader_size(self, root, x):
        data = self.data
        value = data.get_root(root, x)
        while value >= 0:
            x = value
            value = data.get_root(root, x)
        return x, value

    def leader(self, x, version=-1):
        return self._leader_size(self.roots[version], x)[0]

    root = leader
    find = leader

    def size(self, x, version=-1):
        return -self._leader_size(self.roots[version], x)[1]

    def same(self, x, y, version=-1):
        root = self.roots[version]
        return self._leader_size(root, x)[0] == self._leader_size(root, y)[0]

    def unite(self, x, y, version=-1):
        root = self.roots[version]
        x, sx = self._leader_size(root, x)
        y, sy = self._leader_size(root, y)
        count = self.component_count[version]
        if x != y:
            if sx > sy:
                x, y = y, x
                sx, sy = sy, sx
            root = self.data.update_root(root, x, sx + sy)
            root = self.data.update_root(root, y, x)
            count -= 1
        self.roots.append(root)
        self.component_count.append(count)
        return len(self.roots) - 1

    merge = unite

    def fork(self, version=-1):
        self.roots.append(self.roots[version])
        self.component_count.append(self.component_count[version])
        return len(self.roots) - 1

    def components(self, version=-1):
        return self.component_count[version]

    def groups(self, version=-1):
        res = {}
        for i in range(self.n):
            leader = self.leader(i, version)
            res.setdefault(leader, []).append(i)
        return list(res.values())
