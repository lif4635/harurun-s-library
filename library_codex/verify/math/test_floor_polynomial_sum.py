from library_codex.math.FloorPolynomialSum import floor_polynomial_sums


def test_floor_polynomial_sums_against_direct_evaluation():
    for n in range(1, 25):
        for modulus in range(1, 12):
            for multiplier in range(-12, 13):
                for addend in range(-12, 13, 4):
                    actual = floor_polynomial_sums(
                        n, modulus, multiplier, addend, 3, 3
                    )
                    for x_power in range(4):
                        for y_power in range(4):
                            expected = sum(
                                index ** x_power
                                * ((multiplier * index + addend) // modulus) ** y_power
                                for index in range(n)
                            )
                            assert actual[x_power][y_power] == expected

