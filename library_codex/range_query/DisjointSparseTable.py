class DisjointSparseTable:
    __slots__ = ("n", "op", "data")

    def __init__(self, op, lst):
        n = len(lst)
        h = max(1, (n - 1).bit_length())
        data = [None] * (n * h)
        data[:n] = lst

        for level in range(1, h):
            width = 1 << level
            step = width << 1
            base = level * n
            for left in range(0, n, step):
                mid = min(left + width, n)
                data[base + mid - 1] = lst[mid - 1]
                for i in range(mid - 2, left - 1, -1):
                    data[base + i] = op(lst[i], data[base + i + 1])

                right = min(mid + width, n)
                if mid < right:
                    data[base + mid] = lst[mid]
                    for i in range(mid + 1, right):
                        data[base + i] = op(data[base + i - 1], lst[i])

        self.n = n
        self.op = op
        self.data = data

    def prod(self, l, r):
        assert 0 <= l < r <= self.n
        if l + 1 == r:
            return self.data[l]
        level = (l ^ (r - 1)).bit_length() - 1
        base = level * self.n
        return self.op(self.data[base + l], self.data[base + r - 1])

    query = prod
