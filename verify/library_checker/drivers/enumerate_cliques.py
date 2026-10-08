import sys

from library_codex.graph_enumeration.EnumerateCliques import enumerate_cliques


def main():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, m = next(data), next(data)
    values = [next(data) for _ in range(n)]
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u, v = next(data), next(data)
        graph[u].append(v)
        graph[v].append(u)
    answer = 0

    def collect(vertices):
        nonlocal answer
        value = 1
        for vertex in vertices:
            value = value * values[vertex] % 998244353
        answer = (answer + value) % 998244353

    enumerate_cliques(graph, collect)
    print(answer)


main()
