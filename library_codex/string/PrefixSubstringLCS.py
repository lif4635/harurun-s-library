class PrefixSubstringLCS:
    __slots__ = ("first", "second", "n", "m", "queries", "query_count")

    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.n = len(first)
        self.m = len(second)
        self.queries = [None] * self.n
        self.query_count = 0

    def add(self, prefix_end, left, right):
        if not (0 <= prefix_end <= self.n):
            raise IndexError("prefix end is out of range")
        if not (0 <= left <= right <= self.m):
            raise IndexError("substring range is out of range")
        query_id = self.query_count
        self.query_count += 1
        if prefix_end == 0 or right == 0 or left == right:
            return query_id
        row = self.queries[prefix_end - 1]
        if row is None:
            row = {}
            self.queries[prefix_end - 1] = row
        bucket = row.get(right - 1)
        query = (left, query_id)
        if bucket is None:
            row[right - 1] = [query]
        else:
            bucket.append(query)
        return query_id

    add_query = add

    def run(self):
        width = self.m
        result = [0] * self.query_count
        if self.n == 0 or width == 0:
            return result
        permutation = list(range(width))
        second = self.second
        for first_index, first_value in enumerate(self.first):
            previous = -1
            for second_index in range(width):
                value = permutation[second_index]
                if first_value == second[second_index] or value < previous:
                    permutation[second_index] = previous
                    previous = value

            row = self.queries[first_index]
            if row is None:
                continue
            bit = [0] * (width + 1)
            total = 0
            for right in range(width):
                value = permutation[right]
                if value != -1:
                    total += 1
                    index = value + 1
                    while index <= width:
                        bit[index] += 1
                        index += index & -index
                bucket = row.get(right)
                if bucket is None:
                    continue
                for left, query_id in bucket:
                    count_less = 0
                    index = left
                    while index:
                        count_less += bit[index]
                        index -= index & -index
                    result[query_id] = (
                        right - left + 1 - (total - count_less)
                    )
        return result


def prefix_substring_lcs(first, second, queries):
    solver = PrefixSubstringLCS(first, second)
    for prefix_end, left, right in queries:
        solver.add(prefix_end, left, right)
    return solver.run()
