"""有向グラフの全辺を反転した隣接listを作る。"""

def reverse_graph(graph):
    reverse = [[] for _ in graph]
    for source, row in enumerate(graph):
        for entry in row:
            if isinstance(entry, int):
                reverse[entry].append(source)
            else:
                target = entry[0]
                reverse[target].append((source,) + tuple(entry[1:]))
    return reverse

