import random
import ast
from pathlib import Path
import subprocess
import sys

import pytest

from library_codex.segment_tree.SegTreeTraversal import SegTreeTraversal
from verify.atcoder.abc434_g import Keyboard


def normalize(text):
    back = 0
    digits = []
    for char in text:
        if char != "B":
            digits.append(char)
        elif digits:
            digits.pop()
        else:
            back += 1
    value = 0
    for char in digits:
        value = (value * 10 + int(char)) % 998244353
    return back, len(digits), value


@pytest.mark.parametrize("n", [0, 1, 2, 3, 7, 32, 65, 128])
def test_noncommutative_order(n):
    values = [chr(33 + i % 80) for i in range(n)]
    calls = []

    def merge(data, node, right):
        calls.append(node)
        assert node > 0
        return data[node] + right

    tree = SegTreeTraversal(merge, "", values)
    assert len(calls) == tree.size - 1
    for left in range(n + 1):
        for right in range(left, n + 1):
            calls.clear()
            assert tree.prod(left, right) == "".join(values[left:right])
            assert len(calls) <= 2 * tree.size.bit_length()
    for index in range(n):
        calls.clear()
        tree.set(index, "x")
        values[index] = "x"
        assert len(calls) == tree.size.bit_length() - 1
        assert tree.get(index) == "x"
        assert tree.all_prod() == "".join(values)
    assert len(tree) == n
    assert tree.tolist() == values
    assert str(tree) == str(values)
    assert repr(tree) == "SegTreeTraversal(%r)" % values
    assert tree.prod(0, n) == "".join(values)


def test_validation():
    merge = lambda data, node, right: data[node] + right
    with pytest.raises(ValueError):
        SegTreeTraversal(merge, 0, -1)
    with pytest.raises(ValueError):
        SegTreeTraversal(merge, 0, [1], storage=lambda n, e: [])
    tree = SegTreeTraversal(merge, 0, [1, 2, 3])
    for index in [-1, 3, 4]:
        with pytest.raises(IndexError):
            tree.set(index, 99)
        with pytest.raises(IndexError):
            tree.get(index)
    for left, right in [(-1, 1), (3, 2), (0, 4)]:
        with pytest.raises(IndexError):
            tree.prod(left, right)
    assert tree.tolist() == [1, 2, 3]
    token = object()
    empty = SegTreeTraversal(lambda *args: pytest.fail("empty interval"), token, [])
    assert empty.prod(0, 0) is token
    assert empty.all_prod() is token


def test_storage_and_iterable():
    from array import array

    merge = lambda data, node, right: data[node] + right
    tree = SegTreeTraversal(merge, 0, (i for i in range(5)))
    assert tree.tolist() == list(range(5))
    assert tree.all_prod() == 10
    tree = SegTreeTraversal(merge, 0, 5, storage=lambda n, e: array("q", [e]) * n)
    assert isinstance(tree.data, array)
    tree.set(3, 7)
    assert tree.get(3) == 7
    assert tree.prod(1, 5) == 7
    assert tree.tolist() == [0, 0, 0, 7, 0]


@pytest.mark.parametrize("n", [0, 1, 2, 3, 7, 16, 31, 65, 129])
def test_keyboard_random(n):
    rng = random.Random(n)
    text = [rng.choice("123456789BBBB") for _ in range(n)]
    tree = Keyboard("".join(text))
    for _ in range(250):
        if n and rng.randrange(3) == 0:
            index = rng.randrange(n)
            char = rng.choice("123456789BBBB")
            tree.set(index, char)
            text[index] = char
        left = rng.randrange(n + 1)
        right = rng.randrange(left, n + 1)
        assert tree.prod(left, right) == normalize(text[left:right])
        assert tree.prod(0, n) == normalize(text)
    assert tree.tolist() == text
    assert str(tree) == "".join(text)
    assert repr(tree) == "Keyboard(%r)" % "".join(text)
    assert tree.prod(0, n) == normalize(text)


def test_keyboard_prefix_and_boundaries():
    for text in ["B" * 35, "1" * 35, "1234567891BBBBBBB456", "9B" * 80, "B23567", "1" * 70 + "B" * 40 + "23456789"]:
        tree = Keyboard(text)
        for node in range(1, tree.tree.size * 2):
            height = tree.tree.size.bit_length() - node.bit_length()
            left = (node << height) - tree.tree.size
            right = left + (1 << height)
            digits = []
            for c in text[left:right]:
                if c != "B":
                    digits.append(c)
                elif digits:
                    digits.pop()
            for count in range(len(digits) + 1):
                assert tree.tree.merge(tree.tree.data, node, (len(digits) - count, 0, 0, 0))[2] == normalize(digits[:count])[2]
        for left in range(len(text) + 1):
            for right in range(left, len(text) + 1):
                assert tree.prod(left, right) == normalize(text[left:right])
    tree = Keyboard("19B")
    for index in [-1, 3]:
        with pytest.raises(IndexError):
            tree.set(index, "1")
    for value in ["0", "x"]:
        with pytest.raises(ValueError):
            tree.set(0, value)
        with pytest.raises(ValueError):
            Keyboard(value)
    assert str(tree) == "19B"


def test_keyboard_sample():
    tree = Keyboard("1234567891")
    commands = [(2, 5, 7), (2, 2, 8), (2, 1, 10), (1, 3, "B"), (1, 4, "B"), (2, 2, 4), (2, 2, 8), (2, 1, 10), (1, 7, "B"), (2, 3, 9), (1, 3, "4"), (2, 1, 10)]
    answers = []
    for kind, a, b in commands:
        if kind == 1:
            tree.set(a - 1, b)
        else:
            _, length, value = tree.prod(a - 1, b)
            answers.append(value if length else -1)
    assert answers == [567, 2345678, 236323538, -1, 5678, 567891, 589, 125891]


def test_standalone(tmp_path):
    from library_codex.tools.build_library_catalog import build_standalone_code

    root = Path(__file__).resolve().parents[3]
    source, _ = build_standalone_code(root / "verify/atcoder/abc434_g.py", root / "library_codex")
    saved = (root / "verify/atcoder/abc434_g_standalone.py").read_text(encoding="utf-8")
    assert ast.dump(ast.parse(source)) == ast.dump(ast.parse(saved))
    assert "from library_codex" not in saved
    sample = "10 12\n1234567891\n2 5 7\n2 2 8\n2 1 10\n1 3 B\n1 4 B\n2 2 4\n2 2 8\n2 1 10\n1 7 B\n2 3 9\n1 3 4\n2 1 10\n"
    run = subprocess.run([sys.executable, "-I", "-c", saved], input=sample, text=True, capture_output=True, cwd=tmp_path, check=True)
    assert run.stdout.split() == ["567", "2345678", "236323538", "-1", "5678", "567891", "589", "125891"]


def test_default_storage_supports_descendant_merge():
    def merge(data, node, right):
        text, removed = right
        left_text, left_removed = data[node]
        keep = len(left_text) - removed
        if keep <= 0:
            return text, left_removed - keep
        while node * 2 < len(data) and len(data[node * 2][0]) >= keep:
            node *= 2
        return data[node][0][:keep] + text, left_removed

    values = [("a", 0), ("b", 0), ("c", 0), ("", 2)]
    tree = SegTreeTraversal(merge, ("", 0), values)
    assert tree.prod(0, 4) == ("a", 0)
    tree.set(1, ("", 1))
    assert tree.prod(0, 4) == ("", 1)
