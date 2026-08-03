"""rollback可能な状態更新を使ってoffline区間queryを処理する。"""

class RollbackMo:
    """Mo ordering for data structures supporting snapshot and rollback."""

    __slots__ = ("n", "queries")

    def __init__(self, size):
        self.n = size
        self.queries = []

    def add(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open query")
        self.queries.append((left, right))
        return len(self.queries) - 1

    add_query = add

    def run(self, initialize, insert, snapshot, rollback, output):
        query_count = len(self.queries)
        width = max(1, int(self.n / max(1, query_count + 1) ** 0.5))
        order = sorted(range(query_count), key=lambda index: (
            self.queries[index][0] // width, self.queries[index][1]
        ))
        answers = [None] * query_count
        initialize()
        snapshot()
        for query in order:
            left, right = self.queries[query]
            if right - left < width:
                for index in range(left, right):
                    insert(index)
                answers[query] = output(query)
                rollback()
        last_block = -1
        right_endpoint = 0
        for query in order:
            left, right = self.queries[query]
            if right - left < width:
                continue
            block = left // width
            if block != last_block:
                initialize()
                last_block = block
                right_endpoint = min(self.n, (block + 1) * width)
            while right_endpoint < right:
                insert(right_endpoint)
                right_endpoint += 1
            snapshot()
            for index in range(min(self.n, (block + 1) * width) - 1,
                               left - 1, -1):
                insert(index)
            answers[query] = output(query)
            rollback()
        return answers

