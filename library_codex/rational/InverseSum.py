"""逆数和を指定精度で数値計算する。"""

from library_codex.rational.Digamma import digamma

def inverse_sum(left, right):
    return digamma(right) - digamma(left)

