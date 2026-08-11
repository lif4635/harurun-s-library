"""無向グラフから奇cycleを1つ復元する。"""

from collections import deque


def find_odd_cycle(graph):
    """奇cycleの頂点を周上の順に返し、二部グラフなら空listを返す。"""
    n = len(graph)
    color = [-1] * n
    parent = [-1] * n
    depth = [0] * n
    for start in range(n):
        if color[start] >= 0:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for entry in graph[vertex]:
                other = entry if isinstance(entry, int) else entry[0]
                if not 0 <= other < n:
                    raise IndexError("an edge endpoint is outside the graph")
                if color[other] < 0:
                    color[other] = color[vertex] ^ 1
                    parent[other] = vertex
                    depth[other] = depth[vertex] + 1
                    queue.append(other)
                elif color[other] == color[vertex]:
                    first = vertex
                    second = other
                    first_path = []
                    second_path = []
                    while depth[first] > depth[second]:
                        first_path.append(first)
                        first = parent[first]
                    while depth[second] > depth[first]:
                        second_path.append(second)
                        second = parent[second]
                    while first != second:
                        first_path.append(first)
                        second_path.append(second)
                        first = parent[first]
                        second = parent[second]
                    first_path.append(first)
                    return first_path + list(reversed(second_path))
    return []
