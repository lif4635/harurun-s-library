"""Small reproducible PyPy benchmark for the advanced-flow backends."""

import argparse
import ast
import random
import statistics
import subprocess
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.graph_flow.PushRelabel import PushRelabel
from library_codex.graph_flow.MaxFlow import MaxFlowGraph


def build_edges(n, density, seed):
    rng = random.Random(seed)
    edges = []
    for source in range(n):
        for target in range(n):
            if source != target and rng.random() < density:
                edges.append((source, target, rng.randrange(1, 1_000_001)))
    return edges


def run(flow_class, n, edges, repeat):
    samples = []
    value = None
    for trial in range(repeat + 2):
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
        if trial >= 2:
            samples.append(elapsed)
    return value, statistics.median(samples)


def historical_fifo(revision):
    source = subprocess.check_output(
        ["git", "show", revision + ":library_codex/graph_flow/AdvancedFlow.py"],
        cwd=Path(__file__).resolve().parents[2], text=True,
    )
    tree = ast.parse(source)
    tree.body = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
                 or isinstance(node, ast.ClassDef) and node.name == "PushRelabelMaxFlow"]
    namespace = {}
    exec(compile(tree, "<historical FIFO>", "exec"), namespace)
    return namespace["PushRelabelMaxFlow"]


def suite(seed):
    rng = random.Random(seed)
    n = 1600
    edges = [(v, v + 1, rng.randrange(1, 10000)) for v in range(n - 1)]
    edges += [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 10000)) for _ in range(10000)]
    yield "sparse", n, edges
    yield "dense", 600, build_edges(600, 0.3, seed)
    width, layers = 50, 18
    n = width * layers + 2
    edges = [(0, 1 + v, 1000) for v in range(width)]
    edges += [(n - 2 - v, n - 1, 1000) for v in range(width)]
    for layer in range(layers - 1):
        for v in range(width):
            for _ in range(10):
                edges.append((1 + layer * width + v,
                              1 + (layer + 1) * width + rng.randrange(width),
                              rng.randrange(1, 300)))
    yield "layered", n, edges
    width = 60
    edges = []
    for r in range(width):
        for c in range(width):
            v = r * width + c
            for w in (v + 1 if c + 1 < width else -1,
                      v + width if r + 1 < width else -1):
                if w != -1:
                    edges.extend(((v, w, rng.randrange(1, 100)),
                                  (w, v, rng.randrange(1, 100))))
    yield "grid", width * width, edges
    size = 500
    n = size * 2 + 2
    edges = [(0, v + 1, 1) for v in range(size)]
    edges += [(v + size + 1, n - 1, 1) for v in range(size)]
    edges += [(rng.randrange(size) + 1, rng.randrange(size) + size + 1, 1)
              for _ in range(8000)]
    yield "bipartite", n, edges
    n = 300
    edges = [(0, 1, 10**30), (0, n - 2, 10**30), (n - 2, n - 1, 7)]
    edges += [(v, v + 1, 10**30) for v in range(1, n - 3)]
    yield "dead_end", n, edges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertices", type=int, default=300)
    parser.add_argument("--density", type=float, default=0.12)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--seed", type=int, default=801)
    parser.add_argument("--suite", action="store_true")
    parser.add_argument("--baseline-ref")
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("repeat must be positive")
    backends = [("Dinic", MaxFlowGraph), ("Highest", PushRelabel)]
    if args.baseline_ref:
        backends.append(("FIFO", historical_fifo(args.baseline_ref)))
    cases = suite(args.seed) if args.suite else [
        ("random", args.vertices, build_edges(args.vertices, args.density, args.seed))]
    print("case V E " + " ".join(name + "_ms" for name, _ in backends), flush=True)
    for name, n, edges in cases:
        results = [run(backend, n, edges, args.repeat) for _, backend in backends]
        if len({value for value, _ in results}) != 1:
            raise AssertionError("flow implementations disagree")
        print(name, n, len(edges), *(f"{elapsed * 1000:.3f}" for _, elapsed in results), flush=True)
        if not args.suite:
            print(f"Dinic:       {results[0][1]:.6f}s")
            print(f"PushRelabel: {results[1][1]:.6f}s")
            print(f"ratio:       {results[0][1] / results[1][1]:.3f}x")


if __name__ == "__main__":
    main()
