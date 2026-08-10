"""静的な列の複数の半開区間についてmexをまとめて求める。"""


def range_mex(values, queries):
    """各query ``[left, right)`` に含まれない最小の非負整数を返す。"""
    values = list(values)
    queries = list(queries)
    length = len(values)
    grouped = [[] for _ in range(length + 1)]
    for index, query in enumerate(queries):
        if len(query) != 2:
            raise ValueError("each query must contain left and right")
        left, right = query
        if not 0 <= left <= right <= length:
            raise ValueError("query must satisfy 0 <= left <= right <= len(values)")
        grouped[right].append((left, index))

    size = 1
    while size <= length:
        size <<= 1
    minimum_last = [-1] * (size << 1)
    answer = [0] * len(queries)

    for right in range(length + 1):
        if right:
            value = values[right - 1]
            if 0 <= value <= length:
                node = size + value
                minimum_last[node] = right - 1
                node >>= 1
                while node:
                    left_value = minimum_last[node << 1]
                    right_value = minimum_last[node << 1 | 1]
                    minimum_last[node] = (
                        left_value if left_value < right_value else right_value
                    )
                    node >>= 1

        for left, query_index in grouped[right]:
            node = 1
            while node < size:
                child = node << 1
                if minimum_last[child] < left:
                    node = child
                else:
                    node = child | 1
            answer[query_index] = node - size
    return answer
