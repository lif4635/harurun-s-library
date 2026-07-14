import random

from library_codex.optimization.SlopeTrick import WeightedSlopeTrick


def evaluate_terms(terms, constant, point):
    result = constant
    for kind, breakpoint, count in terms:
        if kind == 1:
            result += max(0, point - breakpoint) * count
        else:
            result += max(0, breakpoint - point) * count
    return result


def test_weighted_slope_trick_random_hinges_shifts_and_eval():
    rng = random.Random(718934)
    for _ in range(300):
        slope = WeightedSlopeTrick()
        terms = []
        constant = 0
        for _ in range(100):
            kind = rng.randrange(5)
            if kind < 3:
                point = rng.randrange(-100, 101)
                count = rng.randrange(20)
                if kind == 0:
                    slope.add_x_minus_a(point, count)
                    terms.append((1, point, count))
                elif kind == 1:
                    slope.add_a_minus_x(point, count)
                    terms.append((-1, point, count))
                else:
                    slope.add_abs(point, count)
                    terms.append((1, point, count))
                    terms.append((-1, point, count))
            elif kind == 3:
                value = rng.randrange(-1000, 1001)
                slope.add_constant(value)
                constant += value
            else:
                amount = rng.randrange(-20, 21)
                slope.shift(amount)
                terms = [
                    (term_kind, breakpoint + amount, count)
                    for term_kind, breakpoint, count in terms
                ]
            for _ in range(3):
                point = rng.randrange(-200, 201)
                assert slope.evaluate(point) == evaluate_terms(
                    terms, constant, point
                )
            point, minimum = slope.get_min()
            assert evaluate_terms(terms, constant, point) == minimum
        candidates = [0] + [breakpoint for _, breakpoint, _ in terms]
        assert slope.get_min()[1] == min(
            evaluate_terms(terms, constant, point) for point in candidates
        )


def test_slope_trick_slide_chmin_and_merge():
    rng = random.Random(518973)
    for _ in range(500):
        base = WeightedSlopeTrick(rng.randrange(-100, 101))
        terms = []
        constant = base.minimum
        for _ in range(20):
            point = rng.randrange(-30, 31)
            count = rng.randrange(1, 10)
            if rng.randrange(2):
                base.add_x_minus_a(point, count)
                terms.append((1, point, count))
            else:
                base.add_a_minus_x(point, count)
                terms.append((-1, point, count))
        left = rng.randrange(-10, 1)
        right = rng.randrange(0, 11)
        slid = WeightedSlopeTrick()
        for kind, point, count in terms:
            if kind == 1:
                slid.add_x_minus_a(point, count)
            else:
                slid.add_a_minus_x(point, count)
        slid.add_constant(constant)
        slid.slide(left, right)
        for point in range(-50, 51):
            expected = min(
                evaluate_terms(terms, constant, value)
                for value in range(point - right, point - left + 1)
            )
            assert slid.evaluate(point) == expected
        right_min = WeightedSlopeTrick()
        left_min = WeightedSlopeTrick()
        for kind, point, count in terms:
            target = right_min.add_x_minus_a if kind == 1 else right_min.add_a_minus_x
            target(point, count)
            target = left_min.add_x_minus_a if kind == 1 else left_min.add_a_minus_x
            target(point, count)
        right_min.add_constant(constant)
        left_min.add_constant(constant)
        right_min.chmin_right()
        left_min.chmin_left()
        for point in range(-50, 51):
            assert right_min.evaluate(point) == min(
                evaluate_terms(terms, constant, value)
                for value in range(-100, point + 1)
            )
            assert left_min.evaluate(point) == min(
                evaluate_terms(terms, constant, value)
                for value in range(point, 101)
            )
    first = WeightedSlopeTrick(7)
    second = WeightedSlopeTrick(-3)
    first.add_abs(-5, 4)
    second.add_abs(8, 6)
    expected = [first.evaluate(point) + second.evaluate(point) for point in range(-30, 31)]
    first.merge(second)
    assert [first.evaluate(point) for point in range(-30, 31)] == expected
