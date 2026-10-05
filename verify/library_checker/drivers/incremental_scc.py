import sys
from library_codex.graph_connectivity.AdvancedConnectivity import incremental_scc_offline
from library_codex.union_find.UnionFind import UnionFind


def main():
    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    values = list(map(int, read().split()))
    edges = [tuple(map(int, read().split())) for _ in range(m)]
    events = incremental_scc_offline(n, edges)
    uf = UnionFind(n)
    total = 0
    mod = 998244353
    answer = []
    for event in events:
        for index in event:
            u, v = edges[index]
            u, v = uf.find(u), uf.find(v)
            if u != v:
                total = (total + values[u] * values[v]) % mod
                combined = (values[u] + values[v]) % mod
                values[uf.merge(u, v)] = combined
        answer.append(str(total))
    sys.stdout.write("\n".join(answer))


if __name__ == "__main__":
    main()
