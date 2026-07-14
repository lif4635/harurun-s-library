from itertools import product
import random

from library_codex.graph.MinCostBFlow import MinCostBFlow


def brute(vertex_count, edges, supply):
    best = None
    best_flow = None
    ranges = [range(lower, upper + 1) for _, _, lower, upper, _ in edges]
    for flows in product(*ranges):
        balance = [0] * vertex_count
        cost = 0
        for flow, edge in zip(flows, edges):
            source, target, _, _, edge_cost = edge
            balance[source] += flow
            balance[target] -= flow
            cost += flow * edge_cost
        if balance != supply:
            continue
        if best is None or cost < best:
            best = cost
            best_flow = flows
    return best, best_flow


def check_dual(solver):
    dual = solver.dual
    for source, target, lower, upper, cost, flow in solver.edges():
        if flow < upper:
            assert cost + dual[source] - dual[target] >= 0
        if flow > lower:
            assert -cost + dual[target] - dual[source] >= 0


def test_min_cost_b_flow_exhaustive_random_small():
    rng = random.Random(719834)
    for vertex_count in range(1, 6):
        for _ in range(1200):
            edge_count = rng.randrange(8)
            edges = []
            for _ in range(edge_count):
                source = rng.randrange(vertex_count)
                target = rng.randrange(vertex_count)
                lower = rng.randrange(-2, 3)
                upper = lower + rng.randrange(4)
                cost = rng.randrange(-5, 6)
                edges.append((source, target, lower, upper, cost))
            supply = [rng.randrange(-3, 4) for _ in range(vertex_count - 1)]
            supply.append(-sum(supply))
            expected, _ = brute(vertex_count, edges, supply)
            solver = MinCostBFlow(vertex_count)
            for vertex, value in enumerate(supply):
                solver.add_supply(vertex, value)
            for edge in edges:
                solver.add_edge(*edge)
            feasible, cost = solver.run()
            assert feasible == (expected is not None)
            if feasible:
                assert cost == expected
                actual_balance = [0] * vertex_count
                for source, target, lower, upper, _, flow in solver.edges():
                    assert lower <= flow <= upper
                    actual_balance[source] += flow
                    actual_balance[target] -= flow
                assert actual_balance == supply
                check_dual(solver)


def test_negative_cycles_self_loops_and_infeasible():
    solver = MinCostBFlow(3)
    first = solver.add_edge(0, 1, 0, 10, 5)
    second = solver.add_edge(1, 2, 0, 10, -8)
    third = solver.add_edge(2, 0, 0, 10, 1)
    loop = solver.add_edge(1, 1, -4, 7, -3)
    feasible, cost = solver.run()
    assert feasible
    assert [solver.get_flow(i) for i in (first, second, third)] == [10, 10, 10]
    assert solver.get_flow(loop) == 7
    assert cost == -41
    check_dual(solver)
    impossible = MinCostBFlow(2)
    impossible.add_supply(0, 1)
    impossible.add_supply(1, -1)
    assert impossible.run() == (False, 0)


def test_large_banded_transport():
    size = 10000
    solver = MinCostBFlow(size)
    solver.add_supply(0, 10**9)
    solver.add_supply(size - 1, -(10**9))
    edge_ids = []
    for vertex in range(size - 1):
        edge_ids.append(
            solver.add_edge(vertex, vertex + 1, 0, 10**9, vertex % 17 - 8)
        )
        solver.add_edge(vertex + 1, vertex, 0, 10**9, 20)
    feasible, cost = solver.run()
    assert feasible
    assert all(solver.get_flow(edge_id) == 10**9 for edge_id in edge_ids)
    assert cost == sum(vertex % 17 - 8 for vertex in range(size - 1)) * 10**9
