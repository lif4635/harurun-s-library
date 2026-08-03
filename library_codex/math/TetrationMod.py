"""巨大な累乗塔を法の下で計算する。"""

from library_codex.prime.Factorization import factor_count, euler_phi

def _pow_mod_with_bound(base, exponent, modulus):
    """Return base**exponent mod modulus and whether the exact value is < modulus."""
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    modular_result = 1 % modulus
    modular_base = base % modulus
    capped_result = 1
    capped_base = min(base, modulus)
    power = exponent
    while power:
        if power & 1:
            modular_result = modular_result * modular_base % modulus
            capped_result = min(modulus, capped_result * capped_base)
        power >>= 1
        if power:
            modular_base = modular_base * modular_base % modulus
            capped_base = min(modulus, capped_base * capped_base)
    return modular_result, capped_result < modulus

def tetration_mod(base, height, modulus):
    """base ↑↑ height modulo modulus; 0 ↑↑ height follows 0**0 == 1."""
    if base < 0 or height < 0 or modulus <= 0:
        raise ValueError("base/height must be nonnegative and modulus positive")
    if base == 0:
        value = 1 if height & 1 == 0 else 0
        return value % modulus
    if base == 1:
        return 1 % modulus
    frames = []
    current_height = height
    current_modulus = modulus
    while True:
        if current_modulus == 1:
            value, below = 0, False
            break
        if current_height == 0:
            value, below = 1 % current_modulus, 1 < current_modulus
            break
        if current_height == 1:
            value, below = base % current_modulus, base < current_modulus
            break
        next_modulus = euler_phi(current_modulus)
        frames.append((current_modulus, next_modulus))
        current_modulus = next_modulus
        current_height -= 1
    while frames:
        parent_modulus, exponent_modulus = frames.pop()
        exponent = value if below else value + exponent_modulus
        value, power_below = _pow_mod_with_bound(base, exponent, parent_modulus)
        below = below and power_below
    return value % modulus

