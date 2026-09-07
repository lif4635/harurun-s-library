"""Monge重みを持つDAGの最短路を辺数制約付きで計算する。"""

from library_codex.optimization.MonotoneMinima import monotone_minima

def monge_shortest_paths(target, cost, infinity=10 ** 100):
    """Distances from 0 to every vertex 0..target in a complete Monge DAG."""
    if target < 0:
        raise ValueError("target must be nonnegative")
    distance = [float("inf")] * (target + 1)
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

def _monge_fixed_layers(target, edge_count, cost, infinity):
    infinity = float("inf")
    distance = [infinity] * (target + 1)
    distance[0] = 0
    for _ in range(edge_count):
        distance = _monge_layer(distance, target, cost, infinity)
    return distance[target]

def _monge_penalty(target, cost, penalty):
    scale = target + 1
    extra = penalty * scale + 1
    def encoded(first, second):
        value = cost(first, second)
        if not isinstance(value, int):
            raise TypeError("integer=True requires integer costs; use integer=False")
        return value * scale + extra

    value = monge_shortest_paths(target, encoded, float("inf"))[target]
    return divmod(value, scale)

def monge_d_edge_shortest_path(target, edge_count, cost, infinity=10 ** 100, *, integer=True):
    if target < 0:
        raise ValueError("target must be nonnegative")
    if not 0 <= edge_count <= target:
        return infinity
    if edge_count == 0:
        return 0 if target == 0 else infinity
    if edge_count == 1:
        return cost(0, target)
    if edge_count == target:
        return sum(cost(vertex, vertex + 1) for vertex in range(target))
    if edge_count == 2:
        return min(cost(0, vertex) + cost(vertex, target)
                   for vertex in range(1, target))
    if not integer:
        return _monge_fixed_layers(target, edge_count, cost, infinity)
    attempts = 0

    def solve(penalty):
        nonlocal attempts
        if attempts >= edge_count:
            return None
        attempts += 1
        return _monge_penalty(target, cost, penalty)

    penalty = 0
    result = solve(penalty)
    if result is None:
        return _monge_fixed_layers(target, edge_count, cost, infinity)
    value, count = result
    if count == edge_count:
        return value
    if count > edge_count:
        lower, upper = 0, 1
        direction = 1
    else:
        lower, upper = -1, 0
        direction = -1
    while True:
        penalty = upper if direction == 1 else lower
        result = solve(penalty)
        if result is None:
            return _monge_fixed_layers(target, edge_count, cost, infinity)
        value, count = result
        if count == edge_count:
            return value - penalty * edge_count
        if (count < edge_count) == (direction == 1):
            break
        if direction == 1:
            lower, upper = upper, upper * 2
        else:
            lower, upper = lower * 2, lower
    while upper - lower > 1:
        penalty = (lower + upper) // 2
        result = solve(penalty)
        if result is None:
            return _monge_fixed_layers(target, edge_count, cost, infinity)
        value, count = result
        if count == edge_count:
            return value - penalty * edge_count
        if count > edge_count:
            lower = penalty
        else:
            upper = penalty
    result = solve(upper)
    if result is None:
        return _monge_fixed_layers(target, edge_count, cost, infinity)
    return result[0] - upper * edge_count

def enumerate_monge_d_edge_shortest_paths(target, cost, infinity=10 ** 100):
    if target < 0:
        raise ValueError("target must be nonnegative")
    answer = [infinity] * (target + 1)
    if target == 0:
        answer[0] = 0
        return answer
    distance = [float("inf")] * (target + 1)
    distance[0] = 0
    for edges in range(1, target + 1):
        distance = _monge_layer(distance, target, cost, float("inf"))
        answer[edges] = distance[target]
    return answer
