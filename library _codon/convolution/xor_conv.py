MOD = 998244353
def walsh_hadamard_tranform(a: list, inv: bool = False):
    i, n = 1, len(a)
    while i < n:
        for j in range(0, n, i << 1):
            for k in range(i):
                s, t = a[j + k], a[j + k + i]
                a[j + k], a[j + k + i] = (s + t) % MOD, (s - t) % MOD
        i <<= 1
    if inv:
        inv_n = pow(n, -1, MOD)
        for i in range(n):
            a[i] = (a[i] * inv_n) % MOD

def bitwise_xor_conv(a: list, b: list):
    n = len(a)
    assert n == len(b)
    walsh_hadamard_tranform(a, False)
    walsh_hadamard_tranform(b, False)
    for i in range(n):
        a[i] = (a[i] * b[i]) % MOD
    walsh_hadamard_tranform(a, True)