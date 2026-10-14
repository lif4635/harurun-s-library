import sys

from library_codex.tree.Rerooting import rerooting_dp


def main():
    read = sys.stdin.buffer.readline
    n = int(read())
    values = list(map(int, read().split()))
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        u, v, b, c = map(int, read().split())
        graph[u].append((v, (b, c)))
        graph[v].append((u, (b, c)))

    def merge(left, right):
        return (left[0] + right[0]) % 998244353, left[1] + right[1]

    def put_edge(value, source, target, edge):
        total, size = value
        b, c = edge
        return (b * total + c * size) % 998244353, size

    def put_vertex(value, vertex):
        return (value[0] + values[vertex]) % 998244353, value[1] + 1

    answer = rerooting_dp(graph, merge, (0, 0), put_edge, put_vertex)
    print(" ".join(str(value[0]) for value in answer))


if __name__ == "__main__":
    main()
