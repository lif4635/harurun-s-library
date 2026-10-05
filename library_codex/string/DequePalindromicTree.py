"""両端で追加・削除する列の回文の種類数と最長回文接頭辞・接尾辞を保つ。"""


class DequePalindromicTree:
    __slots__ = (
        "_data", "_prefix", "_suffix", "_head", "_size", "_mask",
        "_length", "_link", "_quick", "_parent", "_count", "_children",
        "_edges", "_free", "_distinct",
    )

    def __init__(self, sequence=()):
        self._data = [None] * 8
        self._prefix = [1] * 8
        self._suffix = [1] * 8
        self._head = self._size = self._distinct = 0
        self._mask = 7
        self._length = [-1, 0]
        self._link = [0, 0]
        self._quick = [0, 0]
        self._parent = [0, 0]
        self._count = [0, 0]
        self._children = [0, 0]
        self._edges = {}
        self._free = []
        for symbol in sequence:
            self.append(symbol)

    def __len__(self):
        return self._size

    @property
    def distinct_count(self):
        return self._distinct

    @property
    def longest_prefix(self):
        return self._length[self._prefix[self._head]] if self._size else 0

    @property
    def longest_suffix(self):
        return self._length[self._suffix[(self._head + self._size - 1) & self._mask]] if self._size else 0

    def _grow(self):
        size = self._size
        head = self._head
        self._data = self._data[head:] + self._data[:head] + [None] * size
        self._prefix = self._prefix[head:] + self._prefix[:head] + [1] * size
        self._suffix = self._suffix[head:] + self._suffix[:head] + [1] * size
        self._head = 0
        self._mask = 2 * size - 1

    def _find(self, symbol, node, front):
        length = self._length
        link = self._link
        quick = self._quick
        data = self._data
        mask = self._mask
        size = self._size
        start = self._head if front else self._head + size - 1
        direction = 1 if front else -1
        while True:
            span = length[node]
            if span == -1 or (span < size and data[(start + direction * span) & mask] == symbol):
                return node
            suffix = link[node]
            span = length[suffix]
            if span == -1 or data[(start + direction * span) & mask] == symbol:
                return suffix
            node = quick[node]

    def _push(self, symbol, front):
        hash(symbol)
        if self._size == len(self._data):
            self._grow()
        size = self._size
        head = self._head
        mask = self._mask
        length = self._length
        link = self._link
        if size:
            last = self._prefix[head] if front else self._suffix[(head + size - 1) & mask]
            parent = self._find(symbol, last, front)
        else:
            parent = 0
        key = (parent, symbol)
        node = self._edges.get(key, -1)
        created = node == -1
        if created:
            suffix = 1 if parent == 0 else self._edges[self._find(symbol, link[parent], front), symbol]
            if self._free:
                node = self._free.pop()
                length[node] = length[parent] + 2
                link[node] = suffix
                self._parent[node] = parent
            else:
                node = len(length)
                length.append(length[parent] + 2)
                link.append(suffix)
                self._quick.append(0)
                self._parent.append(parent)
                self._count.append(0)
                self._children.append(0)
            self._children[suffix] += 1
            self._edges[key] = node
            self._distinct += 1
        else:
            suffix = link[node]
        if front:
            head = (head - 1) & mask
            self._head = head
            slot = head
        else:
            slot = (head + size) & mask
        self._data[slot] = symbol
        self._prefix[slot] = self._suffix[slot] = 1
        size += 1
        self._size = size
        if created:
            shorter = link[suffix]
            start = head if front else head + size - 1
            direction = 1 if front else -1
            if shorter != 0 and self._data[(start + direction * length[suffix]) & mask] == self._data[(start + direction * length[shorter]) & mask]:
                self._quick[node] = self._quick[suffix]
            else:
                self._quick[node] = shorter
        if front:
            self._prefix[head] = node
            self._suffix[(head + length[node] - 1) & mask] = node
            slot = (head + length[node] - length[suffix]) & mask
            if length[suffix] and self._prefix[slot] == suffix:
                self._prefix[slot] = 1
        else:
            self._suffix[(head + size - 1) & mask] = node
            self._prefix[(head + size - length[node]) & mask] = node
            slot = (head + size - length[node] + length[suffix] - 1) & mask
            if length[suffix] and self._suffix[slot] == suffix:
                self._suffix[slot] = 1
        self._count[node] += 1

    def append(self, symbol):
        self._push(symbol, False)

    def appendleft(self, symbol):
        self._push(symbol, True)

    def _pop(self, front):
        size = self._size
        if not size:
            raise IndexError("pop from an empty palindromic deque")
        head = self._head
        mask = self._mask
        length = self._length
        slot = head if front else (head + size - 1) & mask
        node = self._prefix[slot] if front else self._suffix[slot]
        symbol = self._data[slot]
        suffix = self._link[node]
        if front:
            start = (head + length[node] - length[suffix]) & mask
            end = (head + length[node] - 1) & mask
            if length[node] >= 2 and length[self._prefix[start]] < length[suffix]:
                self._prefix[start] = self._suffix[end] = suffix
            else:
                self._suffix[end] = 1
            self._head = (head + 1) & mask
        else:
            start = (head + size - length[node]) & mask
            end = (head + size - length[node] + length[suffix] - 1) & mask
            if length[node] >= 2 and length[self._suffix[end]] < length[suffix]:
                self._suffix[end] = self._prefix[start] = suffix
            else:
                self._prefix[start] = 1
        self._count[node] -= 1
        if self._count[node] == 0 and self._children[node] == 0:
            del self._edges[self._parent[node], symbol]
            self._children[suffix] -= 1
            self._free.append(node)
            self._distinct -= 1
        self._data[slot] = None
        self._prefix[slot] = self._suffix[slot] = 1
        self._size -= 1
        return symbol

    def pop(self):
        return self._pop(False)

    def popleft(self):
        return self._pop(True)

    def query(self):
        if not self._size:
            return 0, 0, 0
        return self._distinct, self._length[self._prefix[self._head]], self._length[self._suffix[(self._head + self._size - 1) & self._mask]]

    def tolist(self):
        return [self._data[(self._head + i) & self._mask] for i in range(self._size)]

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "DequePalindromicTree(" + repr(self.tolist()) + ")"
