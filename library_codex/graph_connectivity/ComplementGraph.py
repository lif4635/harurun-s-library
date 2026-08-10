"""隣接listを明示的に反転せず、補グラフを幅優先探索する。"""


def _to_vertex(edge):
    return edge if isinstance(edge, int) else edge[0]


def complement_bfs(graph, source):
    """元のgraphに辺がない頂点対を辺とみなし、sourceからBFSする。"""
    n = len(graph)
    if not 0 <= source < n:
        raise IndexError("source is outside the graph")

    distance = [-1] * n
    parent = [-1] * n
    distance[source] = 0
    queue = [source]
    unvisited = [v for v in range(n) if v != source]
    marked = [0] * n
    stamp = 0
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head += 1
        stamp += 1
        for edge in graph[vertex]:
            to = _to_vertex(edge)
            if not 0 <= to < n:
                raise IndexError("an edge endpoint is outside the graph")
            marked[to] = stamp

        index = len(unvisited) - 1
        while index >= 0:
            to = unvisited[index]
            if marked[to] != stamp:
                distance[to] = distance[vertex] + 1
                parent[to] = vertex
                queue.append(to)
                unvisited[index] = unvisited[-1]
                unvisited.pop()
            index -= 1
    return distance, parent


def complement_components(graph):
    """無向graphの補グラフにおける連結成分を列挙する。"""
    n = len(graph)
    unvisited = list(range(n))
    marked = [0] * n
    stamp = 0
    components = []
    while unvisited:
        root = unvisited.pop()
        component = [root]
        head = 0
        while head < len(component):
            vertex = component[head]
            head += 1
            stamp += 1
            for edge in graph[vertex]:
                to = _to_vertex(edge)
                if not 0 <= to < n:
                    raise IndexError("an edge endpoint is outside the graph")
                marked[to] = stamp

            index = len(unvisited) - 1
            while index >= 0:
                to = unvisited[index]
                if marked[to] != stamp:
                    component.append(to)
                    unvisited[index] = unvisited[-1]
                    unvisited.pop()
                index -= 1
        components.append(component)
    return components
