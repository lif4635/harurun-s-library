"""一次式の床和と合同条件を満たす整数の個数を高速に数える。"""

def floor_sum(n, modulus, multiplier, addend):
    """Sum floor((multiplier*i+addend)/modulus), 0 <= i < n.

    Unlike ACL's narrow interface, multiplier and addend may be negative.
    """
    if n < 0 or modulus <= 0:
        raise ValueError("requires n >= 0 and modulus > 0")
    quotient_a, multiplier = divmod(multiplier, modulus)
    quotient_b, addend = divmod(addend, modulus)
    answer = quotient_a * n * (n - 1) // 2 + quotient_b * n
    while True:
        if multiplier >= modulus:
            quotient, multiplier = divmod(multiplier, modulus)
            answer += quotient * n * (n - 1) // 2
        if addend >= modulus:
            quotient, addend = divmod(addend, modulus)
            answer += quotient * n
        maximum = multiplier * n + addend
        if maximum < modulus:
            return answer
        n, addend = divmod(maximum, modulus)
        multiplier, modulus = modulus, multiplier

def mod_affine_range_count(multiplier, addend, modulus, x_limit, y_limit):
    """Count x in [0,x_limit) with (multiplier*x+addend)%modulus<y_limit."""
    if not 0 <= y_limit <= modulus:
        raise ValueError("y_limit out of range")
    return (floor_sum(x_limit, modulus, multiplier, addend + modulus)
            - floor_sum(x_limit, modulus, multiplier,
                        addend + modulus - y_limit))

