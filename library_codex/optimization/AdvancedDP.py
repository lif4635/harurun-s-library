from math import isqrt

from library_codex.optimization.Optimization import monotone_minima


def convex_min_plus_convolution(convex, arbitrary, return_argmin=False):
    """Min-plus convolution where ``convex`` has nondecreasing differences."""
    if not convex or not arbitrary:
        return ([], []) if return_argmin else []
    first_size = len(convex)
    second_size = len(arbitrary)

    def compare(output, first, second):
        first_convex = output - first
        second_convex = output - second
        if not 0 <= first_convex < first_size:
            return False
        if not 0 <= second_convex < first_size:
            return True
        return convex[first_convex] + arbitrary[first] <= (
            convex[second_convex] + arbitrary[second]
        )

    indices = monotone_minima(
        first_size + second_size - 1, second_size, compare=compare
    )
    values = [convex[output - index] + arbitrary[index]
              for output, index in enumerate(indices)]
    if not return_argmin:
        return values
    convex_indices = [output - index for output, index in enumerate(indices)]
    return values, convex_indices


def concave_max_plus_convolution(concave, arbitrary, return_argmax=False):
    negated_convex = [-value for value in concave]
    negated_arbitrary = [-value for value in arbitrary]
    result = convex_min_plus_convolution(
        negated_convex, negated_arbitrary, return_argmax
    )
    if return_argmax:
        values, indices = result
        return [-value for value in values], indices
    return [-value for value in result]


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


def knapsack_branch_and_bound(values, weights, capacity):
    """Exact 0/1 knapsack using an iterative fractional-bound search."""
    if len(values) != len(weights) or capacity < 0:
        raise ValueError("invalid knapsack input")
    free_value = 0
    items = []
    for value, weight in zip(values, weights):
        if weight < 0:
            raise ValueError("weights must be nonnegative")
        if value <= 0:
            continue
        if weight == 0:
            free_value += value
        elif weight <= capacity:
            items.append((value, weight))
    items.sort(key=lambda item: item[0] / item[1], reverse=True)
    size = len(items)

    def bound(index, value, remaining):
        result = value
        while index < size and remaining:
            item_value, item_weight = items[index]
            if item_weight <= remaining:
                result += item_value
                remaining -= item_weight
                index += 1
            else:
                return result + item_value * remaining / item_weight
        return result

    best = free_value
    stack = [(0, free_value, capacity)]
    while stack:
        index, value, remaining = stack.pop()
        if index == size:
            if value > best:
                best = value
            continue
        if bound(index, value, remaining) <= best:
            continue
        item_value, item_weight = items[index]
        stack.append((index + 1, value, remaining))
        if item_weight <= remaining:
            candidate = value + item_value
            if candidate > best:
                best = candidate
            stack.append((index + 1, candidate, remaining - item_weight))
    return best


class RollbackMo:
    """Mo ordering for data structures supporting snapshot and rollback."""

    __slots__ = ("n", "queries")

    def __init__(self, size):
        self.n = size
        self.queries = []

    def add(self, left, right):
        if not 0 <= left <= right <= self.n:
            raise IndexError("invalid half-open query")
        self.queries.append((left, right))
        return len(self.queries) - 1

    add_query = add

    def run(self, initialize, insert, snapshot, rollback, output):
        query_count = len(self.queries)
        width = max(1, int(self.n / max(1, query_count + 1) ** 0.5))
        order = sorted(range(query_count), key=lambda index: (
            self.queries[index][0] // width, self.queries[index][1]
        ))
        answers = [None] * query_count
        initialize()
        snapshot()
        for query in order:
            left, right = self.queries[query]
            if right - left < width:
                for index in range(left, right):
                    insert(index)
                answers[query] = output(query)
                rollback()
        last_block = -1
        right_endpoint = 0
        for query in order:
            left, right = self.queries[query]
            if right - left < width:
                continue
            block = left // width
            if block != last_block:
                initialize()
                last_block = block
                right_endpoint = min(self.n, (block + 1) * width)
            while right_endpoint < right:
                insert(right_endpoint)
                right_endpoint += 1
            snapshot()
            for index in range(min(self.n, (block + 1) * width) - 1,
                               left - 1, -1):
                insert(index)
            answers[query] = output(query)
            rollback()
        return answers


concave_min_plus_convolution = convex_min_plus_convolution
MongeShortestPath = monge_shortest_paths
dEdgeMongeShortestPath = monge_d_edge_shortest_path
BranchAndBound = knapsack_branch_and_bound
