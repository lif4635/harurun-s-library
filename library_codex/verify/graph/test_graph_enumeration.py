import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from graph_enumeration.EnumerateTriangles import enumerate_triangles  # noqa: E402


def test_triangle_enumeration_vertices_edges_and_callback():
    rng = random.Random(3)
    for n in range(1, 20):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(30):
            edges = [edge for edge in pairs if rng.randrange(5) == 0]
            edge_id = {edge: i for i, edge in enumerate(edges)}
            expected = {
                (u, v, w)
                for u in range(n) for v in range(u + 1, n)
                for w in range(v + 1, n)
                if (u, v) in edge_id and (u, w) in edge_id
                and (v, w) in edge_id
            }
            items = enumerate_triangles(n, edges)
            actual = set()
            for u, v, w, a, b, c in items:
                actual.add(tuple(sorted((u, v, w))))
                incident = {
                    tuple(sorted(edges[a])), tuple(sorted(edges[b])),
                    tuple(sorted(edges[c])),
                }
                assert incident == {
                    tuple(sorted((u, v))), tuple(sorted((u, w))),
                    tuple(sorted((v, w))),
                }
            assert actual == expected
            called = []
            count = enumerate_triangles(
                n, edges, lambda *item: called.append(item)
            )
            assert count == len(called) == len(expected)
