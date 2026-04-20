def sa_is(s, upper):
    n = len(s)
    if n == 0: return []
    if n == 1: return [0]
    if n == 2: return [0, 1] if s[0] < s[1] else [1, 0]
    sa = [-1] * n
    ls = [0] * n
    for i in range(n - 2, -1, -1):
        ls[i] = ls[i + 1] if s[i] == s[i + 1] else (s[i] < s[i + 1])
    sum_l, sum_s = [0] * (upper + 1), [0] * (upper + 1)
    for i in range(n):
        if ls[i]: sum_l[s[i] + 1] += 1
        else: sum_s[s[i]] += 1
    for i in range(upper + 1):
        sum_s[i] += sum_l[i]
        if i < upper: sum_l[i + 1] += sum_s[i]

    def induce(lms):
        sa[:] = [-1] * n
        buf = list(sum_s)
        for d in lms:
            if d == n: continue
            sa[buf[s[d]]] = d
            buf[s[d]] += 1
        buf = list(sum_l)
        sa[buf[s[n - 1]]] = n - 1
        buf[s[n - 1]] += 1
        for i in range(n):
            v = sa[i]
            if v >= 1 and not ls[v - 1]:
                b = buf[s[v - 1]]
                sa[b] = v - 1
                buf[s[v - 1]] = b + 1
        buf = list(sum_l)
        for i in range(n - 1, -1, -1):
            v = sa[i]
            if v >= 1 and ls[v - 1]:
                b = buf[s[v - 1] + 1] - 1
                buf[s[v - 1] + 1] = b
                sa[b] = v - 1

    lms_map = [-1] * (n + 1)
    m = 0
    for i in range(1, n):
        if not ls[i - 1] and ls[i]:
            lms_map[i] = m
            m += 1
    lms = [i for i in range(1, n) if not ls[i - 1] and ls[i]]
    induce(lms)
    
    if m:
        sorted_lms = [v for v in sa if lms_map[v] != -1]
        rec_s, rec_upper = [0] * m, 0
        rec_s[lms_map[sorted_lms[0]]] = 0
        for i in range(1, m):
            l, r = sorted_lms[i - 1], sorted_lms[i]
            end_l = lms[lms_map[l] + 1] if lms_map[l] + 1 < m else n
            end_r = lms[lms_map[r] + 1] if lms_map[r] + 1 < m else n
            same = (end_l - l == end_r - r)
            if same:
                while l < end_l:
                    if s[l] != s[r]: break
                    l += 1; r += 1
                if l == n or s[l] != s[r]: same = False
            if not same: rec_upper += 1
            rec_s[lms_map[sorted_lms[i]]] = rec_upper
        rec_sa = sa_is(rec_s, rec_upper)
        for i in range(m): sorted_lms[i] = lms[rec_sa[i]]
        induce(sorted_lms)
    return sa

def suffix_array(s):
    n = len(s)
    if type(s) is str: return sa_is([ord(i) for i in s], 255)
    idx = sorted(range(n), key=s.__getitem__)
    s2, now = [0] * n, 0
    for i in range(n):
        if i and s[idx[i - 1]] != s[idx[i]]: now += 1
        s2[idx[i]] = now
    return sa_is(s2, now)

def lcp_array(s, sa):
    n = len(s)
    if n == 0: return []
    rnk = [0] * n
    for i in range(n): rnk[sa[i]] = i
    lcp, h = [0] * (n - 1), 0
    for i in range(n):
        if h > 0: h -= 1
        if rnk[i] == 0: continue
        j = sa[rnk[i] - 1]
        while j + h < n and i + h < n and s[j + h] == s[i + h]: h += 1
        lcp[rnk[i] - 1] = h
    return lcp

class StaticStringBase:
    def __init__(self, S):
        self.S = S
        self.size = len(S)
        self.SA = suffix_array(S)
        self.RSA = [0] * self.size
        for i, sa_i in enumerate(self.SA): self.RSA[sa_i] = i
        self.LCP = lcp_array(S, self.SA)
        n = len(self.LCP)
        self.lcp_len = n
        if n > 0:
            max_k = n.bit_length()
            self.rmq_st = [0] * (max_k * n)
            self.rmq_st[:n] = self.LCP
            st = self.rmq_st
            for k in range(1, max_k):
                step = 1 << (k - 1)
                curr, prev = k * n, (k - 1) * n
                lim = n - (1 << k) + 1
                st[curr : curr + lim] = [a if a < b else b for a, b in zip(st[prev : prev + lim], st[prev + step : prev + step + lim])]
        else:
            self.rmq_st = []

class StaticString:
    __slots__ = ['base', 'l', 'r']
    def __init__(self, base, l, r):
        self.base, self.l, self.r = base, l, r

    @classmethod
    def from_string(cls, S):
        return cls(StaticStringBase(S), 0, len(S))

    def __getitem__(self, idx):
        cls = type(idx)
        if cls is slice:
            start, stop, _ = idx.indices(self.r - self.l)
            return StaticString(self.base, self.l + start, self.l + stop)
        elif cls is tuple:
            parts = []
            base, offset, size = self.base, self.l, self.r - self.l
            for i in idx:
                if type(i) is slice:
                    start, stop, _ = i.indices(size)
                    if start < stop:
                        parts.append(StaticString(base, offset + start, offset + stop))
                else:
                    v = i if i >= 0 else i + size
                    parts.append(StaticString(base, offset + v, offset + v + 1))
            return MergedStaticString(parts)
        return self.base.S[self.l + idx]

    def __str__(self): return self.base.S[self.l:self.r]
    def __len__(self): return self.r - self.l

    def __add__(self, other):
        return MergedStaticString([self, other])

    def lcp(self, other):
        bl, br = self.base.RSA[self.l], self.base.RSA[other.l]
        if bl > br: bl, br = br, bl
        sl, ol = self.r - self.l, other.r - other.l
        min_l = sl if sl < ol else ol
        if bl == br: return min_l
        
        k_idx = (br - bl).bit_length() - 1
        curr = k_idx * self.base.lcp_len
        v1, v2 = self.base.rmq_st[curr + bl], self.base.rmq_st[curr + br - (1 << k_idx)]
        rmq_v = v1 if v1 < v2 else v2
        return min_l if min_l < rmq_v else rmq_v

class MergedStaticString:
    __slots__ = ['S', 'lencum']
    def __init__(self, parts=None):
        if parts:
            self.S = [p for p in parts if (p.r - p.l) > 0]
            self.lencum = []
            cur = 0
            for p in self.S:
                cur += p.r - p.l
                self.lencum.append(cur)
        else:
            self.S, self.lencum = [], []

    def __iadd__(self, T):
        if (T.r - T.l) == 0: return self
        self.S.append(T)
        self.lencum.append((self.lencum[-1] if self.lencum else 0) + (T.r - T.l))
        return self

    def __add__(self, T):
        res = MergedStaticString(self.S)
        res += T
        return res

    def __len__(self): return self.lencum[-1] if self.lencum else 0

    def __getitem__(self, idx):
        if type(idx) is slice:
            res = MergedStaticString()
            start, stop, _ = idx.indices(len(self))
            tmp = 0
            for i in range(len(self.S)):
                next_tmp = self.lencum[i]
                if tmp < start:
                    if stop < next_tmp: res += self.S[i][(start - tmp):(stop - tmp)]
                    elif start < next_tmp: res += self.S[i][(start - tmp):]
                elif next_tmp <= stop:
                    res += self.S[i]
                elif tmp < stop:
                    res += self.S[i][0:(stop - tmp)]
                tmp = next_tmp
            return res
        else:
            if idx < 0: idx += len(self)
            for i in range(len(self.lencum)):
                if idx < self.lencum[i]:
                    part = self.S[i]
                    return part.base.S[part.l + idx - (self.lencum[i-1] if i > 0 else 0)]
            return ""

    def lcp(self, other):
        if not self.S or not other.S: return 0
        s, t = self.S[0], other.S[0]
        si, ti, res = 0, 0, 0
        len_S, len_other_S = len(self.S), len(other.S)
        
        while True:
            bl, br = s.base.RSA[s.l], t.base.RSA[t.l]
            if bl > br: bl, br = br, bl
            sl, tl = s.r - s.l, t.r - t.l
            min_l = sl if sl < tl else tl
            
            if bl == br:
                tmp = min_l
            else:
                k_idx = (br - bl).bit_length() - 1
                curr = k_idx * s.base.lcp_len
                v1, v2 = s.base.rmq_st[curr + bl], s.base.rmq_st[curr + br - (1 << k_idx)]
                rmq_v = v1 if v1 < v2 else v2
                tmp = min_l if min_l < rmq_v else rmq_v

            res += tmp
            
            if tmp == sl and tmp == tl:
                si += 1; ti += 1
                if si == len_S or ti == len_other_S: return res
                s, t = self.S[si], other.S[ti]
            elif tmp == sl:
                si += 1
                if si == len_S: return res
                s = self.S[si]
                t = StaticString(t.base, t.l + tmp, t.r)
            elif tmp == tl:
                ti += 1
                if ti == len_other_S: return res
                s = StaticString(s.base, s.l + tmp, s.r)
                t = other.S[ti]
            else:
                return res

    def __lt__(self, other):
        v_lcp = self.lcp(other)
        sl, ol = len(self), len(other)
        if min(sl, ol) == v_lcp: return sl < ol
        return self[v_lcp] < other[v_lcp]

    def __str__(self): return "".join(str(p) for p in self.S)

def to_static_strings(strings):
    tmp = "$".join(strings) + "$"
    base = StaticStringBase(tmp)
    res, now = [], 0
    for s in strings:
        res.append(StaticString(base, now, now + len(s)))
        now += len(s) + 1
    return res