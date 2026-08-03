"""順序・k番目・前後要素を対数時間で扱う乱択平衡二分探索木。"""

from operator import add

class TreapSet:
    __slots__ = (
        "root", "key", "priority", "left", "right", "parent", "size", "state"
    )

    def __init__(self, values=()):
        self.root = -1
        self.key = []
        self.priority = []
        self.left = []
        self.right = []
        self.parent = []
        self.size = []
        self.state = 0x9E3779B97F4A7C15
        for value in values:
            self.add(value)

    def _random(self):
        value = self.state
        value ^= value << 7 & ((1 << 64) - 1)
        value ^= value >> 9
        self.state = value
        return value

    def _new(self, key):
        node = len(self.key)
        self.key.append(key)
        self.priority.append(self._random())
        self.left.append(-1)
        self.right.append(-1)
        self.parent.append(-1)
        self.size.append(1)
        return node

    def _update(self, node):
        left = self.left[node]
        right = self.right[node]
        self.size[node] = 1 + (
            self.size[left] if left >= 0 else 0
        ) + (self.size[right] if right >= 0 else 0)

    def _update_up(self, node):
        while node >= 0:
            self._update(node)
            node = self.parent[node]

    def _rotate(self, node):
        parent = self.parent[node]
        grandparent = self.parent[parent]
        if self.left[parent] == node:
            middle = self.right[node]
            self.right[node] = parent
            self.left[parent] = middle
        else:
            middle = self.left[node]
            self.left[node] = parent
            self.right[parent] = middle
        if middle >= 0:
            self.parent[middle] = parent
        self.parent[parent] = node
        self.parent[node] = grandparent
        if grandparent < 0:
            self.root = node
        elif self.left[grandparent] == parent:
            self.left[grandparent] = node
        else:
            self.right[grandparent] = node
        self._update(parent)
        self._update(node)

    def _find(self, key):
        node = self.root
        while node >= 0:
            current = self.key[node]
            if key == current:
                return node
            node = self.left[node] if key < current else self.right[node]
        return -1

    def add(self, key):
        if self.root < 0:
            self.root = self._new(key)
            return True
        node = self.root
        while True:
            current = self.key[node]
            if key == current:
                return False
            if key < current:
                child = self.left[node]
                if child < 0:
                    child = self._new(key)
                    self.left[node] = child
                    self.parent[child] = node
                    break
            else:
                child = self.right[node]
                if child < 0:
                    child = self._new(key)
                    self.right[node] = child
                    self.parent[child] = node
                    break
            node = child
        self._update_up(node)
        while self.parent[child] >= 0 and self.priority[child] < self.priority[self.parent[child]]:
            self._rotate(child)
        self._update_up(self.parent[child])
        return True

    insert = add

    def discard(self, key):
        node = self._find(key)
        if node < 0:
            return False
        while self.left[node] >= 0 or self.right[node] >= 0:
            left = self.left[node]
            right = self.right[node]
            if right < 0 or (
                left >= 0 and self.priority[left] < self.priority[right]
            ):
                self._rotate(left)
            else:
                self._rotate(right)
        parent = self.parent[node]
        if parent < 0:
            self.root = -1
        elif self.left[parent] == node:
            self.left[parent] = -1
        else:
            self.right[parent] = -1
        self._update_up(parent)
        return True

    erase = discard

    def bisect_left(self, key):
        node = self.root
        result = 0
        while node >= 0:
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if self.key[node] < key:
                result += left_size + 1
                node = self.right[node]
            else:
                node = left
        return result

    lower_bound = bisect_left

    def bisect_right(self, key):
        node = self.root
        result = 0
        while node >= 0:
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if self.key[node] <= key:
                result += left_size + 1
                node = self.right[node]
            else:
                node = left
        return result

    upper_bound = bisect_right

    def kth(self, index):
        if index < 0 or index >= len(self):
            raise IndexError("kth index out of range")
        node = self.root
        while True:
            left = self.left[node]
            left_size = self.size[left] if left >= 0 else 0
            if index < left_size:
                node = left
            elif index == left_size:
                return self.key[node]
            else:
                index -= left_size + 1
                node = self.right[node]

    def ge(self, key, default=None):
        index = self.bisect_left(key)
        return self.kth(index) if index < len(self) else default

    def gt(self, key, default=None):
        index = self.bisect_right(key)
        return self.kth(index) if index < len(self) else default

    def le(self, key, default=None):
        index = self.bisect_right(key) - 1
        return self.kth(index) if index >= 0 else default

    def lt(self, key, default=None):
        index = self.bisect_left(key) - 1
        return self.kth(index) if index >= 0 else default

    def min(self):
        return self.kth(0)

    def max(self):
        return self.kth(len(self) - 1)

    def __contains__(self, key):
        return self._find(key) >= 0

    def __len__(self):
        root = self.root
        return self.size[root] if root >= 0 else 0

    def __iter__(self):
        stack = []
        node = self.root
        while stack or node >= 0:
            while node >= 0:
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            yield self.key[node]
            node = self.right[node]

    def tolist(self):
        """保持するkeyを昇順listで返す。O(N)。"""
        return list(self)

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "TreapSet(%r)" % self.tolist()
