"""一次式の剰余の最小値を、連続した整数範囲で求める。"""


def min_mod(n, modulus, multiplier, addend):
    """0<=i<nにおける(multiplier*i+addend)%modulusの最小値。O(log modulus)。"""
    if n <= 0 or modulus <= 0:
        raise ValueError("requires n > 0 and modulus > 0")
    multiplier %= modulus
    addend %= modulus
    answer = addend
    while True:
        if multiplier * 2 > modulus:
            addend = (addend + multiplier * (n - 1)) % modulus
            multiplier = modulus - multiplier
        if addend < answer:
            answer = addend
        if answer == 0:
            return 0
        count = (multiplier * (n - 1) + addend) // modulus
        if count == 0:
            return answer
        addend = (addend - modulus) % multiplier
        n, modulus, multiplier = count, multiplier, -modulus % multiplier
