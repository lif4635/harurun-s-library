import bisect
import random

import pytest

from library_codex.ordered_set.BinaryTrie import BinaryTrie


def test_binary_trie_random_multiset_and_lazy_xor():
    rng = random.Random(820641)
    bit_length = 10
    mask = (1 << bit_length) - 1
    solver = BinaryTrie(bit_length)
    values = []
    for _ in range(20000):
        kind = rng.randrange(7)
        if kind <= 1:
            value = rng.randrange(mask + 1)
            solver.add(value)
            bisect.insort(values, value)
        elif kind == 2 and values:
            value = rng.choice(values)
            solver.discard(value)
            values.remove(value)
        elif kind == 3:
            value = rng.randrange(mask + 1)
            solver.xor_all(value)
            values = sorted(item ^ value for item in values)
        elif values:
            index = rng.randrange(len(values))
            value = rng.randrange(mask + 1)
            assert solver.kth(index) == values[index]
            assert solver.bisect_left(value) == bisect.bisect_left(values, value)
            assert solver.xor_min(value) == min(values, key=lambda item: item ^ value)
            assert solver.xor_max(value) == max(values, key=lambda item: item ^ value)
        assert len(solver) == len(values)


def test_counts_boundaries_reuse_and_debug():
    tree = BinaryTrie(60)
    with pytest.raises(IndexError):
        tree.min()
    with pytest.raises(ValueError):
        tree.add(1 << 60)
    with pytest.raises(ValueError):
        tree.add(-1)
    with pytest.raises(ValueError):
        tree.xor_all(-1)
    for cycle in range(100):
        values = [(cycle << 40) + i for i in range(64)]
        for x in values:
            tree.add(x, 3)
        assert len(tree.count) == 127
        assert tree.tolist() == [x for x in values for _ in range(3)]
        assert str(tree) == str(tree.tolist())
        assert repr(tree) == "BinaryTrie(%r)" % tree.tolist()
        assert tree.bisect_left(-1) == 0
        assert tree.bisect_left(1 << 60) == len(tree)
        assert tree.count_value(-1) == tree.count_value(1 << 60) == 0
        for x in values:
            assert tree.discard(x, 2) == 2
            assert tree.discard(x, 9) == 1
            assert tree.discard(x) == 0
        assert len(tree) == 0
        assert len(tree.free) == len(tree.count)
        tree.xor_all(cycle)
    tree.add(7)
    tree.add(7, 100000)
    assert len(tree) == 100001
    assert tree.max() == 7


def test_exhaustive_small_sets_and_xor():
    for mask in range(256):
        tree = BinaryTrie(3)
        values = [x for x in range(8) if mask >> x & 1]
        for x in reversed(values):
            tree.add(x)
        for change in range(8):
            tree.xor_all(change)
            values = sorted(x ^ change for x in values)
            assert tree.tolist() == values
            assert [tree.kth(i) for i in range(len(tree))] == values
            for x in range(-1, 10):
                assert tree.bisect_left(x) == bisect.bisect_left(values, x)
            if values:
                for x in range(16):
                    assert tree.xor_min(x) == min(values, key=lambda v: v ^ x)
                    assert tree.xor_max(x) == max(values, key=lambda v: v ^ x)


def test_catalog_contract_and_standalone(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    catalog = json.loads((root / "library-catalog.json").read_text())
    module = next(m for m in catalog["modules"] if m["modulePath"] == "library_codex.ordered_set.BinaryTrie")
    assert module["article"]
    methods = {m["name"]: m for m in module["classes"][0]["methods"]}
    assert methods['xor_min']['returnFormat'] == 'int'
    assert 'XORした結果ではなく' in methods['xor_min']['returnDescription']
    script = tmp_path / "standalone.py"
    script.write_text(module["standaloneCode"] + "\ntree = BinaryTrie(8)\ntree.add(3, 2)\ntree.xor_all(1)\nassert tree.tolist() == [2, 2]\nassert tree.xor_min(7) == 2\n")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=20)
