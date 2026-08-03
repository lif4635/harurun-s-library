"""queue全体のmonoid積をpush・popと同じ償却計算量で保つSWAG。"""

class SWAGQueue:
    __slots__ = ("op", "identity", "front", "back")

    def __init__(self, op, identity):
        self.op = op
        self.identity = identity
        self.front = []
        self.back = []

    def append(self, value):
        aggregate = value if not self.back else self.op(self.back[-1][1], value)
        self.back.append((value, aggregate))

    push = append

    def popleft(self):
        if not self.front:
            while self.back:
                value = self.back.pop()[0]
                aggregate = value if not self.front else self.op(value, self.front[-1][1])
                self.front.append((value, aggregate))
        if not self.front:
            raise IndexError("pop from empty SWAGQueue")
        return self.front.pop()[0]

    pop = popleft

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
