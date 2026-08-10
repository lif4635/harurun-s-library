"""同じ更新列に対する複数の単調判定の境界を並列二分探索する。"""


def parallel_binary_search(query_count, ok, ng, reset, update, check):
    """各queryについて、既知のtrue側とfalse側の境界からtrue側を返す。"""
    if query_count < 0:
        raise ValueError("query_count must be nonnegative")
    if ok < 0 or ng < 0:
        raise ValueError("update counts must be nonnegative")
    true_side = [ok] * query_count
    false_side = [ng] * query_count
    update_count = max(ok, ng)

    while True:
        middle = [-1] * query_count
        counts = [0] * (update_count + 1)
        active = 0
        for query in range(query_count):
            if abs(true_side[query] - false_side[query]) <= 1:
                continue
            target = (true_side[query] + false_side[query]) >> 1
            middle[query] = target
            counts[target + 1] += 1
            active += 1
        if active == 0:
            return true_side

        for index in range(update_count):
            counts[index + 1] += counts[index]
        cursor = counts[:]
        order = [0] * active
        for query, target in enumerate(middle):
            if target >= 0:
                order[cursor[target]] = query
                cursor[target] += 1

        reset()
        applied = 0
        for query in order:
            target = middle[query]
            while applied < target:
                update(applied)
                applied += 1
            if check(query):
                true_side[query] = target
            else:
                false_side[query] = target
