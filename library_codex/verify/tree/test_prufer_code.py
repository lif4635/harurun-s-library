import itertools
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.tree.PruferCode import (
    prufer_decode,
    prufer_decode_edges,
    prufer_decode_extended,
    prufer_encode,
    prufer_encode_extended,
)


def edge_set(tree):
    return {
        (u, v) if u < v else (v, u)
        for u, edges in enumerate(tree)
        for v in edges
        if u != v
    }


def test_all_codes_up_to_seven_vertices():
    for n in range(1, 8):
        seen = set()
        codes = [()] if n <= 2 else itertools.product(range(n), repeat=n - 2)
        for code in codes:
            tree = prufer_decode(code, n)
            assert prufer_encode(tree) == list(code)
            assert len(edge_set(tree)) == max(0, n - 1)
            seen.add(tuple(sorted(edge_set(tree))))
            extended = prufer_encode_extended(tree)
            assert edge_set(prufer_decode_extended(extended)) == edge_set(tree)
            decoded_edges = {
                (u, v) if u < v else (v, u)
                for u, v in prufer_decode_edges(code, n)
            }
            assert decoded_edges == edge_set(tree)
        assert len(seen) == (1 if n <= 2 else n ** (n - 2))


def test_random_roundtrip():
    rng = random.Random(0)
    for _ in range(10000):
        n = rng.randrange(1, 100)
        code = [rng.randrange(n) for _ in range(max(0, n - 2))]
        tree = prufer_decode(code, n)
        assert prufer_encode(tree) == code


def test_default_and_edge_cases():
    assert prufer_decode([]) == [[1], [0]]
    assert prufer_decode([], 0) == []
    assert prufer_decode([], 1) == [[]]
    tree = prufer_decode([1, 1])
    assert edge_set(tree) == {(0, 1), (1, 2), (1, 3)}


def test_large_without_recursion():
    n = 200000
    code = [(v * 1000003 + 97) % n for v in range(n - 2)]
    tree = prufer_decode(code)
    assert prufer_encode(tree) == code


if __name__ == "__main__":
    test_all_codes_up_to_seven_vertices()
    test_random_roundtrip()
    test_default_and_edge_cases()
    test_large_without_recursion()
