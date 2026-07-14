from fractions import Fraction


class Surreal:
    __slots__ = ("value",)

    def __init__(self, numerator=0, denominator=1):
        self.value = (numerator if isinstance(numerator, Fraction)
                      else Fraction(numerator, denominator))

    def __eq__(self, other):
        return self.value == (other.value if isinstance(other, Surreal) else other)

    def __lt__(self, other):
        return self.value < (other.value if isinstance(other, Surreal) else other)

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    def __add__(self, other):
        return Surreal(self.value + (other.value if isinstance(other, Surreal)
                                     else other))

    __radd__ = __add__

    def __neg__(self):
        return Surreal(-self.value)

    def __sub__(self, other):
        return self + (-other if isinstance(other, Surreal) else -other)

    @staticmethod
    def between(left, right, include_left=False, include_right=False):
        left_value = None if left is None else left.value
        right_value = None if right is None else right.value
        if ((left_value is None or left_value < 0
             or include_left and left_value == 0)
                and (right_value is None or 0 < right_value
                     or include_right and right_value == 0)):
            return Surreal(0)
        sign = False
        if right_value is not None and right_value <= 0:
            sign = True
            left_value, right_value = (
                None if right_value is None else -right_value,
                None if left_value is None else -left_value,
            )
            include_left, include_right = include_right, include_left
        for exponent in range(65):
            denominator = 1 << exponent
            if left_value is None:
                numerator = -(1 << 127)
            else:
                scaled = left_value * denominator
                numerator = scaled.numerator // scaled.denominator
                if Fraction(numerator, 1) < scaled or not include_left:
                    numerator += 1
            candidate = Fraction(numerator, denominator)
            if (right_value is None or candidate < right_value
                    or include_right and candidate == right_value):
                return Surreal(-candidate if sign else candidate)
        raise OverflowError("no dyadic value found within 64 fractional bits")


class NumStar:
    __slots__ = ("number", "star")

    def __init__(self, number=0, star=0):
        self.number = number if isinstance(number, Surreal) else Surreal(number)
        self.star = star

    a = property(lambda self: self.number)
    b = property(lambda self: self.star)

    def __eq__(self, other):
        return self.number == other.number and self.star == other.star

    def __add__(self, other):
        return NumStar(self.number + other.number, self.star ^ other.star)

    __sub__ = __add__

    def __neg__(self):
        return NumStar(-self.number, self.star)

    @staticmethod
    def _mex(values):
        present = set(values)
        result = 0
        while result in present:
            result += 1
        return result

    @staticmethod
    def calculate(left_options, right_options):
        left_bound = max((value.number for value in left_options), default=None,
                         key=lambda value: value.value if value is not None else 0)
        right_bound = min((value.number for value in right_options), default=None,
                          key=lambda value: value.value if value is not None else 0)
        left_stars = [value.star for value in left_options
                      if left_bound is not None and value.number == left_bound]
        right_stars = [value.star for value in right_options
                       if right_bound is not None and value.number == right_bound]
        left_mex = NumStar._mex(left_stars)
        right_mex = NumStar._mex(right_stars)
        if (left_bound is None or right_bound is None
                or left_bound < right_bound):
            return NumStar(Surreal.between(
                left_bound, right_bound, left_mex == 0, right_mex == 0
            ), 0)
        if left_bound == right_bound and left_mex == right_mex:
            return NumStar(left_bound, left_mex)
        return None

    calc = calculate

    def outcome(self):
        if self.number > 0:
            return True, False
        if self.number < 0:
            return False, True
        if self.star == 0:
            return False, False
        return True, True


def solve_partizan_game(states, options):
    result = {}
    visiting = set()
    for initial in states:
        if initial in result:
            continue
        stack = [(initial, 0, None)]
        while stack:
            state, phase, cached = stack.pop()
            if state in result:
                continue
            if phase == 0:
                if state in visiting:
                    return {}
                visiting.add(state)
                left, right = options(state)
                left = list(left)
                right = list(right)
                stack.append((state, 1, (left, right)))
                for child in reversed(left + right):
                    if child in visiting and child not in result:
                        return {}
                    if child not in result:
                        stack.append((child, 0, None))
            else:
                left, right = cached
                if any(child not in result for child in left + right):
                    return {}
                value = NumStar.calculate(
                    [result[child] for child in left],
                    [result[child] for child in right],
                )
                if value is None:
                    return {}
                result[state] = value
                visiting.remove(state)
    return result


SolvePartizanGame = solve_partizan_game
