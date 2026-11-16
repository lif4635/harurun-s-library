"""一点代入と区間クエリを時系列で登録し、更新付きMoでまとめて答える。"""


class MoWithUpdates:
    """値の追加・削除・答え取得だけを指定して更新付き区間集計を行う。"""

    __slots__ = ("values", "updates", "queries", "_latest", "block_size")

    def __init__(self, values, block_size=None):
        if block_size is not None and block_size < 1:
            raise ValueError("block_size must be positive")
        self.values = list(values)
        self._latest = self.values.copy()
        self.updates = []
        self.queries = []
        self.block_size = block_size

    def set(self, index, value):
        """この時点以降のクエリに適用する一点代入を登録する。"""
        if not 0 <= index < len(self.values):
            raise IndexError("index out of range")
        self.updates.append((index, self._latest[index], value))
        self._latest[index] = value

    def query(self, left, right):
        """現在までの代入を反映した半開区間[left, right)を登録する。"""
        if not 0 <= left <= right <= len(self.values):
            raise IndexError("invalid half-open range")
        index = len(self.queries)
        self.queries.append((left, right, len(self.updates), index))
        return index

    def run(self, add, remove, get):
        """add(value)・remove(value)・get()で全クエリの答えを登録順に返す。"""
        queries = self.queries
        if not queries:
            return []
        n, count, changes = len(self.values), len(queries), len(self.updates)
        width = self.block_size
        if width is None:
            width = max(1, min(n, round((n * n * changes / count) ** (1 / 3)))) if changes else max(1, int(n / count ** 0.5))
        if changes:
            def key(query):
                left, right = query[0] // width, query[1] // width
                return left, -right if left & 1 else right, -query[2] if (left ^ right) & 1 else query[2]

            ordered = sorted(queries, key=key)
        else:
            ordered = sorted(queries, key=lambda q: (q[0] // width, -q[1] if q[0] // width & 1 else q[1]))
        values = self.values.copy()
        updates = self.updates
        answers = [None] * count
        left = right = time = 0
        for lo, hi, target, index in ordered:
            while time < target:
                position, old, new = updates[time]
                if left <= position < right:
                    remove(old)
                    add(new)
                values[position] = new
                time += 1
            while time > target:
                time -= 1
                position, old, new = updates[time]
                if left <= position < right:
                    remove(new)
                    add(old)
                values[position] = old
            while left > lo:
                left -= 1
                add(values[left])
            while right < hi:
                add(values[right])
                right += 1
            while left < lo:
                remove(values[left])
                left += 1
            while right > hi:
                right -= 1
                remove(values[right])
            answers[index] = get()
        while left < right:
            remove(values[left])
            left += 1
        return answers
