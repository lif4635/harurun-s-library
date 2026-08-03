"""Offline half-open range queries with Mo's algorithm."""


class Mo:
    """Order and execute offline range queries by moving two endpoints."""

    __slots__ = ("n", "queries", "block_size")

    def __init__(self, n, query_count=0, block_size=None):
        self.n = n
        self.queries = []
        self.block_size = block_size or max(1, int(n / max(1, query_count) ** 0.5))

    def add_query(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open query")
        self.queries.append((left, right, len(self.queries)))
        return len(self.queries) - 1

    def order(self):
        width = self.block_size
        return sorted(
            self.queries,
            key=lambda query: (
                query[0] // width,
                query[1] if (query[0] // width) & 1 == 0 else -query[1],
            ),
        )

    def run(self, add_left, add_right, remove_left, remove_right, get):
        answer = [None] * len(self.queries)
        left = right = 0
        for query_left, query_right, query_id in self.order():
            while query_left < left:
                left -= 1
                add_left(left)
            while right < query_right:
                add_right(right)
                right += 1
            while left < query_left:
                remove_left(left)
                left += 1
            while query_right < right:
                right -= 1
                remove_right(right)
            answer[query_id] = get()
        return answer
