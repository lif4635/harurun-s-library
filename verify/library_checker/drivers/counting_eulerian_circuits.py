import sys

from library_codex.graph_enumeration.EulerianCircuits import count_eulerian_circuits


def main():
    data = iter(map(int, sys.stdin.buffer.read().split()))
    n, m = next(data), next(data)
    edges = [(next(data), next(data)) for _ in range(m)]
    print(count_eulerian_circuits(n, edges))


if __name__ == "__main__":
    main()
