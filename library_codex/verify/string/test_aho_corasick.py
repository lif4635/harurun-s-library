from collections import Counter
import random
import string
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from library_codex.string.AhoCorasick import AhoCorasick
from library_codex.string.CompressedTrie import CompressedTrie
from library_codex.string.Trie import Trie


def occurrence_positions(text, pattern):
    if not pattern:
        return list(range(len(text) + 1))
    return [
        start for start in range(len(text) - len(pattern) + 1)
        if text[start:start + len(pattern)] == pattern
    ]


def test_trie_and_compressed_trie():
    rng = random.Random(0)
    for _ in range(3000):
        words = [
            "".join(rng.choice("abc") for _ in range(rng.randrange(15)))
            for _ in range(rng.randrange(50))
        ]
        expected = Counter(words)
        trie = Trie()
        dense = Trie("abc")
        compressed = CompressedTrie(words)
        for i, word in enumerate(words):
            trie.add(word, i)
            dense.add(word, i)
        candidates = words + [
            "".join(rng.choice("abcd") for _ in range(rng.randrange(15)))
            for _ in range(30)
        ]
        for word in candidates:
            assert trie.count(word) == expected[word]
            assert dense.count(word) == expected[word]
            assert compressed.count(word) == expected[word]
            for end in range(len(word) + 1):
                prefix = word[:end]
                count = sum(value for key, value in expected.items() if key.startswith(prefix))
                assert trie.prefix_count(prefix) == count
                assert dense.prefix_count(prefix) == count
                assert compressed.prefix_count(prefix) == count
        assert trie.word_count == dense.word_count == compressed.word_count == len(words)
        assert compressed.node_count <= 2 * len(expected) + 1


def test_trie_operations():
    for trie in (Trie(), Trie("abc")):
        root = trie.add("", 10, 2)
        ab = trie.add("ab", 11, 3)
        abc = trie.add("abc", 12)
        assert root == 0
        assert trie.word_count == 6
        assert trie.ids(root) == [10]
        assert trie.ids(ab) == [11]
        assert trie.ids(abc) == [12]
        assert list(trie.iter_prefixes("abc")) == [
            (0, root), (2, ab), (3, abc)
        ]
        assert trie.longest_prefix("abca") == (3, abc)
        assert Counter(dict(trie.words())) == Counter({(): 2, ("a", "b"): 3, ("a", "b", "c"): 1})
        assert trie.erase("ab", 2)
        assert trie.count("ab") == 1
        assert trie.prefix_count("a") == 2
        assert not trie.erase("ab", 2)
        assert not trie.erase("ac")


def validate_aho(patterns, text, alphabet=None):
    aho = AhoCorasick(alphabet)
    for pattern_id, pattern in enumerate(patterns):
        assert aho.add(pattern, pattern_id + 1000) == pattern_id
    aho.build()
    expected_positions = [
        occurrence_positions(text, pattern) for pattern in patterns
    ]
    expected_counts = list(map(len, expected_positions))
    assert aho.count_by_pattern(text) == expected_counts
    assert aho.count_matches(text) == sum(expected_counts)
    assert aho.match(text) == sum(expected_counts)
    assert aho.match(text, True) == {
        pattern_id + 1000: count
        for pattern_id, count in enumerate(expected_counts)
    }
    assert aho.match_positions(text) == expected_positions
    actual = Counter(aho.finditer(text))
    expected = Counter(
        (start + len(pattern), pattern_id + 1000)
        for pattern_id, pattern in enumerate(patterns)
        for start in expected_positions[pattern_id]
    )
    assert actual == expected
    failure_tree = aho.failure_tree()
    assert sum(map(len, failure_tree)) == len(aho) - 1


def test_random_aho_against_brute():
    rng = random.Random(1)
    for _ in range(5000):
        patterns = [
            "".join(rng.choice("abc") for _ in range(rng.randrange(10)))
            for _ in range(rng.randrange(20))
        ]
        text = "".join(rng.choice("abcd") for _ in range(rng.randrange(50)))
        validate_aho(patterns, text)
        validate_aho(patterns, text, "abc")


def test_integer_alphabet():
    patterns = [(), (1,), (1, 2), (2, 1), (1, 2)]
    text = (1, 2, 1, 2, 3, 1)
    validate_aho(patterns, text)
    validate_aho(patterns, text, range(4))


def test_dense_without_completed_transitions():
    patterns = ["aabx", "ab", "bx", "x", ""]
    text = "aaabxaabxabx"
    aho = AhoCorasick("abx")
    for pattern in patterns:
        aho.add(pattern)
    aho.build(False)
    expected = [len(occurrence_positions(text, pattern)) for pattern in patterns]
    assert aho.count_by_pattern(text) == expected
    assert aho.count_matches(text) == sum(expected)
    assert aho.match_positions(text) == [
        occurrence_positions(text, pattern) for pattern in patterns
    ]


def test_deep_pattern_without_recursion():
    n = 300000
    pattern = "a" * n
    aho = AhoCorasick("ab")
    aho.add(pattern)
    aho.add("b")
    aho.build()
    assert aho.count_by_pattern(pattern + "b") == [1, 1]
    assert aho.node_count == n + 2


if __name__ == "__main__":
    test_trie_and_compressed_trie()
    test_trie_operations()
    test_random_aho_against_brute()
    test_integer_alphabet()
    test_dense_without_completed_transitions()
    test_deep_pattern_without_recursion()
