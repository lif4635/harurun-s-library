"""辺listからbit mask形式の無向隣接表を作る。"""

def graph_from_edges(n, edges):
    """Build an undirected adjacency list from pairs."""
    graph = [[] for _ in range(n)]
    for u, v in edges:
        if u != v:
            graph[u].append(v)
            graph[v].append(u)
    return graph

