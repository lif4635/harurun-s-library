import sys
from library_codex.graph_enumeration.EnumerateTriangles import enumerate_triangles


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    values = list(map(int, read().split()))
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    answer = 0

    def collect(a, b, c, ab, ac, bc):
        nonlocal answer
        answer = (answer + values[a] * values[b] % 998244353 * values[c]) % 998244353

    enumerate_triangles(n, edges, collect)
    print(answer)


if __name__ == "__main__":
    main()
