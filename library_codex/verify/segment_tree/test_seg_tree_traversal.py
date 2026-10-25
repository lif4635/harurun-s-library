import random
import ast
from pathlib import Path
import subprocess
import sys

import pytest

from library_codex.segment_tree.SegTreeTraversal import build, fold, update
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


@pytest.mark.parametrize("size", [1, 2, 4, 8, 32, 128])
def test_noncommutative_order(size):
    data = [""] * (size * 2)
    data[size:] = [chr(33 + i % 80) for i in range(size)]
    calls = []

    def pull(node):
        calls.append(node)
        data[node] = data[node * 2] + data[node * 2 + 1]

    build(size, pull)
    assert calls == list(range(size - 1, 0, -1))
    for left in range(size + 1):
        for right in range(left, size + 1):
            nodes = []

            def prepend(node, result):
                nodes.append(node)
                return data[node] + result

            assert fold(size, left, right, prepend, "!") == "".join(data[size + left:size + right]) + "!"
            assert len(nodes) <= 2 * size.bit_length()
    for index in range(size):
        data[size + index] = "x"
        calls.clear()
        update(size, index, pull)
        assert len(calls) == size.bit_length() - 1
        assert data[1] == "".join(data[size:])


def test_validation():
    for size in [0, -1, 3, 6]:
        with pytest.raises(ValueError):
            build(size, lambda node: None)
    for index in [-1, 8]:
        with pytest.raises(IndexError):
            update(8, index, lambda node: None)
    for left, right in [(-1, 1), (3, 2), (0, 9)]:
        with pytest.raises(IndexError):
            fold(8, left, right, lambda node, result: result, None)
    token = object()
    assert fold(1, 0, 0, lambda *args: pytest.fail("empty interval"), token) is token


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
        for node in range(1, tree.size * 2):
            height = tree.size.bit_length() - node.bit_length()
            left = (node << height) - tree.size
            right = left + (1 << height)
            digits = []
            for c in text[left:right]:
                if c != "B":
                    digits.append(c)
                elif digits:
                    digits.pop()
            for count in range(len(digits) + 1):
                assert tree._prefix(node, count) == normalize(digits[:count])[2]
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


def test_variants():
    from library_codex.benchmarks.seg_tree_traversal import stack_fold

    size = 128
    data = [""] * (size * 2)
    data[size:] = [chr(33 + i % 80) for i in range(size)]
    build(size, lambda node: data.__setitem__(node, data[node * 2] + data[node * 2 + 1]))
    prepend = lambda node, value: data[node] + value
    for left in range(size + 1):
        for right in range(left, size + 1):
            assert fold(size, left, right, prepend, "") == stack_fold(size, left, right, prepend, "")
