"""2列間のLevenshtein距離を計算し、最短編集列を復元する。"""


def edit_distance(first, second):
    """挿入・削除・置換の最小回数を省memoryで求める。"""
    if len(first) < len(second):
        first, second = second, first
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
