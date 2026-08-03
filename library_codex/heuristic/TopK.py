"""評価値が上位k件に入る要素だけを保持する。"""

class TopK:
    __slots__ = ("k", "hash_function", "values")

    def __init__(self, count, hash_function=hash):
        if count < 0:
            raise ValueError("count must be nonnegative")
        self.k = count
        self.hash_function = hash_function
        self.values = {}

    def insert(self, value):
        key = self.hash_function(value)
        old = self.values.get(key)
        if old is None or value < old:
            self.values[key] = value
        if len(self.values) >= max(1, self.k << 1):
            self.normalize()

    def normalize(self):
        if len(self.values) > self.k:
            selected = sorted(self.values.items(), key=lambda item: item[1])[:self.k]
            self.values = dict(selected)

    def get(self):
        self.normalize()
        return sorted(self.values.values())

