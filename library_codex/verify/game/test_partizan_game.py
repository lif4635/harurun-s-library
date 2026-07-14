from fractions import Fraction

from library_codex.game.PartizanGame import NumStar, Surreal, solve_partizan_game


def test_numstar_canonical_values_and_solver():
    zero = NumStar.calculate([], [])
    one = NumStar.calculate([zero], [])
    minus_one = NumStar.calculate([], [zero])
    star = NumStar.calculate([zero], [zero])
    half = NumStar.calculate([zero], [one])
    assert zero == NumStar(0, 0)
    assert one == NumStar(1, 0)
    assert minus_one == NumStar(-1, 0)
    assert star == NumStar(0, 1)
    assert half.number.value == Fraction(1, 2)
    assert star.outcome() == (True, True)

    options = {
        "0": ([], []),
        "1": (["0"], []),
        "-1": ([], ["0"]),
        "*": (["0"], ["0"]),
        "1/2": (["0"], ["1"]),
    }
    result = solve_partizan_game(options, options.__getitem__)
    assert result["1/2"].number.value == Fraction(1, 2)
    assert solve_partizan_game([0], lambda state: ([state], [])) == {}


def test_surreal_between_open_and_closed_bounds():
    assert Surreal.between(Surreal(0), Surreal(1)).value == Fraction(1, 2)
    assert Surreal.between(Surreal(0), Surreal(1), True).value == 0
    assert Surreal.between(Surreal(-1), Surreal(0), False, False).value == Fraction(-1, 2)

