# https://github.com/atcoder/ac-library/blob/master/atcoder/convolution.hpp
from array import array
MOD = 998244353
IMAG = 911660635
IIMAG = 86583718
INV2 = 499122177
rate2 = array('I', [0, 911660635, 509520358, 369330050, 332049552, 983190778, 123842337, 238493703, 975955924, 603855026, 856644456, 131300601, 842657263, 730768835, 942482514, 806263778, 151565301, 510815449, 503497456, 743006876, 741047443, 56250497, 867605899, 0])
irate2 = array('I', [0, 86583718, 372528824, 373294451, 645684063, 112220581, 692852209, 155456985, 797128860, 90816748, 860285882, 927414960, 354738543, 109331171, 293255632, 535113200, 308540755, 121186627, 608385704, 438932459, 359477183, 824071951, 103369235, 0])
rate3 = array('I', [0, 372528824, 337190230, 454590761, 816400692, 578227951, 180142363, 83780245, 6597683, 70046822, 623238099, 183021267, 402682409, 631680428, 344509872, 689220186, 365017329, 774342554, 729444058, 102986190, 128751033, 395565204, 0])
irate3 = array('I', [0, 509520358, 929031873, 170256584, 839780419, 282974284, 395914482, 444904435, 72135471, 638914820, 66769500, 771127074, 985925487, 262319669, 262341272, 625870173, 768022760, 859816005, 914661783, 430819711, 272774365, 530924681, 0])

# https://judge.yosupo.jp/submission/55648
def butterfly(a: list):
    n = len(a)
    h = (n - 1).bit_length()
    le = 0
    while le < h:
        if h - le == 1:
            p = 1 << (h - le - 1)
            rot = 1
            for s in range(1 << le):
                offset = s << (h - le)
                for i in range(p):
                    l = a[i + offset]
                    r = a[i + offset + p] * rot
                    a[i + offset] = (l + r) % MOD
                    a[i + offset + p] = (l - r) % MOD
                rot *= rate2[(~s & -~s).bit_length()]
                rot %= MOD
            le += 1
        else:
            p = 1 << (h - le - 2)
            rot = 1
            for s in range(1 << le):
                rot2 = rot * rot % MOD
                rot3 = rot2 * rot % MOD
                offset = s << (h - le)
                for i in range(p):
                    a0 = a[i + offset]
                    a1 = a[i + offset + p] * rot
                    a2 = a[i + offset + p * 2] * rot2
                    a3 = a[i + offset + p * 3] * rot3
                    a1na3imag = (a1 - a3) % MOD * IMAG
                    a[i + offset] = (a0 + a2 + a1 + a3) % MOD
                    a[i + offset + p] = (a0 + a2 - a1 - a3) % MOD
                    a[i + offset + p * 2] = (a0 - a2 + a1na3imag) % MOD
                    a[i + offset + p * 3] = (a0 - a2 - a1na3imag) % MOD
                rot *= rate3[(~s & -~s).bit_length()]
                rot %= MOD
            le += 2

def butterfly_inv(a: list):
    n = len(a)
    h = (n - 1).bit_length()
    le = h
    while le:
        if le == 1:
            p = 1 << (h - le)
            irot = 1
            for s in range(1 << (le - 1)):
                offset = s << (h - le + 1)
                for i in range(p):
                    l = a[i + offset]
                    r = a[i + offset + p]
                    a[i + offset] = (l + r) % MOD
                    a[i + offset + p] = (l - r) * irot % MOD
                irot *= irate2[(~s & -~s).bit_length()]
                irot %= MOD
            le -= 1
        else:
            p = 1 << (h - le)
            irot = 1
            for s in range(1 << (le - 2)):
                irot2 = irot * irot % MOD
                irot3 = irot2 * irot % MOD
                offset = s << (h - le + 2)
                for i in range(p):
                    a0 = a[i + offset]
                    a1 = a[i + offset + p]
                    a2 = a[i + offset + p * 2]
                    a3 = a[i + offset + p * 3]
                    a2na3iimag = (a2 - a3) * IIMAG % MOD
                    a[i + offset] = (a0 + a1 + a2 + a3) % MOD
                    a[i + offset + p] = (a0 - a1 + a2na3iimag) * irot % MOD
                    a[i + offset + p * 2] = (a0 + a1 - a2 - a3) * irot2 % MOD
                    a[i + offset + p * 3] = (a0 - a1 - a2na3iimag) * irot3 % MOD
                irot *= irate3[(~s & -~s).bit_length()]
                irot %= MOD
            le -= 2

def intt(a):
    if len(a) <= 1: return
    butterfly_inv(a)
    iv = pow(len(a), MOD - 2, MOD)
    for i, x in enumerate(a): a[i] = x * iv % MOD

def multiply(s: list, t: list):
    n = len(s)
    m = len(t)
    if min(n, m) <= 60:
        a = [0] * (n + m - 1)
        for i in range(n):
            if i&0b111 == 0:        
                for j in range(m):
                    a[i + j] += s[i] * t[j]
                    a[i + j] %= MOD
            else:
                for j in range(m):
                    a[i + j] += s[i] * t[j]
        return [x % MOD for x in a]
    a = s.copy()
    b = t.copy()
    z = 1 << (n + m - 2).bit_length()
    a += [0] * (z - n)
    b += [0] * (z - m)
    butterfly(a)
    butterfly(b)
    for i in range(z):
        a[i] *= b[i]
        a[i] %= MOD
    butterfly_inv(a)
    a = a[:n + m - 1]
    iz = pow(z, MOD - 2, MOD)
    return [v * iz % MOD for v in a]

def pow2(s: list):
    n = len(s)
    l = (n << 1) - 1
    if n <= 60:
        a = [0] * l
        for i, x in enumerate(s):
            for j, y in enumerate(s):
                a[i + j] += x * y
        return [x % MOD for x in a]
    z = 1 << (l - 1).bit_length()
    a = s + [0] * (z - n)
    butterfly(a)
    for i, x in enumerate(a): a[i] = x * x % MOD
    butterfly_inv(a)
    a[l:] = []
    iz = pow(z, MOD - 2, MOD)
    return [x * iz % MOD for x in a]

def shrink(a: list):
    while a and not a[-1]: a.pop()

def fps_add(a: list, b: list):
    if len(a) < len(b):
        res = b.copy()
        for i, x in enumerate(a):
            res[i] += x
    else:
        res = a.copy()
        for i, x in enumerate(b):
            res[i] += x
    return [x-MOD if MOD <= x else x in res]

def fps_sub(a: list, b: list):
    if len(a) < len(b):
        res = b.copy()
        for i, x in enumerate(a):
            res[i] -= x
        return [MOD-x if 0 < x else -x in res]
    else:
        res = a.copy()
        for i, x in enumerate(b):
            res[i] -= x
        return [x if 0 <= x else x+MOD in res]

def fps_neg(a: list):
    return [MOD-x if x else 0 for x in a]

def fps_div(a: list, b: list) -> list:
    if len(a) < len(b): return []
    n = len(a) - len(b) + 1
    cnt = 0
    if len(b) > 64:
        return multiply(a[::-1][:n], fps_inv(b[::-1], n))[:n][::-1]
    f = a.copy()
    g = b.copy()
    while g and not g[-1]:
        g.pop()
        cnt += 1
    coef = pow(g[-1], MOD - 2, MOD)
    g = [x * coef % MOD for x in g]
    deg = len(f) - len(g) + 1
    lg = len(g)
    res = [0] * deg
    for i in reversed(range(deg)):
        res[i] = x = f[i + lg - 1] % MOD
        for j, y in enumerate(g):
            f[i + j] -= x * y
    return [x * codf  % MOD for x in res] + [0] * cnt

def fps_mod(a: list, b: list) -> list:
    res = fps_sub(a, multiply(fps_div(a, b),  b))
    while res and not res[-1]: res.pop()
    return res

def fps_divmod(a: list, b: list):
    q = fps_div(a, b)
    r = fps_sub(a, multiply(q, b))
    while r and not r[-1]: r.pop()
    return q, r

def fps_eval(a: list, x: int) -> int:
    r = 0
    w = 1
    for v in a:
        r += w * v % MOD
        w = w * x % MOD
    return r % MOD

def fps_inv(a: list, deg: int=-1):
    # assert(self[0] != 0)
    if deg == -1: deg = len(a)
    res = [0] * deg
    res[0] = pow(a[0], MOD - 2, MOD)
    d = 1
    iv = INV2
    while d < deg:
        d2 = d << 1
        f = [0] * d2
        fl = min(len(a), d2)
        f[:fl] = a[:fl]
        g = [0] * d2
        g[:d] = res[:d]
        butterfly(g)
        butterfly(f)
        for i in range(d2): f[i] = f[i] * g[i] % MOD
        butterfly_inv(f)
        f[:d] = [0] * d
        for i in range(d, d2): f[i] = f[i] * iv % MOD
        butterfly(f)
        for i in range(d2): f[i] = f[i] * g[i] % MOD
        butterfly_inv(f)
        for i in range(d, min(d2, deg)): res[i] = (MOD-f[i]) * iv % MOD
        d <<= 1
        iv = iv * INV2 % MOD
    return res

def fps_pow(a: list, k: int, deg=-1) -> list:
    n = len(a)
    if deg == -1: deg = n
    if k == 0:
        if not deg: return []
        res = [0] * deg
        res[0] = 1
        return res
    for i, x in enumerate(a):
        if x:
            iz = pow(x, MOD - 2, MOD)
            res = [x * iz % MOD for x in a[i:]]
            res = fps_log(res, deg)
            res = [x * k % MOD for x in res]
            res = fps_exp(res, deg)
            coef = pow(x, k, MOD)
            res = [0] * (i * k) + [x * coef % MOD for x in res]
            if len(res) < deg:
                return res + [0] * (deg - len(res))
            return res[:deg]
        if (i + 1) * k >= deg: break
    return [0] * deg

def fps_exp(a: list, deg: int=-1):
    # assert a[0] == 0
    if deg == -1: deg = len(a)
    inv = [0, 1]
    def inplace_integral(f: list) -> list:
        n = len(f)
        while len(inv) <= n:
            j, k = divmod(MOD, len(inv))
            inv.append((-inv[k] * j) % MOD)
        return [0] + [x * inv[i + 1] % MOD for i, x in enumerate(f)]

    b = [1, (a[1] if 1 < len(a) else 0)]
    c = [1]
    z1 = []
    z2 = [1, 1]
    m = 2
    while m < deg:
        y = b + [0] * m
        butterfly(y)
        z1 = z2
        z = [y[i] * p % MOD for i, p in enumerate(z1)]
        intt(z)
        z[:m >> 1] = [0] * (m >> 1)
        butterfly(z)
        for i, p in enumerate(z1): z[i] = z[i] * (-p) % MOD
        intt(z)
        c[m >> 1:] = z[m >> 1:]
        z2 = c + [0] * m
        butterfly(z2)
        tmp = min(len(a), m)
        x = a[:tmp] + [0] * (m - tmp)
        x = fps_diff(x)
        x.append(0)
        butterfly(x)
        for i, p in enumerate(x): x[i] = y[i] * p % MOD
        intt(x)
        for i, p in enumerate(b):
            if not i: continue
            x[i - 1] -= p * i % MOD
        x += [0] * m
        for i in range(m - 1): x[m + i], x[i] = x[i], 0
        butterfly(x)
        for i, p in enumerate(z2): x[i] = x[i] * p % MOD
        intt(x)
        x.pop()
        x = inplace_integral(x)
        x[:m] = [0] * m
        for i in range(m, min(len(a), m << 1)): x[i] += a[i]
        butterfly(x)
        for i, p in enumerate(y): x[i] = x[i] * p % MOD
        intt(x)
        b[m:] = x[m:]
        m <<= 1
    return b[:deg]

def fps_log(a: list, deg=-1) -> list:
    # assert(a[0] == 1)
    if deg == -1: deg = len(a)
    return fps_integral(multiply(fps_diff(a), fps_inv(a, deg))[:deg - 1])

def fps_integral(a: list):
    n = len(a)
    res = [0] * (n + 1)
    if n: res[1] = 1
    for i in range(2, n + 1):
        j, k = divmod(MOD, i)
        res[i] = (-res[k] * j) % MOD
    for i, x in enumerate(a): res[i + 1] = res[i + 1] * x % MOD
    return res

def fps_diff(a: list):
    return [i * x % MOD for i, x in enumerate(a) if i]

def LinearRecurrence(n: int, p: list, q: list):
    """
    [x^n]P(x)/Q(x)
    """
    # assert len(p) < len(q)
    shrink(q)
    while n:
        q2 = q[:]
        for i in range(1,len(q2),2): q2[i] = (-q2[i])%MOD
        s = multiply(p,q2)
        t = multiply(q,q2)
        for i in range(n&1,len(s),2): p[i>>1] = s[i]
        for i in range(0,len(t),2): q[i>>1] = t[i]
        n >>= 1
    return p[0] * pow(q[0], -1, MOD) % MOD

def fps_compsite(f: list, g: list):
    """
    g(f(x)) mod x^(n+1)
    """
    # assert len(f) == len(g)
    def trans_multiply(s, t):
        n = len(s)
        m = len(t)
        l = 1 << (max(n, m) - 1).bit_length()
        a = s + [0] * (l - n)
        b = t + [0] * (l - m)
        a = [a[0]] + [a[l - i] for i in range(1, l)]
        butterfly(a)
        butterfly(b)
        iz = pow(l, MOD-2, MOD)
        for i, x in enumerate(b):
            a[i] = a[i] * x % MOD * iz % MOD
        butterfly_inv(a)
        a = [a[0]] + [a[l - i] for i in range(1, l)]
        return a[:n - m + 1]
    
    n = len(f)
    l = 1 << (n - 1).bit_length()
    a = [MOD - x for x in f] + [0] * (2 * l - n)
    b = g + [0] * (l - n) 
    
    def _inner(q, n, k):
        if n == 1:
            p = [0] * (2 * k)
            p[0::2] = b[::-1]
            return p
        siz = 2 * n * k
        r = [MOD - x if i & 1 else x for i,x in enumerate(q)]
        qq = multiply(q, r)
        qq.append(0)
        for i in range(0, siz, 2):
            qq[siz+i] = (qq[siz+i] + 2 * q[i]) % MOD
        nq = [0] * siz
        for j in range(2 * k):
            for i in range(n >> 1):
                nq[n * j + i] = qq[2 * n * j + 2 * i]
        np = _inner(nq, n >> 1, k << 1)
        
        pq = [0] * (2 * siz)
        for j in range(2 * k):
            for i in range(n >> 1):
                pq[2 * n * j + 2 * i + 1] = np[n * j + i]
        
        p = [pq[siz + i] for i in range(siz)]
        pq.pop()
        x = trans_multiply(pq, r)
        p = [(p[i] + x[i]) % MOD for i in range(siz)]
        return p
    
    p = _inner(a, l, 1)
    p = p[l-1::-1]
    return p[:n]

def MultisetSum(a: list, lim: int=-1) -> list:
    """
    #{ b | sum(b) == k, b \subset a}
    """
    if lim == -1: lim = sum(a)
    d = [0] * (lim+1)
    for x in a:
        if x <= lim: d[x] += 1
    inv = [1,1]
    for i in range(len(inv), lim+1):
        inv.append(-inv[MOD%i] * (inv//i) % MOD)
    res = [0] * (lim+1)
    for i in range(1, lim+1):
        if d[i]:
            tmp = d[i] * i
            for j in range(i, lim+1, i):
                res[j] += tmp * inv[j] % MOD
    res = fps_exp(res, lim+1)
    return res

def _fft2d(s: list[list]):
    h, w = len(s),len(s[0])
    for i in range(h):
        ntt(s[i])
    buf = [0] * h
    for j in range(w):
        buf = [s[i][j] for i in range(h)]
        ntt(buf)
        for i in range(h):
            s[i][j] = buf[i]

def _ifft2d(s: list[list]):
    h, w = len(s),len(s[0])
    for i in range(h):
        intt(s[i])
    buf = [0] * h
    for j in range(w):
        buf = [s[i][j] for i in range(h)]
        intt(buf)
        for i in range(h):
            s[i][j] = buf[i]

def multiply_2D(s: list[list], t: list[list]):
    """
    not verify
    """
    from copy import deepcopy
    hs, ws = len(s), len(s[0])
    ht, wt = len(t), len(t[0])
    h = 1 << (hs + ht - 2).bit_length()
    w = 1 << (ws + wt - 2).bit_length()
    a = deepcopy(s)
    b = deepcopy(t)
    for i in range(hs):
        a[i] += [0] * (w - ws)
    for i in range(ht):
        b[i] += [0] * (w - wt)
    a += [[0]*w for i in range(h - hs)]
    b += [[0]*w for i in range(h - ht)]
    _fft2d(a)
    _fft2d(b)
    for i in range(h):
        for j in range(w):
            a[i][j] *= b[i][j]
            a[i][j] %= MOD
    _ifft2d(a)
    a = a[:hs + ht - 1]
    for i in range(hs + ht - 1):
        a[i][ws + wt - 1:] = []
    return a