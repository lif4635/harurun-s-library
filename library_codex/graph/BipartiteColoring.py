"""無向グラフが二部グラフか判定し、2色の割当を返す。"""

from collections import deque

def bipartite_coloring(graph):
    n = len(graph)
    color = [-1] * n
    for start in range(n):
        if color[start] >= 0:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                if color[other] < 0:
                    color[other] = color[node] ^ 1
                    queue.append(other)
                elif color[other] == color[node]:
                    return None
    return color

