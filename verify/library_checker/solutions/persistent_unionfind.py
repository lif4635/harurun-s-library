class PersistentArray:
    __slots__ = ('n', 'default', 'shift', 'branch', 'mask', 'height', 'pool', 'roots')

    def __init__(self, a_or_n, default=0, shift=2):
        assert shift > 0
        if isinstance(a_or_n, int):
            n = a_or_n
            values = None
        else:
            values = list(a_or_n)
            n = len(values)
        assert n >= 0
        branch = 1 << shift
        height = max(1, ((n - 1).bit_length() + shift - 1) // shift)
        pool = [0] * branch
        if values is None or n == 0:
            root = 0
        else:
            level = []
            for left in range(0, n, branch):
                node = values[left:left + branch]
                node += [default] * (branch - len(node))
                pool.extend(node)
                level.append((len(pool) >> shift) - 1)
            for _ in range(1, height):
                nxt = []
                for left in range(0, len(level), branch):
                    node = level[left:left + branch]
                    node += [0] * (branch - len(node))
                    pool.extend(node)
                    nxt.append((len(pool) >> shift) - 1)
                level = nxt
            root = level[0]
        self.n = n
        self.default = default
        self.shift = shift
        self.branch = branch
        self.mask = branch - 1
        self.height = height
        self.pool = pool
        self.roots = [root]

    def get_root(self, root, index):
        assert 0 <= index < self.n
        pool = self.pool
        shift = self.shift
        mask = self.mask
        for level in range(self.height - 1, 0, -1):
            if root == 0:
                return self.default
            root = pool[(root << shift) + (index >> level * shift & mask)]
        return self.default if root == 0 else pool[(root << shift) + (index & mask)]

    def get(self, index, version=-1):
        return self.get_root(self.roots[version], index)

    def update_root(self, root, index, value):
        assert 0 <= index < self.n
        pool = self.pool
        shift = self.shift
        mask = self.mask
        branch = self.branch
        path = []
        for level in range(self.height - 1, 0, -1):
            pos = index >> level * shift & mask
            path.append((root, pos))
            root = pool[(root << shift) + pos] if root else 0
        if root:
            left = root << shift
            node = pool[left:left + branch]
        else:
            node = [self.default] * branch
        node[index & mask] = value
        pool.extend(node)
        child = (len(pool) >> shift) - 1
        for (root, pos) in reversed(path):
            if root:
                left = root << shift
                node = pool[left:left + branch]
            else:
                node = [0] * branch
            node[pos] = child
            pool.extend(node)
            child = (len(pool) >> shift) - 1
        return child

    def set(self, index, value, version=-1):
        root = self.update_root(self.roots[version], index, value)
        self.roots.append(root)
        return len(self.roots) - 1
    update = set

    def fork(self, version=-1):
        self.roots.append(self.roots[version])
        return len(self.roots) - 1

    def tolist(self, version=-1):
        root = self.roots[version]
        return [self.get_root(root, i) for i in range(self.n)]

    def node_count(self):
        return len(self.pool) // self.branch - 1

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return 'PersistentArray(%r)' % self.tolist()

class PersistentUnionFind:
    __slots__ = ('n', 'data', 'roots', 'component_count')

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
        return (x, value)

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
        (x, sx) = self._leader_size(root, x)
        (y, sy) = self._leader_size(root, y)
        count = self.component_count[version]
        if x != y:
            if sx > sy:
                (x, y) = (y, x)
                (sx, sy) = (sy, sx)
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
import sys

def main():
    read = sys.stdin.buffer.readline
    (n, q) = map(int, read().split())
    tree = PersistentUnionFind(n)
    versions = [0] * (q + 1)
    answer = []
    for i in range(q):
        (kind, version, u, v) = map(int, read().split())
        if kind == 0:
            versions[i + 1] = tree.unite(u, v, versions[version + 1])
        else:
            answer.append(str(int(tree.same(u, v, versions[version + 1]))))
    sys.stdout.write('\n'.join(answer))
if __name__ == '__main__':
    main()
