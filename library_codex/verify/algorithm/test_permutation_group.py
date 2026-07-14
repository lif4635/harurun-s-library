import itertools
import random

from library_codex.algorithm.PermutationGroup import simplify_permutation_subgroup


def _compose(first, second):
    return tuple(first[second[index]] for index in range(len(first)))


def _closure(n, generators):
    identity = tuple(range(n))
    seen = {identity}
    queue = [identity]
    for current in queue:
        for generator in generators:
            value = _compose(generator, current)
            if value not in seen:
                seen.add(value)
                queue.append(value)
    return seen


def test_simplify_permutation_subgroup_small_random_groups():
    rng = random.Random(314159)
    for n in range(1, 8):
        all_permutations = list(itertools.permutations(range(n)))
        for _ in range(30):
            generators = [list(rng.choice(all_permutations))
                          for _ in range(rng.randrange(5))]
            basis = simplify_permutation_subgroup(n, generators)
            flattened = [permutation for level in basis for permutation in level]
            assert _closure(n, generators) == _closure(n, flattened)
            order = 1
            for fixed, level in enumerate(basis):
                images = {permutation[fixed] for permutation in level}
                assert len(images) == len(level)
                for permutation in level:
                    assert permutation[fixed + 1:] == list(range(fixed + 1, n))
                order *= len(level) or 1
            assert order == len(_closure(n, generators))

