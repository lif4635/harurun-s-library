import sys

from library_codex.tree.CentroidDistanceAdd import CentroidDistanceAdd


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    values = list(map(int, read().split()))
    graph = [[] for _ in range(n)]
    for _ in range(n - 1):
        u, v = map(int, read().split())
        graph[u].append(v)
        graph[v].append(u)
    tree = CentroidDistanceAdd(graph, values)
    result = []
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            tree.add(query[1], query[2], query[3], query[4])
        else:
            result.append(str(tree.get(query[1])))
    sys.stdout.write("\n".join(result))


if __name__ == "__main__":
    main()
