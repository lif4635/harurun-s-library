"""Reproducible list-adjacency versus CSR graph benchmark."""

import argparse
import random
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from library_codex.graph.CSRGraph import (
    CSRGraph,
    CSRLowLink,
    CSRStronglyConnectedComponents,
    dijkstra_csr,
)
from library_codex.graph.LowLink import LowLink
from library_codex.graph.ShortestPath import dijkstra
from library_codex.graph.StronglyConnectedComponents import StronglyConnectedComponents


def make_edges(n, m, seed, weighted):
    rng = random.Random(seed)
    edges = [(vertex, vertex + 1, 1) for vertex in range(n - 1)]
    while len(edges) < m:
        source = rng.randrange(n)
        target = rng.randrange(n)
        weight = rng.randrange(1, 1_000_001) if weighted else 1
        edges.append((source, target, weight))
    return edges


def list_graph(n, edges, undirected=False):
    graph = [[] for _ in range(n)]
    for source, target, weight in edges:
        graph[source].append((target, weight))
        if undirected:
            graph[target].append((source, weight))
    return graph


def timed(function):
    started = perf_counter()
    result = function()
    return result, perf_counter() - started


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--algorithm", choices=("dijkstra", "scc", "lowlink"), default="dijkstra")
    parser.add_argument("--backend", choices=("list", "csr"), required=True)
    parser.add_argument("--vertices", type=int, default=100000)
    parser.add_argument("--edges", type=int, default=500000)
    parser.add_argument("--seed", type=int, default=8200)
    args = parser.parse_args()
    weighted = args.algorithm == "dijkstra"
    edges = make_edges(args.vertices, args.edges, args.seed, weighted)

    if args.algorithm == "dijkstra":
        if args.backend == "list":
            graph, build_time = timed(lambda: list_graph(args.vertices, edges))
            answer, solve_time = timed(lambda: dijkstra(graph, 0)[0])
        else:
            graph, build_time = timed(lambda: CSRGraph(args.vertices, edges))
            answer, solve_time = timed(lambda: dijkstra_csr(graph, 0)[0])
        checksum = sum(value for value in answer if value != float("inf"))
    elif args.algorithm == "scc":
        if args.backend == "list":
            graph, build_time = timed(lambda: list_graph(args.vertices, edges))
            answer, solve_time = timed(lambda: StronglyConnectedComponents(graph))
        else:
            graph, build_time = timed(lambda: CSRGraph(args.vertices, edges))
            answer, solve_time = timed(lambda: CSRStronglyConnectedComponents(graph))
        checksum = answer.count
    else:
        pairs = [(source, target) for source, target, _ in edges]
        build_time = 0.0
        if args.backend == "list":
            answer, solve_time = timed(lambda: LowLink(args.vertices, pairs))
        else:
            answer, solve_time = timed(lambda: CSRLowLink(args.vertices, pairs))
        checksum = len(answer.bridge_ids)

    print(
        f"algorithm={args.algorithm} backend={args.backend} "
        f"vertices={args.vertices} edges={args.edges}"
    )
    print(f"build={build_time:.6f}s solve={solve_time:.6f}s total={build_time + solve_time:.6f}s")
    print(f"checksum={checksum}")


if __name__ == "__main__":
    main()
