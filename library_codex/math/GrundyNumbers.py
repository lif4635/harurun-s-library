"""遷移グラフからmexとGrundy数を計算する。"""

def grundy_numbers(graph):
    """Return DAG Grundy numbers, or None when the graph has a cycle."""
    n = len(graph)
    indegree = [0] * n
    for row in graph:
        for to in row:
            indegree[to] += 1
    order = [v for v in range(n) if indegree[v] == 0]
    for v in order:
        for to in graph[v]:
            indegree[to] -= 1
            if indegree[to] == 0:
                order.append(to)
    if len(order) != n:
        return None
    grundy = [0] * n
    marker = [0] * (n + 1)
    stamp = 0
    for v in reversed(order):
        stamp += 1
        for to in graph[v]:
            marker[grundy[to]] = stamp
        value = 0
        while marker[value] == stamp:
            value += 1
        grundy[v] = value
    return grundy

def mex(values):
    values = set(value for value in values if value >= 0)
    result = 0
    while result in values:
        result += 1
    return result

