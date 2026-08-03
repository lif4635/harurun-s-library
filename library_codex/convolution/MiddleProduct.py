"""多項式積の中央の必要な係数だけを計算する。"""

from library_codex.convolution.NTT import convolution, get_ntt, primitive_root

DEFAULT_MOD = 998244353

def middle_product(first, second, start, count, mod=DEFAULT_MOD):
    """A requested coefficient window of the ordinary convolution."""
    if count <= 0:
        return []
    product = convolution(first, second, mod)
    return [product[i] if 0 <= i < len(product) else 0
            for i in range(start, start + count)]

