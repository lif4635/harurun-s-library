"""二部割当問題の最小費用または最大利益を求める。"""

def hungarian(cost):
    """Minimum-cost injection from rows to columns.

    Returns ``(minimum_cost, assignment)`` where ``assignment[i]`` is the
    column matched to row ``i``.  Requires ``rows <= columns`` and supports
    negative integer or floating-point costs.  Complexity is O(R^2 C).
    """
    rows = len(cost)
    if rows == 0:
        return 0, []
    columns = len(cost[0])
    if columns < rows:
        raise ValueError("hungarian requires rows <= columns")
    if any(len(row) != columns for row in cost):
        raise ValueError("cost matrix must be rectangular")
    u = [0] * (rows + 1)
    v = [0] * (columns + 1)
    matching = [0] * (columns + 1)
    way = [0] * (columns + 1)
    for i in range(1, rows + 1):
        matching[0] = i
        min_value = [float("inf")] * (columns + 1)
        used = [False] * (columns + 1)
        column = 0
        while True:
            used[column] = True
            row = matching[column]
            delta = float("inf")
            next_column = 0
            row_cost = cost[row - 1]
            for j in range(1, columns + 1):
                if not used[j]:
                    current = row_cost[j - 1] - u[row] - v[j]
                    if current < min_value[j]:
                        min_value[j] = current
                        way[j] = column
                    if min_value[j] < delta:
                        delta = min_value[j]
                        next_column = j
            for j in range(columns + 1):
                if used[j]:
                    u[matching[j]] += delta
                    v[j] -= delta
                else:
                    min_value[j] -= delta
            column = next_column
            if matching[column] == 0:
                break
        while column:
            previous = way[column]
            matching[column] = matching[previous]
            column = previous
    assignment = [-1] * rows
    for column in range(1, columns + 1):
        row = matching[column]
        if row:
            assignment[row - 1] = column - 1
    return -v[0], assignment

def hungarian_max(cost):
    """Maximum-cost injection from rows to columns."""
    value, assignment = hungarian([[-x for x in row] for row in cost])
    return -value, assignment

