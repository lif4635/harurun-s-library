import sys

from library_codex.graph_enumeration.ChromaticPolynomial import chromatic_polynomial


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    graph = [[] for _ in range(n)]
    for _ in range(m):
        a, b = map(int, read().split())
        graph[a].append(b)
    print(*chromatic_polynomial(graph))


if __name__ == "__main__":
    main()
