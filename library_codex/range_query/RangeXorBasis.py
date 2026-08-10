"""静的整数列の複数の半開区間について、XOR線形基底を一括計算する。"""


def _prepare(values, queries):
    values = list(values)
    if any(value < 0 for value in values):
        raise ValueError("values must be nonnegative")
    n = len(values)
    grouped = [[] for _ in range(n + 1)]
    for query_id, query in enumerate(queries):
        left, right = query
        if not 0 <= left <= right <= n:
            raise IndexError("query must be a half-open interval in values")
        grouped[right].append((query_id, left))
    return values, grouped


def _solve(values, queries, calculate):
    queries = list(queries)
    values, grouped = _prepare(values, queries)
    bit_count = max((value.bit_length() for value in values), default=0)
    basis = [0] * bit_count
    position = [-1] * bit_count
    answer = [None] * len(queries)

    for right in range(len(values) + 1):
        for query_id, left in grouped[right]:
            current = [
                basis[bit]
                for bit in range(bit_count - 1, -1, -1)
                if position[bit] >= left
            ]
            answer[query_id] = calculate(current, query_id)
        if right == len(values):
            break

        value = values[right]
        inserted_at = right
        for bit in range(bit_count - 1, -1, -1):
            if value >> bit & 1 == 0:
                continue
            if basis[bit] == 0:
                basis[bit] = value
                position[bit] = inserted_at
                break
            if inserted_at > position[bit]:
                value, basis[bit] = basis[bit], value
                inserted_at, position[bit] = position[bit], inserted_at
            value ^= basis[bit]
    return answer


def range_xor_basis(values, queries):
    """各半開区間に含まれる値が張るXOR線形基底を返す。"""
    return _solve(values, queries, lambda basis, _query_id: basis)


def range_max_xor(values, queries, initial=0):
    """各半開区間から任意個の値を選び、initialとのXORを最大化する。"""
    if initial < 0:
        raise ValueError("initial must be nonnegative")

    def calculate(basis, _query_id):
        result = initial
        for value in basis:
            candidate = result ^ value
            if candidate > result:
                result = candidate
        return result

    return _solve(values, queries, calculate)
