"""必要な辺だけを生成し、整数IDを振っていない状態間の最短路を求める。"""

from heapq import heappop, heappush


def _search(starts, adjacent, finish):
    distance = dict.fromkeys(starts, 0)
    previous = {}
    heap = [(0, index, state) for index, state in enumerate(distance)]
    serial = len(heap)
    while heap:
        cost, _, state = heappop(heap)
        if cost != distance[state]:
            continue
        if finish is not None and finish(state):
            return distance, previous, state, True
        for other, weight in adjacent(state):
            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative weights")
            candidate = cost + weight
            if other not in distance or candidate < distance[other]:
                distance[other] = candidate
                previous[other] = state
                heappush(heap, (candidate, serial, other))
                serial += 1
    return distance, previous, None, False


def implicit_dijkstra(starts, adjacent):
    """複数始点から到達できる全状態の最短距離と直前の状態を返す。"""
    distance, previous, _, _ = _search(starts, adjacent, None)
    return distance, previous


def implicit_shortest_path(starts, adjacent, finish):
    """finish(state)を満たす状態までの最短距離と経路を返す。"""
    distance, previous, state, found = _search(starts, adjacent, finish)
    if not found:
        return float("inf"), []
    cost = distance[state]
    path = [state]
    while state in previous:
        state = previous[state]
        path.append(state)
    path.reverse()
    return cost, path
