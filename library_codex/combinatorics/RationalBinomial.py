"""有理数として二項係数を正確に計算する。"""

import math

from fractions import Fraction

class RationalBinomial:
    def fac(self, number):
        return Fraction(math.factorial(number)) if number >= 0 else Fraction(0)

    def finv(self, number):
        return 1 / self.fac(number) if number >= 0 else Fraction(0)

    def inv(self, number):
        return Fraction(1, number) if number else Fraction(1)

    def C(self, number, chosen):
        return Fraction(math.comb(number, chosen)) if 0 <= chosen <= number else Fraction(0)

    def P(self, number, chosen):
        return Fraction(math.perm(number, chosen)) if 0 <= chosen <= number else Fraction(0)

    def H(self, number, chosen):
        if number < 0 or chosen < 0:
            return Fraction(0)
        return Fraction(1) if chosen == 0 else self.C(number + chosen - 1, chosen)

    def multinomial(self, groups):
        if any(group < 0 for group in groups):
            return Fraction(0)
        total = sum(groups)
        result = math.factorial(total)
        for group in groups:
            result //= math.factorial(group)
        return Fraction(result)

    __call__ = C

