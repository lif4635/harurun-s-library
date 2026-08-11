"""削除と前後の生存要素検索に特化した整数集合。"""


class DecrementalSet:
    """初期状態で0以上size未満の整数をすべて保持する削除専用集合。"""

    __slots__ = ("n", "forward", "backward", "active", "size")

    def __init__(self, size):
        if size < 0:
            raise ValueError("size must be nonnegative")
        self.n = size
        self.forward = list(range(size + 1))
        self.backward = list(range(size + 1))
        self.active = bytearray(b"\1") * size
        self.size = size

    @staticmethod
    def _find(parent, node):
        root = node
        while parent[root] != root:
            root = parent[root]
        while node != root:
            next_node = parent[node]
            parent[node] = root
            node = next_node
        return root

    def discard(self, value):
        if not 0 <= value < self.n or not self.active[value]:
            return False
        self.active[value] = 0
        self.size -= 1
        self.forward[value] = self._find(self.forward, value + 1)
        reversed_index = self.n - 1 - value
        self.backward[reversed_index] = self._find(
            self.backward, reversed_index + 1
        )
        return True

    def next(self, value):
        if value < 0:
            value = 0
        if value >= self.n:
            return -1
        result = self._find(self.forward, value)
        return result if result < self.n else -1

    def prev(self, value):
        if value >= self.n:
            value = self.n - 1
        if value < 0:
            return -1
        result = self._find(self.backward, self.n - 1 - value)
        return -1 if result == self.n else self.n - 1 - result

    def tolist(self):
        result = []
        value = self.next(0)
        while value >= 0:
            result.append(value)
            value = self.next(value + 1)
        return result

    def __contains__(self, value):
        return 0 <= value < self.n and bool(self.active[value])

    def __len__(self):
        return self.size

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "DecrementalSet(%r)" % self.tolist()
