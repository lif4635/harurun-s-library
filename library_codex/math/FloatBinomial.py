"""浮動小数点数で二項係数を逐次計算する。"""

import math

class FloatBinomial:
    __slots__ = ("log_factorial",)
    LOG_ZERO = -1e100

    def __init__(self, maximum):
        self.log_factorial = [0.0] * (maximum + 1)
        for index in range(1, maximum + 1):
            self.log_factorial[index] = self.log_factorial[index - 1] + math.log(index)

    def logfac(self, number):
        return self.log_factorial[number]

    def logfinv(self, number):
        return -self.log_factorial[number]

    def logC(self, number, chosen):
        if chosen < 0 or number < chosen:
            return self.LOG_ZERO
        return (self.log_factorial[number] - self.log_factorial[chosen]
                - self.log_factorial[number - chosen])

    def logP(self, number, chosen):
        if chosen < 0 or number < chosen:
            return self.LOG_ZERO
        return self.log_factorial[number] - self.log_factorial[number - chosen]

