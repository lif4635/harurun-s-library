"""Small reproducible PyPy benchmark for the advanced-flow backends."""

import argparse
import random
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.graph.AdvancedFlow import PushRelabelMaxFlow
from library_codex.graph.MaxFlow import MaxFlowGraph


def build_edges(n, density, seed):
    rng = random.Random(seed)
    edges = []
    for source in range(n):
        for target in range(n):
            if source != target and rng.random() < density:
                edges.append((source, target, rng.randrange(1, 1_000_001)))
    return edges


def run(flow_class, n, edges, repeat):
    best = float("inf")
    value = None
    for _ in range(repeat):
        graph = flow_class(n)
        for edge in edges:
            graph.add_edge(*edge)
        started = perf_counter()
        current = graph.flow(0, n - 1)
        elapsed = perf_counter() - started
        if value is None:
            value = current
        elif current != value:
            raise AssertionError("backends disagree across repetitions")
        best = min(best, elapsed)
    return value, best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertices", type=int, default=300)
    parser.add_argument("--density", type=float, default=0.12)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--seed", type=int, default=801)
    args = parser.parse_args()
    edges = build_edges(args.vertices, args.density, args.seed)
    print(f"vertices={args.vertices} edges={len(edges)} density={args.density}")
    baseline_value, baseline_time = run(MaxFlowGraph, args.vertices, edges, args.repeat)
    fast_value, fast_time = run(PushRelabelMaxFlow, args.vertices, edges, args.repeat)
    if baseline_value != fast_value:
        raise AssertionError("Dinic and push-relabel disagree")
    print(f"Dinic:       {baseline_time:.6f}s")
    print(f"PushRelabel: {fast_time:.6f}s")
    print(f"ratio:       {baseline_time / fast_time:.3f}x")


if __name__ == "__main__":
    main()
