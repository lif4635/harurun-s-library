"""過去時刻の連結性と成分サイズを問い合わせる部分永続Union-Find。"""

class PartialPersistentUnionFind:
    __slots__ = (
        "n", "parent", "parent_time", "size_time", "size_value", "last_time"
    )

    def __init__(self, size):
        self.n = size
        self.parent = [-1] * size
        self.parent_time = [1 << 60] * size
        self.size_time = [[-1] for _ in range(size)]
        self.size_value = [[1] for _ in range(size)]
        self.last_time = -1

    def find(self, node, time=None):
        if time is None:
            time = self.last_time
        parent = self.parent
        parent_time = self.parent_time
        while parent[node] >= 0 and parent_time[node] <= time:
            node = parent[node]
        return node

    leader = find

    def merge(self, first, second, time=None):
        if time is None:
            time = self.last_time + 1
        if time < self.last_time:
            raise ValueError("time must be nondecreasing")
        self.last_time = time
        first = self.find(first, time)
        second = self.find(second, time)
        if first == second:
            return False
        parent = self.parent
        if parent[first] > parent[second]:
            first, second = second, first
        parent[first] += parent[second]
        parent[second] = first
        self.parent_time[second] = time
        self.size_time[first].append(time)
        self.size_value[first].append(-parent[first])
        return True

    unite = merge

    def same(self, first, second, time=None):
        return self.find(first, time) == self.find(second, time)

    def size(self, node, time=None):
        from bisect import bisect_right

        if time is None:
            time = self.last_time
        root = self.find(node, time)
        index = bisect_right(self.size_time[root], time) - 1
        return self.size_value[root][index]

    def when_unite(self, first, second):
        if not self.same(first, second):
            return -1
        low = -1
        high = self.last_time
        while low + 1 < high:
            middle = (low + high) >> 1
            if self.same(first, second, middle):
                high = middle
            else:
                low = middle
        return high

    def size_ge(self, node, target):
        if target <= 1:
            return -1
        if self.size(node) < target:
            return -1
        low = -1
        high = self.last_time
        while low + 1 < high:
            middle = (low + high) >> 1
            if self.size(node, middle) >= target:
                high = middle
            else:
                low = middle
        return high
