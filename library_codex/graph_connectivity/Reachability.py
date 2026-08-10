"""有向グラフ上の複数の到達可能性queryをまとめて判定する。"""

from library_codex.graph_connectivity.StronglyConnectedComponents import SCC


def reachability(graph, queries):
    """各(source, target)についてsourceからtargetへ到達できるか返す。"""
    n = len(graph)
    pairs = list(queries)
    for source, target in pairs:
        if not 0 <= source < n or not 0 <= target < n:
            raise IndexError("a query vertex is outside the graph")
    if not pairs:
        return []

    decomposition = SCC(graph)
    component = decomposition.component
    dag = decomposition.dag
    count = decomposition.count

    indegree = [0] * count
    for edges in dag:
        for to in edges:
            indegree[to] += 1
    order = [v for v in range(count) if indegree[v] == 0]
    head = 0
    while head < len(order):
        vertex = order[head]
        head += 1
        for to in dag[vertex]:
            indegree[to] -= 1
            if indegree[to] == 0:
                order.append(to)

    result = [False] * len(pairs)
    by_source = {}
    for index, (source, target) in enumerate(pairs):
        first = component[source]
        second = component[target]
        if first == second:
            result[index] = True
        else:
            by_source.setdefault(first, []).append((index, second))

    sources = list(by_source)
    batch_size = 2048
    for begin in range(0, len(sources), batch_size):
        batch = sources[begin:begin + batch_size]
        reached = [0] * count
        for bit, source in enumerate(batch):
            reached[source] = 1 << bit
        for vertex in order:
            bits = reached[vertex]
            if bits:
                for to in dag[vertex]:
                    reached[to] |= bits
        for bit, source in enumerate(batch):
            flag = 1 << bit
            for index, target in by_source[source]:
                result[index] = bool(reached[target] & flag)
    return result
