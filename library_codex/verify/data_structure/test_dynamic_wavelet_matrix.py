from __future__ import annotations

import random
import unittest

from library_codex.data_structure.DynamicWaveletMatrix import (
    CompressedDynamicWaveletMatrix,
    DynamicWaveletMatrix,
    OfflineDynamicWaveletMatrix,
    dynamic_range_min_count_sum_at_least,
)


def brute_min_count(values: list[int], target: int) -> int:
    if target <= 0:
        return 0
    total = 0
    for count, value in enumerate(sorted(values, reverse=True), 1):
        total += value
        if total >= target:
            return count
    return -1


class ImmediateBackendsTest(unittest.TestCase):
    def assert_queries(self, matrix, values, left, right, lower, upper, target):
        segment = values[left:right]
        ordered = sorted(segment)

        self.assertEqual(matrix.range_sum(left, right), sum(segment))
        self.assertEqual(matrix.count_lt(left, right, upper), sum(
            value < upper for value in segment
        ))
        self.assertEqual(matrix.count_le(left, right, upper), sum(
            value <= upper for value in segment
        ))
        self.assertEqual(matrix.rank(left, right, lower), segment.count(lower))
        self.assertEqual(matrix.range_freq(left, right, lower), sum(
            value < lower for value in segment
        ))
        self.assertEqual(matrix.range_freq(left, right, lower, upper), sum(
            lower <= value < upper for value in segment
        ))
        self.assertEqual(matrix.sum_lt(left, right, upper), sum(
            value for value in segment if value < upper
        ))
        self.assertEqual(matrix.sum_le(left, right, upper), sum(
            value for value in segment if value <= upper
        ))
        self.assertEqual(matrix.sum_range(left, right, lower), sum(
            value for value in segment if value < lower
        ))
        self.assertEqual(matrix.sum_range(left, right, lower, upper), sum(
            value for value in segment if lower <= value < upper
        ))
        self.assertEqual(
            matrix.min_count_sum_at_least(left, right, target),
            brute_min_count(segment, target),
        )

        below = [value for value in segment if value < upper]
        above = [value for value in segment if value >= lower]
        self.assertEqual(
            matrix.prev_value(left, right, upper, None),
            max(below) if below else None,
        )
        self.assertEqual(
            matrix.next_value(left, right, lower, None),
            min(above) if above else None,
        )
        at_most = [value for value in segment if value <= lower]
        self.assertEqual(
            matrix.max_le(left, right, lower, None),
            max(at_most) if at_most else None,
        )
        self.assertEqual(
            matrix.min_ge(left, right, lower, None),
            min(above) if above else None,
        )

        for k in {0, len(segment) // 2, len(segment)}:
            self.assertEqual(matrix.sum_k_smallest(left, right, k), sum(ordered[:k]))
            self.assertEqual(matrix.sum_k_largest(left, right, k), sum(ordered[-k:]) if k else 0)
        if segment:
            k = len(segment) // 2
            self.assertEqual(matrix.kth_smallest(left, right, k), ordered[k])
            self.assertEqual(matrix.kth_largest(left, right, k), ordered[-k - 1])

    def test_random_differential(self):
        for seed in range(20):
            random.seed(seed)
            n = random.randint(1, 18)
            initial = [random.randint(1, 80) for _ in range(n)]
            updates = [
                (random.randrange(n), random.randint(1, 120))
                for _ in range(50)
            ]
            matrices = [
                DynamicWaveletMatrix(initial),
                CompressedDynamicWaveletMatrix(initial, updates),
            ]
            values = initial[:]

            for index, value in updates:
                values[index] = value
                for matrix in matrices:
                    matrix.set(index, value)
                    self.assertEqual(matrix.tolist(), values)

                for _ in range(3):
                    left = random.randrange(n + 1)
                    right = random.randrange(left, n + 1)
                    lower = random.randint(-10, 130)
                    upper = random.randint(-10, 130)
                    target = random.randint(-10, sum(values[left:right]) + 20)
                    for matrix in matrices:
                        self.assert_queries(
                            matrix, values, left, right, lower, upper, target
                        )

    def test_empty_and_validation(self):
        for matrix in (
            DynamicWaveletMatrix([]),
            CompressedDynamicWaveletMatrix([]),
        ):
            self.assertEqual(matrix.tolist(), [])
            self.assertEqual(matrix.range_sum(0, 0), 0)
            self.assertEqual(matrix.count_lt(0, 0, 10), 0)
            self.assertEqual(matrix.sum_k_smallest(0, 0, 0), 0)
            self.assertEqual(matrix.min_count_sum_at_least(0, 0, 1), -1)
            with self.assertRaises(IndexError):
                matrix.kth_smallest(0, 0, 0)

        with self.assertRaises(TypeError):
            DynamicWaveletMatrix([True])
        with self.assertRaises(TypeError):
            DynamicWaveletMatrix([1]).set(True, 2)
        with self.assertRaises(TypeError):
            DynamicWaveletMatrix([1]).count_lt(0, 1, 1.5)
        with self.assertRaises(ValueError):
            CompressedDynamicWaveletMatrix([1], [(0, 2)]).set(0, 3)
        for constructor in (
            DynamicWaveletMatrix,
            CompressedDynamicWaveletMatrix,
            OfflineDynamicWaveletMatrix,
        ):
            with self.assertRaises(OverflowError):
                constructor([1 << 64])
        for matrix in (
            DynamicWaveletMatrix([1]),
            CompressedDynamicWaveletMatrix([1]),
            OfflineDynamicWaveletMatrix([1]),
        ):
            with self.assertRaises(OverflowError):
                matrix.set(0, 1 << 64)
            self.assertEqual(matrix.access(0), 1)

    def test_new_maximum_and_python_integer_sums(self):
        matrix = DynamicWaveletMatrix([1, 2, 3])
        matrix.set(1, 2**40 + 7)
        self.assertEqual(matrix.max_bit, (2**40 + 7).bit_length())
        self.assertEqual(matrix.kth_largest(0, 3, 0), 2**40 + 7)
        matrix.set(1, 2)
        self.assertEqual(matrix.max_bit, 2)

        maximum = (1 << 64) - 1
        huge = DynamicWaveletMatrix([maximum], python_int_sum=True)
        self.assertEqual(huge.range_sum(0, 1), maximum)
        self.assertEqual(huge.kth_smallest(0, 1, 0), maximum)
        with self.assertRaises(OverflowError):
            DynamicWaveletMatrix([2**63])

        width = 64
        limit = 1 << width
        right_chain = [
            limit - (1 << bit) for bit in range(width - 1, -1, -1)
        ]
        chained = DynamicWaveletMatrix(right_chain, python_int_sum=True)
        self.assertEqual(chained.kth_largest(0, width, 0), limit - 1)

    def test_u64_patricia_traversal(self):
        random.seed(20260719)
        initial = [random.randrange(1, 1 << 64) for _ in range(9)]
        updates = [
            (random.randrange(9), random.randrange(1, 1 << 64))
            for _ in range(35)
        ]
        matrices = (
            DynamicWaveletMatrix(initial, python_int_sum=True),
            CompressedDynamicWaveletMatrix(initial, updates),
        )
        values = initial[:]
        for index, value in updates:
            for matrix in matrices:
                matrix.set(index, value)
            values[index] = value
            for _ in range(3):
                left = random.randrange(10)
                right = random.randrange(left, 10)
                lower = random.getrandbits(65)
                upper = random.getrandbits(65)
                target = random.randrange(sum(values[left:right]) + 2)
                for matrix in matrices:
                    self.assert_queries(
                        matrix, values, left, right, lower, upper, target
                    )


class OfflineBackendTest(unittest.TestCase):
    def test_failed_registration_is_atomic(self):
        solver = OfflineDynamicWaveletMatrix([7])
        with self.assertRaises(TypeError):
            solver.range_sum(0.0, 1)
        self.assertEqual(solver.query_count, 0)
        query_id = solver.range_sum(0, 1)
        self.assertEqual(query_id, 0)
        self.assertEqual(solver.solve(), [7])

    def test_random_differential(self):
        for seed in range(30):
            random.seed(10_000 + seed)
            n = random.randint(1, 15)
            values = [random.randint(1, 70) for _ in range(n)]
            solver = OfflineDynamicWaveletMatrix(values)
            expected = []

            for _ in range(80):
                if random.random() < 0.35:
                    index = random.randrange(n)
                    value = random.randint(1, 100)
                    solver.set(index, value)
                    values[index] = value
                    continue

                left = random.randrange(n + 1)
                right = random.randrange(left, n + 1)
                kind = random.randrange(4) if left < right else random.choice((0, 3))
                segment = values[left:right]
                if kind == 0:
                    target = random.randint(-5, sum(segment) + 15)
                    query_id = solver.min_count_sum_at_least(left, right, target)
                    answer = brute_min_count(segment, target)
                elif kind == 1:
                    k = random.randrange(len(segment))
                    query_id = solver.kth_smallest(left, right, k)
                    answer = sorted(segment)[k]
                elif kind == 2:
                    k = random.randrange(len(segment))
                    query_id = solver.kth_largest(left, right, k)
                    answer = sorted(segment, reverse=True)[k]
                else:
                    query_id = solver.range_sum(left, right)
                    answer = sum(segment)
                self.assertEqual(query_id, len(expected))
                expected.append(answer)

            self.assertEqual(solver.solve(), expected)
            self.assertEqual(solver.solve(), expected)
            for query_id, answer in enumerate(expected):
                self.assertEqual(solver.answer(query_id), answer)
            with self.assertRaises(RuntimeError):
                solver.set(0, 1)

    def test_kth_only_fast_path(self):
        values = [9, 1, 7, 3, 5]
        solver = OfflineDynamicWaveletMatrix(values)
        expected = []
        for step in range(25):
            index = step % len(values)
            value = step * 7 + 1
            solver.set(index, value)
            values[index] = value
            left = step % 3
            segment = values[left:]
            k = step % len(segment)
            solver.kth_smallest(left, len(values), k)
            expected.append(sorted(segment)[k])
        self.assertEqual(solver.solve(), expected)

    def test_helper(self):
        values = [2, 7, 1, 8]
        zero_indexed = [
            (0, 5, 0, 4, 12),
            (2, 10, 1, 4, 18),
        ]
        self.assertEqual(
            dynamic_range_min_count_sum_at_least(values, zero_indexed),
            [2, 2],
        )
        one_indexed = [
            (1, 5, 1, 4, 12),
            (3, 10, 2, 4, 18),
        ]
        self.assertEqual(
            dynamic_range_min_count_sum_at_least(
                values, one_indexed, one_indexed=True
            ),
            [2, 2],
        )


if __name__ == "__main__":
    unittest.main()
