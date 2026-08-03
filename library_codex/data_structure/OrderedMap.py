"""key順の探索・k番目・lower/upper boundを扱う順序付きmap。"""

from library_codex.data_structure.TreapSet import TreapSet

class OrderedMap:
    """Order-statistic map backed by the array-based iterative TreapSet."""

    __slots__ = ("keys", "values", "default_factory")

    def __init__(self, items=(), default_factory=lambda: None):
        self.keys = TreapSet()
        self.values = {}
        self.default_factory = default_factory
        for key, value in items:
            self[key] = value

    def __setitem__(self, key, value):
        self.keys.add(key)
        self.values[key] = value

    def __getitem__(self, key):
        if key not in self.values:
            self.keys.add(key)
            self.values[key] = self.default_factory()
        return self.values[key]

    def get(self, key, default=None):
        return self.values.get(key, default)

    def find(self, key):
        return (key, self.values[key]) if key in self.values else None

    def erase(self, key):
        if key not in self.values:
            return False
        del self.values[key]
        self.keys.discard(key)
        return True

    discard = erase

    def lower_bound(self, key):
        return self.keys.bisect_left(key)

    def upper_bound(self, key):
        return self.keys.bisect_right(key)

    def kth_element(self, index):
        key = self.keys.kth(index)
        return key, self.values[key]

    def count(self, key):
        return int(key in self.values)

    def __contains__(self, key):
        return key in self.values

    def __len__(self):
        return len(self.keys)

    def __iter__(self):
        return iter(self.keys)

    def items(self):
        for key in self.keys:
            yield key, self.values[key]

    def __str__(self):
        return str(dict(self.items()))

    def __repr__(self):
        return "OrderedMap(%r)" % dict(self.items())
