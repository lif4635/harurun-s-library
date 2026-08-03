"""deque両端の追加・削除をしながら全体のmonoid積を保つSWAG。"""

class SWAGDeque:
    __slots__ = ("op", "identity", "front", "back")

    def __init__(self, op, identity):
        self.op = op
        self.identity = identity
        self.front = []
        self.back = []

    def appendleft(self, value):
        aggregate = value if not self.front else self.op(value, self.front[-1][1])
        self.front.append((value, aggregate))

    def append(self, value):
        aggregate = value if not self.back else self.op(self.back[-1][1], value)
        self.back.append((value, aggregate))

    push_front = appendleft
    push_back = append

    def _rebuild_front(self):
        values = [item[0] for item in self.back]
        split = (len(values) + 1) >> 1
        self.front = []
        for value in reversed(values[:split]):
            aggregate = value if not self.front else self.op(value, self.front[-1][1])
            self.front.append((value, aggregate))
        self.back = []
        for value in values[split:]:
            aggregate = value if not self.back else self.op(self.back[-1][1], value)
            self.back.append((value, aggregate))

    def _rebuild_back(self):
        values = [item[0] for item in reversed(self.front)]
        split = len(values) >> 1
        self.front = []
        for value in reversed(values[:split]):
            aggregate = value if not self.front else self.op(value, self.front[-1][1])
            self.front.append((value, aggregate))
        self.back = []
        for value in values[split:]:
            aggregate = value if not self.back else self.op(self.back[-1][1], value)
            self.back.append((value, aggregate))

    def popleft(self):
        if not self.front:
            if not self.back:
                raise IndexError("pop from empty SWAGDeque")
            self._rebuild_front()
        return self.front.pop()[0]

    def pop(self):
        if not self.back:
            if not self.front:
                raise IndexError("pop from empty SWAGDeque")
            self._rebuild_back()
        return self.back.pop()[0]

    pop_front = popleft
    pop_back = pop

    def fold(self):
        if not self.front:
            return self.back[-1][1] if self.back else self.identity
        if not self.back:
            return self.front[-1][1]
        return self.op(self.front[-1][1], self.back[-1][1])

    prod = fold
    query = fold

    def __len__(self):
        return len(self.front) + len(self.back)
