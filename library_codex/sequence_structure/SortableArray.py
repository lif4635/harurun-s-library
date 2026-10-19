"""区間をキーで並べ替えながら、値の更新と非可換な区間積を扱う。"""

from library_codex.ordered_set.FastSet import FastSet
from library_codex.segment_tree.SegTree import SegTree


class SortableArray:
    """相異なる整数キーと値の組を、現在の配列順で管理する。"""

    __slots__ = ("n", "op", "identity", "_keys", "_values", "_used", "_left",
                 "_right", "_size", "_priority", "_forward", "_backward",
                 "_roots", "_reverse", "_starts", "_seg")

    def __init__(self, op, identity, items):
        items = list(items)
        keys = [key for key, value in items]
        used = set(keys)
        if len(used) != len(keys):
            raise ValueError("keys must be distinct")
        self.n = n = len(items)
        self.op = op
        self.identity = identity
        self._keys = [0] + keys
        self._values = [identity] + [value for key, value in items]
        self._used = used
        self._left = [0] * (n + 1)
        self._right = [0] * (n + 1)
        self._size = [0] + [1] * n
        self._priority = [0]
        state = 712367821
        for _ in items:
            state ^= (state << 13) & 0xffffffff
            state ^= state >> 17
            state ^= (state << 5) & 0xffffffff
            self._priority.append(state)
        self._forward = self._values[:]
        self._backward = self._values[:]
        self._roots = list(range(1, n + 1))
        self._reverse = bytearray(n)
        self._starts = FastSet(n + 1, range(n + 1))
        self._seg = SegTree(op, identity, self._values[1:])

    def _pull(self, node):
        left = self._left[node]
        right = self._right[node]
        self._size[node] = self._size[left] + self._size[right] + 1
        op = self.op
        value = self._values[node]
        self._forward[node] = op(op(self._forward[left], value), self._forward[right])
        self._backward[node] = op(op(self._backward[right], value), self._backward[left])

    def _split(self, root, key, by_key=False):
        path = []
        left = self._left
        right = self._right
        sizes = self._size
        keys = self._keys
        while root:
            take = keys[root] < key if by_key else sizes[left[root]] < key
            if take:
                if not by_key:
                    key -= sizes[left[root]] + 1
                path.append(root)
                root = right[root]
            else:
                path.append(-root)
                root = left[root]
        first = second = 0
        for node in reversed(path):
            if node > 0:
                right[node] = first
                self._pull(node)
                first = node
            else:
                node = -node
                left[node] = second
                self._pull(node)
                second = node
        return first, second

    def _union(self, first, second):
        stack = [(first, second, False)]
        results = []
        left = self._left
        right = self._right
        priorities = self._priority
        while stack:
            a, b, finish = stack.pop()
            if finish:
                right[a] = results.pop()
                left[a] = results.pop()
                self._pull(a)
                results.append(a)
            elif not a or not b:
                results.append(a or b)
            else:
                if priorities[a] < priorities[b]:
                    a, b = b, a
                low, high = self._split(b, self._keys[a], True)
                stack.append((a, 0, True))
                stack.append((right[a], high, False))
                stack.append((left[a], low, False))
        return results[0]

    def _cut(self, index):
        if index in self._starts:
            return
        start = self._starts.prev(index)
        root = self._roots[start]
        reverse = self._reverse[start]
        count = index - start
        if reverse:
            count = self._size[root] - count
        first, second = self._split(root, count)
        if reverse:
            first, second = second, first
        self._roots[start] = first
        self._roots[index] = second
        self._reverse[index] = reverse
        self._starts.add(index)
        values = self._backward if reverse else self._forward
        self._seg.set(start, values[first])
        self._seg.set(index, values[second])

    def _range(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")

    def get(self, index):
        """現在のindex番目にある(key, value)を返す。"""
        if not 0 <= index < self.n:
            raise IndexError("index out of range")
        start = self._starts.prev(index)
        root = self._roots[start]
        rank = index - start
        if self._reverse[start]:
            rank = self._size[root] - 1 - rank
        while True:
            count = self._size[self._left[root]]
            if rank == count:
                return self._keys[root], self._values[root]
            if rank < count:
                root = self._left[root]
            else:
                rank -= count + 1
                root = self._right[root]

    def set(self, index, key, value):
        """現在のindex番目のキーと値を置き換える。"""
        old, _ = self.get(index)
        if key != old and key in self._used:
            raise ValueError("key is already present")
        self._cut(index)
        self._cut(index + 1)
        node = self._roots[index]
        self._used.remove(old)
        self._used.add(key)
        self._keys[node] = key
        self._values[node] = value
        self._forward[node] = self._backward[node] = value
        self._seg.set(index, value)

    def sort(self, left, right, reverse=False):
        """半開区間[left, right)をキーの昇順、reverse=Trueなら降順にする。"""
        self._range(left, right)
        if right - left <= 1:
            return
        self._cut(left)
        self._cut(right)
        root = self._roots[left]
        index = self._starts.next(left + 1)
        while index < right:
            root = self._union(root, self._roots[index])
            self._roots[index] = 0
            self._starts.discard(index)
            self._seg.set(index, self.identity)
            index = self._starts.next(index + 1)
        self._roots[left] = root
        self._reverse[left] = bool(reverse)
        self._seg.set(left, self._backward[root] if reverse else self._forward[root])

    def prod(self, left, right):
        """半開区間[left, right)の値を、現在の左から右への順でopで畳み込む。"""
        self._range(left, right)
        if left == right:
            return self.identity
        self._cut(left)
        self._cut(right)
        return self._seg.prod(left, right)

    def all_prod(self):
        """現在の配列全体の値を、左から右への順でopで畳み込んだ値を返す。"""
        return self._seg.all_prod()

    def tolist(self):
        """現在の配列順の(key, value)を並べたlistを返す。"""
        result = []
        start = self._starts.next(0)
        while start < self.n:
            root = self._roots[start]
            left, right = self._left, self._right
            if self._reverse[start]:
                left, right = right, left
            stack = []
            while root or stack:
                while root:
                    stack.append(root)
                    root = left[root]
                root = stack.pop()
                result.append((self._keys[root], self._values[root]))
                root = right[root]
            start = self._starts.next(start + 1)
        return result

    def __len__(self):
        return self.n

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "SortableArray(%r)" % self.tolist()
