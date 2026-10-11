from library_codex.graph_flow.MinCostBFlow import MinCostBFlow


def main():
    import sys

    read = sys.stdin.buffer.readline
    n, m = map(int, read().split())
    graph = MinCostBFlow(n)
    for v in range(n):
        graph.add_supply(v, int(read()))
    for _ in range(m):
        graph.add_edge(*map(int, read().split()))
    feasible, cost = graph.run()
    if not feasible:
        print('infeasible')
        return
    print('\n'.join(map(str, [cost] + graph.dual + [graph.get_flow(i) for i in range(m)])))


if __name__ == '__main__':
    main()
