"""整数入力に対する対数値を小さな表で近似して高速に返す。"""

import math

class LogTable:
    __slots__ = ("values", "mask")

    def __init__(self, bits=16, seed=88172645463325252):
        size = 1 << bits
        self.mask = size - 1
        values = [0.0] * size
        value = seed & ((1 << 64) - 1)
        log_max = math.log(2.0) * 64
        for index in range(size):
            value ^= value << 7 & ((1 << 64) - 1)
            value ^= value >> 9
            values[index] = math.log(max(1, value)) - log_max
        self.values = values

    def __call__(self, index):
        return self.values[index & self.mask]

