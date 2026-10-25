"""左の子孫を参照する結合処理で、一点更新と半開区間の集約を行う。"""


class SegTreeTraversal:
    __slots__ = ("n", "size", "data", "merge", "identity")

    def __init__(self, merge, identity, values, *, storage=None):
        if isinstance(values, int):
            n = values
            if n < 0:
                raise ValueError("negative length")
            values = None
        else:
            if not hasattr(values, "__len__"):
                values = list(values)
            n = len(values)
        size = 1 << (n - 1).bit_length() if n else 1
        data = [identity] * (size << 1) if storage is None else storage(size << 1, identity)
        if len(data) != size << 1:
            raise ValueError("storage has incorrect length")
        if values is not None:
            for index, value in enumerate(values):
                data[size + index] = value
        for node in range(size - 1, 0, -1):
            data[node] = merge(data, node << 1, data[node << 1 | 1])
        self.n = n
        self.size = size
        self.data = data
        self.merge = merge
        self.identity = identity

    def set(self, index, value):
        if not 0 <= index < self.n:
            raise IndexError("index outside array")
        data = self.data
        merge = self.merge
        node = self.size + index
        data[node] = value
        node >>= 1
        while node:
            data[node] = merge(data, node << 1, data[node << 1 | 1])
            node >>= 1

    def get(self, index):
        if not 0 <= index < self.n:
            raise IndexError("index outside array")
        return self.data[self.size + index]

    def prod(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open range")
        left += self.size
        right += self.size
        data = self.data
        merge = self.merge
        result = self.identity
        while left < right:
            height = min((right & -right).bit_length(), (right - left).bit_length()) - 1
            result = merge(data, (right >> height) - 1, result)
            right -= 1 << height
        return result

    def all_prod(self):
        return self.data[1]

    def tolist(self):
        data = self.data
        size = self.size
        return [data[size + index] for index in range(self.n)]

    def __len__(self):
        return self.n

    def __str__(self):
        return str(self.tolist())

    def __repr__(self):
        return "SegTreeTraversal(%r)" % self.tolist()
