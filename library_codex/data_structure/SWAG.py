import heapq


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


class ErasableHeap:
    __slots__ = ("heap", "erased", "sign", "size")

    def __init__(self, values=(), maximize=False):
        self.sign = -1 if maximize else 1
        self.heap = [self.sign * value for value in values]
        heapq.heapify(self.heap)
        self.erased = []
        self.size = len(self.heap)

    def _clean(self):
        heap = self.heap
        erased = self.erased
        while erased and heap and erased[0] == heap[0]:
            heapq.heappop(erased)
            heapq.heappop(heap)

    def push(self, value):
        heapq.heappush(self.heap, self.sign * value)
        self.size += 1

    def erase(self, value):
        heapq.heappush(self.erased, self.sign * value)
        self.size -= 1
        self._clean()

    remove = erase

    def top(self):
        self._clean()
        if not self.heap:
            raise IndexError("top from empty ErasableHeap")
        return self.sign * self.heap[0]

    def pop(self):
        value = self.top()
        heapq.heappop(self.heap)
        self.size -= 1
        self._clean()
        return value

    def __len__(self):
        return self.size
