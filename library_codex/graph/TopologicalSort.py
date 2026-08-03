"""DAGの頂点を辺の向きに沿う順序へ並べる。"""

from collections import deque

import heapq

def topological_sort(graph, lexicographical=False):
    n = len(graph)
    indegree = [0] * n
    for row in graph:
        for entry in row:
            other = entry if isinstance(entry, int) else entry[0]
            indegree[other] += 1
    if lexicographical:
        queue = [node for node in range(n) if indegree[node] == 0]
        heapq.heapify(queue)
        result = []
        while queue:
            node = heapq.heappop(queue)
            result.append(node)
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                indegree[other] -= 1
                if indegree[other] == 0:
                    heapq.heappush(queue, other)
    else:
        queue = deque(node for node in range(n) if indegree[node] == 0)
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for entry in graph[node]:
                other = entry if isinstance(entry, int) else entry[0]
                indegree[other] -= 1
                if indegree[other] == 0:
                    queue.append(other)
    return result if len(result) == n else None

