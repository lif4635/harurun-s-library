import itertools
import random
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.DequePalindromicTree import DequePalindromicTree


def brute(sequence):
    palindromes = set()
    prefix = suffix = 0
    for left in range(len(sequence)):
        for right in range(left + 1, len(sequence) + 1):
            part = tuple(sequence[left:right])
            if part == part[::-1]:
                palindromes.add(part)
                if left == 0:
                    prefix = max(prefix, right)
                if right == len(sequence):
                    suffix = max(suffix, right - left)
    return len(palindromes), prefix, suffix


def validate(tree, sequence):
    expected = brute(sequence)
    assert tree.query() == expected
    assert tree.distinct_count == expected[0]
    assert tree.longest_prefix == expected[1]
    assert tree.longest_suffix == expected[2]
    assert len(tree) == len(sequence)
    assert tree.tolist() == sequence
    assert str(tree) == str(sequence)
    assert repr(tree) == "DequePalindromicTree(" + repr(sequence) + ")"
    assert tree.query() == expected
    assert len(tree._edges) == expected[0]
    assert len(tree._length) - len(tree._free) == expected[0] + 2


def operate(tree, sequence, operation, symbol=0):
    if operation == 0:
        assert tree.appendleft(symbol) is None
        sequence.insert(0, symbol)
    elif operation == 1:
        assert tree.append(symbol) is None
        sequence.append(symbol)
    elif operation == 2:
        assert tree.popleft() == sequence.pop(0)
    else:
        assert tree.pop() == sequence.pop()


def test_empty_and_invalid_symbol():
    tree = DequePalindromicTree()
    validate(tree, [])
    for remove in (tree.pop, tree.popleft):
        with pytest.raises(IndexError):
            remove()
        validate(tree, [])
    for append in (tree.append, tree.appendleft):
        with pytest.raises(TypeError):
            append([])
        validate(tree, [])


def test_exhaustive_operation_sequences():
    for operations in itertools.product(range(6), repeat=6):
        tree = DequePalindromicTree()
        sequence = []
        for operation in operations:
            if operation < 4:
                operate(tree, sequence, operation & 1, operation >> 1)
            elif sequence:
                operate(tree, sequence, operation - 2)
            else:
                break
            validate(tree, sequence)


def test_random_updates_and_reuse():
    rng = random.Random(20261005)
    for alphabet in ([0, 1], [None, "a", (2, 3)], list(range(8))):
        for _ in range(20):
            tree = DequePalindromicTree()
            sequence = []
            for _ in range(300):
                operation = rng.randrange(4 if sequence else 2)
                if len(sequence) >= 30:
                    operation = rng.randrange(2, 4)
                operate(tree, sequence, operation, rng.choice(alphabet))
                validate(tree, sequence)


def test_ring_wrap_and_growth():
    rng = random.Random(17)
    tree = DequePalindromicTree("abacaba")
    sequence = list("abacaba")
    for _ in range(300):
        for _ in range(3):
            operate(tree, sequence, 0, rng.choice("abcd"))
        for _ in range(2):
            operate(tree, sequence, 3)
        if len(sequence) > 60:
            for _ in range(40):
                operate(tree, sequence, 2)
        validate(tree, sequence)


def test_node_storage_bounded_by_peak_length():
    tree = DequePalindromicTree()
    for value in range(10000):
        tree.append(value)
        tree.appendleft(value)
        assert tree.query() == (2, 2, 2)
        assert tree.pop() == value
        assert tree.popleft() == value
    assert len(tree._length) == 4
    assert len(tree._data) == 8
    assert not tree._edges
    validate(tree, [])


def test_article_example():
    tree = DequePalindromicTree("ababa")
    assert tree.query() == (5, 5, 5)
    tree.append("c")
    assert tree.query() == (6, 5, 1)
    assert tree.popleft() == "a"
    assert tree.query() == (5, 3, 1)
    tree.appendleft("c")
    assert tree.query() == (5, 1, 1)
    validate(tree, list("cbabac"))


def test_repeated_failure_link_search():
    for front in (False, True):
        tree = DequePalindromicTree("a" * 20000)
        append = tree.appendleft if front else tree.append
        pop = tree.popleft if front else tree.pop
        for _ in range(20000):
            append("b")
            assert tree.query() == ((20001, 1, 20000) if front else (20001, 20000, 1))
            assert pop() == "b"
        assert tree.query() == (20000, 20000, 20000)


def test_long_repeated_and_alternating():
    for sequence in ("a" * 20000, "ab" * 10000):
        tree = DequePalindromicTree(sequence)
        while len(tree):
            size = len(tree)
            longest = size if sequence[0] == sequence[1] else size - (size % 2 == 0)
            assert tree.query() == (size, longest, longest)
            if size & 1:
                tree.pop()
            else:
                tree.popleft()
        validate(tree, [])
