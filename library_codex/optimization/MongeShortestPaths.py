"""Monge重みを持つDAGの最短路を辺数制約付きで計算する。"""

from library_codex.optimization.MonotoneMinima import monotone_minima

def monge_shortest_paths(target, cost, infinity=10 ** 100):
    """Distances from 0 to every vertex 0..target in a complete Monge DAG."""
    if target < 0:
        raise ValueError("target must be nonnegative")
    distance = [infinity] * (target + 1)
    predecessor = [0] * (target + 1)
    distance[0] = 0

    def check(first, second):
        if first >= second:
            return
        candidate = distance[first] + cost(first, second)
        if candidate < distance[second]:
            distance[second] = candidate
            predecessor[second] = first

    if target:
        check(0, target)
    stack = [(0, target, 0)]
    while stack:
        left, right, phase = stack.pop()
        if left + 1 >= right:
            continue
        middle = (left + right) >> 1
        if phase == 0:
            for source in range(predecessor[left], predecessor[right] + 1):
                check(source, middle)
            stack.append((left, right, 1))
            stack.append((left, middle, 0))
        else:
            for source in range(left + 1, middle + 1):
                check(source, right)
            stack.append((middle, right, 0))
    return distance

def _monge_layer(previous, target, cost, infinity):
    def value(destination, source):
        if source >= destination or previous[source] == infinity:
            return infinity
        return previous[source] + cost(source, destination)

    indices = monotone_minima(target + 1, target + 1, value=value)
    result = [infinity] * (target + 1)
    for destination in range(1, target + 1):
        source = indices[destination]
        if source < destination and previous[source] != infinity:
            result[destination] = previous[source] + cost(source, destination)
    return result

def monge_d_edge_shortest_path(target, edge_count, cost, infinity=10 ** 100):
    if not 0 <= edge_count <= target:
        return infinity
    distance = [infinity] * (target + 1)
    distance[0] = 0
    for _ in range(edge_count):
        distance = _monge_layer(distance, target, cost, infinity)
    return distance[target]

def enumerate_monge_d_edge_shortest_paths(target, cost, infinity=10 ** 100):
    answer = [infinity] * (target + 1)
    if target == 0:
        answer[0] = 0
        return answer
    distance = [infinity] * (target + 1)
    distance[0] = 0
    for edges in range(1, target + 1):
        distance = _monge_layer(distance, target, cost, infinity)
        answer[edges] = distance[target]
    return answer

