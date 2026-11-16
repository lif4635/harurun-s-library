"""2列間のLevenshtein距離を計算し、最短編集列を復元する。"""


def edit_distance(first, second):
    """挿入・削除・置換の最小回数をビット並列DPで求める。"""
    if len(first) < len(second):
        first, second = second, first
    size = len(second)
    if not size:
        return len(first)
    masks = {}
    try:
        for index, value in enumerate(second):
            masks[value] = masks.get(value, 0) | (1 << index)
        for value in first:
            hash(value)
    except TypeError:
        return _edit_distance_dp(first, second)
    full = (1 << size) - 1
    high = 1 << (size - 1)
    positive = full
    negative = 0
    distance = size
    for value in first:
        equal = masks.get(value, 0)
        vertical = equal | negative
        horizontal = (((equal & positive) + positive) ^ positive) | equal
        plus = negative | ~(horizontal | positive)
        minus = positive & horizontal
        distance += bool(plus & high) - bool(minus & high)
        plus = (plus << 1) | 1
        positive = ((minus << 1) | ~(vertical | plus)) & full
        negative = plus & vertical
    return distance


def _edit_distance_dp(first, second):
    previous = list(range(len(second) + 1))
    for i, left in enumerate(first, 1):
        current = [i] + [0] * len(second)
        for j, right in enumerate(second, 1):
            current[j] = min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + (left != right),
            )
        previous = current
    return previous[-1]


def edit_distance_bounded(first, second, limit):
    """距離がlimit以下なら正確な距離、それより大きければlimit+1を返す。"""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    if len(first) < len(second):
        first, second = second, first
    n, m = len(first), len(second)
    cutoff = limit + 1
    if n - m > limit:
        return cutoff
    previous = list(range(min(m, limit) + 1))
    start = 0
    for i in range(1, n + 1):
        lo, hi = max(0, i - limit), min(m, i + limit)
        current = [cutoff] * (hi - lo + 1)
        if lo == 0:
            current[0] = i
        for j in range(max(1, lo), hi + 1):
            p = j - start
            above = previous[p] + 1 if 0 <= p < len(previous) else cutoff
            diagonal = previous[p - 1] + (first[i - 1] != second[j - 1]) if 0 <= p - 1 < len(previous) else cutoff
            left = current[j - lo - 1] + 1 if j > lo else cutoff
            current[j - lo] = min(above, diagonal, left)
        if min(current) > limit:
            return cutoff
        previous, start = current, lo
    return min(previous[-1], cutoff)


def edit_distance_with_path(first, second):
    """Levenshtein距離と、その値を達成する編集手順を返す。"""
    n = len(first)
    m = len(second)
    table = [list(range(m + 1))]
    for i in range(1, n + 1):
        row = [i] + [0] * m
        previous = table[-1]
        for j in range(1, m + 1):
            row[j] = min(
                previous[j] + 1,
                row[j - 1] + 1,
                previous[j - 1] + (first[i - 1] != second[j - 1]),
            )
        table.append(row)

    steps = []
    i, j = n, m
    while i or j:
        if i and j:
            cost = first[i - 1] != second[j - 1]
            if table[i][j] == table[i - 1][j - 1] + cost:
                steps.append(("replace" if cost else "match", i - 1, j - 1))
                i -= 1
                j -= 1
                continue
        if i and table[i][j] == table[i - 1][j] + 1:
            steps.append(("delete", i - 1, j))
            i -= 1
        else:
            steps.append(("insert", i, j - 1))
            j -= 1
    steps.reverse()
    return table[n][m], steps
