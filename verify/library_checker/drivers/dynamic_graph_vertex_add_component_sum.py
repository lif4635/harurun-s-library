import sys

from library_codex.graph_connectivity.OfflineDynamicSum import OfflineDynamicSum


def main():
    read = sys.stdin.buffer.readline
    n, q = map(int, read().split())
    graph = OfflineDynamicSum(list(map(int, read().split())))
    for _ in range(q):
        query = list(map(int, read().split()))
        if query[0] == 0:
            graph.add_edge(query[1], query[2])
        elif query[0] == 1:
            graph.remove_edge(query[1], query[2])
        elif query[0] == 2:
            graph.add(query[1], query[2])
        else:
            graph.query(query[1])
    sys.stdout.write("\n".join(map(str, graph.solve())) + "\n")


if __name__ == "__main__":
    main()
