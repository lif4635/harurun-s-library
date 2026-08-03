"""過去versionを残したままappend・popleftできる永続queue。"""

class PersistentQueue:
    __slots__ = ("value", "parent", "up", "tail", "length")

    def __init__(self):
        self.value = []
        self.parent = []
        self.up = []
        self.tail = [-1]
        self.length = [0]

    def append(self, value, version=-1):
        version %= len(self.tail)
        parent = self.tail[version]
        node = len(self.value)
        self.value.append(value)
        self.parent.append(parent)
        ancestors = [parent]
        level = 0
        while ancestors[level] >= 0:
            previous = ancestors[level]
            row = self.up[previous]
            if level >= len(row):
                break
            ancestors.append(row[level])
            level += 1
        self.up.append(ancestors)
        self.tail.append(node)
        self.length.append(self.length[version] + 1)
        return len(self.tail) - 1

    push = append

    def popleft(self, version=-1):
        version %= len(self.tail)
        if self.length[version] == 0:
            raise IndexError("pop from empty PersistentQueue")
        self.tail.append(self.tail[version])
        self.length.append(self.length[version] - 1)
        return len(self.tail) - 1

    pop = popleft

    def front(self, version=-1):
        version %= len(self.tail)
        length = self.length[version]
        if length == 0:
            raise IndexError("front from empty PersistentQueue")
        node = self.tail[version]
        steps = length - 1
        bit = 0
        while steps:
            if steps & 1:
                node = self.up[node][bit]
            steps >>= 1
            bit += 1
        return self.value[node]

    def __len__(self):
        return self.length[-1]
