import sys
from library_codex.graph_matching.GeneralWeightedMatching import GeneralWeightedMatching


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    solver = GeneralWeightedMatching(n)
    for u, v, w in edges:
        solver.add_edge(u, v, w)
    mate = solver.run()
    pairs = [(u, v) for u, v in enumerate(mate) if u < v]
    weight = sum(w for u, v, w in edges if mate[u] == v)
    answer = [f"{len(pairs)} {weight}"]
    answer.extend(f"{u} {v}" for u, v in pairs)
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
