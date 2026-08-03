"""digamma関数を数値的に評価する。"""

import math

def digamma(value):
    result = 0.0
    while value < 50.0:
        result -= 1.0 / value
        value += 1.0
    inverse = 1.0 / value
    square = inverse * inverse
    fourth = square * square
    return (result + math.log(value) - 0.5 * inverse - square / 12.0
            + fourth / 120.0 - fourth * square / 252.0)

