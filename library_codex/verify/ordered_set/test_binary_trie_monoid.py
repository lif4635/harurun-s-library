import random
from operator import add

import pytest

from library_codex.ordered_set.BinaryTrieMonoid import BinaryTrieMonoid


@pytest.mark.parametrize("commutative", [False, True])
def test_random_updates_products_and_xor(commutative):
    rng = random.Random(91490)
    identity = 0 if commutative else ""
    tree = BinaryTrieMonoid(add, identity, 8, commutative=commutative)
    values = {}
    for step in range(5000):
        key = rng.randrange(256)
        kind = rng.randrange(5)
        if kind <= 1:
            value = rng.randrange(-20, 21) if commutative else chr(65 + step % 26)
            tree.set(key, value)
            values[key] = value
        elif kind == 2:
            assert tree.discard(key) == (key in values)
            values.pop(key, None)
        elif kind == 3 and commutative:
            tree.xor_all(key)
            values = {k ^ key: v for k, v in values.items()}
        else:
            l, r = sorted([rng.randrange(-5, 262), rng.randrange(-5, 262)])
            expected = identity
            for k, v in sorted(values.items()):
                if l <= k < r:
                    expected = add(expected, v)
            assert tree.prod(l, r) == expected
        assert tree.get(key) == values.get(key, identity)
        assert len(tree) == len(values)
        expected = identity
        for _, v in sorted(values.items()):
            expected = add(expected, v)
        assert tree.all_prod() == expected
        if step % 50 == 0:
            assert tree.items() == sorted(values.items())
            assert str(tree) == str(dict(sorted(values.items())))
            assert repr(tree) == "BinaryTrieMonoid(%r)" % dict(sorted(values.items()))
            assert len(tree.data) - len(tree.free) == max(0, 2 * len(values) - 1)


def test_identity_keys_reuse_and_guard():
    tree = BinaryTrieMonoid(add, "", 40)
    tree.set(10, "")
    assert tree.items() == [(10, "")]
    assert len(tree) == 1
    tree.xor_all(0)
    with pytest.raises(ValueError):
        tree.xor_all(1)
    with pytest.raises(ValueError):
        tree.set(-1, "x")
    assert tree.get(-1) == ""
    assert tree.discard(10)
    assert tree.all_prod() == tree.prod(0, 1 << 40) == ""
    for i in range(500):
        tree.set(i << 20, "a")
        tree.set((i << 20) + 1, "b")
        assert tree.prod(0, 1 << 40) == "ab"
        assert tree.prod((i << 20) + 1, (i << 20) + 2) == "b"
        assert tree.discard(i << 20)
        assert tree.discard((i << 20) + 1)
        assert len(tree.data) == 3


def test_catalog_contract_and_standalone(tmp_path):
    import json
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    catalog = json.loads((root / "library-catalog.json").read_text())
    module = next(m for m in catalog["modules"] if m["modulePath"] == "library_codex.ordered_set.BinaryTrieMonoid")
    assert module["article"]
    methods = {m["name"]: m for m in module["classes"][0]["methods"]}
    assert methods['prod']['returnFormat'] == 'object'
    assert methods['__repr__']['returnFormat'] == 'str'
    script = tmp_path / "standalone.py"
    script.write_text(module["standaloneCode"] + "\ntree = BinaryTrieMonoid(lambda a, b: a + b, '', 8)\ntree.set(7, 'b')\ntree.set(2, 'a')\nassert tree.prod(0, 8) == 'ab'\n")
    subprocess.run([sys.executable, "-I", str(script)], cwd=tmp_path, check=True, timeout=20)
