class RadixHeap:
    __slots__ = ("buckets", "mins", "size", "last")

    def __init__(self):
        self.buckets = [[]]
        self.mins = [None]
        self.size = 0
        self.last = 0

    def push(self, key, value):
        assert key >= self.last
        b = (key ^ self.last).bit_length()
        buckets = self.buckets
        mins = self.mins
        while len(buckets) <= b:
            buckets.append([])
            mins.append(None)
        buckets[b].append((key, value))
        cur = mins[b]
        if cur is None or key < cur:
            mins[b] = key
        self.size += 1

    def _pull(self):
        buckets = self.buckets
        if buckets[0]:
            return
        i = 1
        while not buckets[i]:
            i += 1
        last = self.mins[i]
        self.last = last
        items = buckets[i]
        buckets[i] = []
        self.mins[i] = None
        mins = self.mins
        for key, value in items:
            b = (key ^ last).bit_length()
            buckets[b].append((key, value))
            cur = mins[b]
            if cur is None or key < cur:
                mins[b] = key

    def pop(self):
        assert self.size
        self._pull()
        self.size -= 1
        item = self.buckets[0].pop()
        if not self.buckets[0]:
            self.mins[0] = None
        return item

    def top(self):
        assert self.size
        i = 0
        buckets = self.buckets
        while not buckets[i]:
            i += 1
        key = self.mins[i]
        for item in reversed(buckets[i]):
            if item[0] == key:
                return item

    peek = top

    def empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def __bool__(self):
        return self.size != 0
