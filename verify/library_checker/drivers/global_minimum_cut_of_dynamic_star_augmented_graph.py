import sys

from library_codex.graph_flow.DynamicStarMinCut import DynamicStarMinCut


def main():
    read = sys.stdin.buffer.readline
    n, m, q = map(int, read().split())
    weights = list(map(int, read().split()))
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    graph = DynamicStarMinCut(n, edges, weights)
    output = []
    for _ in range(q):
        vertex, weight = map(int, read().split())
        output.append(str(graph.set(vertex, weight)))
    sys.stdout.write("\n".join(output))


if __name__ == "__main__":
    main()
