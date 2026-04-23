import array
import random

class ModFast:
    __slots__ = ('p', 'K', 'limit_frac', 'LOG', 'INV', 'POW_LO', 'POW_HI', 'FRAC_A', 'FRAC_B', 'root')
    def __init__(self, p, g = None):
        self.p = p
        self.K = 1 << 21
        self.limit_frac = 1 << 20
        
        self.LOG = array.array('I', [0] * (2 * self.K + 5))
        self.INV = array.array('I', [0] * (2 * self.K + 5))
        
        self.POW_LO = array.array('I', [0] * 32769)
        self.POW_HI = array.array('I', [0] * 32769)
        
        self.FRAC_A = array.array('H', [0] * (1 + self.limit_frac))
        self.FRAC_B = array.array('H', [0] * (1 + self.limit_frac))
        
        if g == None:
            if p == 998244353:
                self.root = 3
            elif p == 10**9 + 9:
                self.root = 13
            else:
                self.root = self._primitive_root(p)
        else:
            self.root = g
        
        self._build_pow()
        self._build_inv()
        self._build_log()
        self._build_frac()

    def _primitive_root(self, p):
        if p == 2: return 1
        m = p - 1
        factors = []
        d = 2
        temp = m
        while d * d <= temp:
            if temp % d == 0:
                factors.append(d)
                while temp % d == 0:
                    temp //= d
            d += 1
        if temp > 1:
            factors.append(temp)
        g = 2
        while True:
            ok = True
            for q in factors:
                if pow(g, m // q, p) == 1:
                    ok = False
                    break
            if ok:
                return g
            g += 1

    def _build_pow(self):
        root = self.root
        p = self.p
        LO = self.POW_LO
        HI = self.POW_HI
        
        LO[0] = 1
        HI[0] = 1
        
        curr = 1
        for i in range(32768):
            next_val = (curr * root) % p
            LO[i+1] = next_val
            curr = next_val
            
        root_pow_15 = LO[32768]
        curr = 1
        for i in range(32768):
            next_val = (curr * root_pow_15) % p
            HI[i+1] = next_val
            curr = next_val

    def _build_inv(self):
        p = self.p
        K = self.K
        INV = self.INV
        INV[K + 1] = 1
        for i in range(2, K + 1):
            if i >= p:
                INV[K + i] = INV[K + (i % p)]
            else:
                INV[K + i] = (p - (p // i)) * INV[K + (p % i)] % p
        for i in range(1, K + 1):
            INV[K - i] = p - INV[K + i]

    def _lpf_table(self, lim):
        lpf = array.array('I', range(lim + 1))
        primes = []
        for i in range(2, lim + 1):
            if lpf[i] == i:
                primes.append(i)
            for p in primes:
                if p > lpf[i] or i * p > lim:
                    break
                lpf[i * p] = p
        return lpf

    def _build_log(self):
        p = self.p
        K = self.K
        LIM = 1 << 21
        LOG = self.LOG
        LO = self.POW_LO
        HI = self.POW_HI
        
        lpf = self._lpf_table(LIM)
        
        S = 1 << 17
        mp = {}
        pw = 1
        r = self.root
        for k in range(S):
            mp[pw] = k
            pw = (pw * r) % p
            
        q_val = (LO[(p - 1 - S) & 32767] * HI[(p - 1 - S) >> 15]) % p
        
        def bsgs(s):
            ans = 0
            while True:
                if s in mp:
                    return ans + mp[s]
                ans += S
                s = (s * q_val) % p
        
        LOG[K + 1] = 0
        
        for i in range(2, LIM + 1):
            if i >= p:
                LOG[K + i] = LOG[K + (i % p)]
                continue
            if lpf[i] < i:
                LOG[K + i] = (LOG[K + lpf[i]] + LOG[K + (i // lpf[i])]) % (p - 1)
                continue
            if i < 100:
                LOG[K + i] = bsgs(i)
                continue
            if i * i > p:
                j = p // i
                k = p % i
                val = (LOG[K + k] + (p - 1) // 2 + (p - 1) - LOG[K + j]) % (p - 1)
                LOG[K + i] = val
                continue
            
            while True:
                k_rand = random.randint(0, p - 2)
                rk = (LO[k_rand & 32767] * HI[k_rand >> 15]) % p
                x = (i * rk) % p
                target_log = (p - 1 - k_rand)
                
                for q in [2, 3, 5, 7, 11, 13, 17, 19]:
                    while x % q == 0:
                        x //= q
                        target_log += LOG[K + q]
                
                if x >= LIM:
                    continue
                while i < x and x < LIM and lpf[x] < i:
                    lx = lpf[x]
                    x //= lx
                    target_log += LOG[K + lx]
                if 1 < x < i:
                    target_log += LOG[K + x]
                    x = 1
                if x == 1:
                    LOG[K + i] = target_log % (p - 1)
                    break
        
        half = (p - 1) // 2
        for i in range(1, LIM + 1):
            LOG[K - i] = (LOG[K + i] + half) % (p - 1)

    def _build_frac(self):
        stack = [(0, 1, 1, 1)]
        limit = 2048
        FA = self.FRAC_A
        FB = self.FRAC_B
        p = self.p
        
        while stack:
            a, b, c, d = stack.pop()
            if b + d < limit:
                stack.append((a, b, a + c, b + d))
                stack.append((a + c, b + d, c, d))
                continue
            
            s = (a * p) // (1024 * b)
            t = (c * p) // (1024 * d)
            
            if s >= len(FA): s = len(FA) - 1
            if t > len(FA): t = len(FA)
            
            if s < len(FA):
                FA[s] = a
                FB[s] = b
            if t < len(FA):
                FA[t] = c
                FB[t] = d
            
            if s + 1 < t:
                ma, mb = min(a, c), min(b, d)
                for i in range(s + 1, t):
                    FA[i] = ma
                    FB[i] = mb

    def pow(self, x, exp):
        if x == 0: return 1 if exp == 0 else 0
        if exp == 0: return 1
        shift = x >> 10
        a = self.FRAC_A[shift]
        b = self.FRAC_B[shift]
        t = x * b - a * self.p
        idx = (self.LOG[self.K + t] - self.LOG[self.K + b]) * exp % (self.p - 1)
        return (self.POW_LO[idx & 32767] * self.POW_HI[idx >> 15]) % self.p

    def pow_r(self, exp):
        exp %= (self.p - 1)
        if exp < 0: exp += (self.p - 1)
        return (self.POW_LO[exp & 32767] * self.POW_HI[exp >> 15]) % self.p

    def log_r(self, x):
        shift = x >> 10
        a = self.FRAC_A[shift]
        b = self.FRAC_B[shift]
        t = x * b - a * self.p
        return (self.LOG[self.K + t] - self.LOG[self.K + b]) % (self.p - 1)

    def inverse(self, x):
        shift = x >> 10
        b = self.FRAC_B[shift]
        t = x * b - self.FRAC_A[shift] * self.p
        return (self.INV[self.K + t] * b) % self.p