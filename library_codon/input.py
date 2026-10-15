import sys
II = lambda : int(input())
LI = lambda : [int(a) for a in input().split()]
SI = lambda : input().rstrip()
LLI = lambda n : [[int(a) for a in input().split()] for _ in range(n)]
LSI = lambda n : [input().rstrip() for _ in range(n)]
LI_1 = lambda : [int(a)-1 for a in input().split()]

from bisect import bisect_right, bisect_left
from collections import defaultdict
from heapq import heappop, heappush, heapify
DD = defaultdict
BSL = bisect_left
BSR = bisect_right

inf = 1001001001001001001
mod = 998244353

@extend
class int:
    @llvm
    def __mod__(self, v: int) -> int:
        %ini = srem i64 %self, %v
        %added = add i64 %ini, %v
        %fin = srem i64 %added, %v
        ret i64 %fin
    
    @llvm
    def __floordiv__(self, v: int) -> int:
        %quot = sdiv i64 %self, %v 
        %rem = srem i64 %self, %v
        %sgn = xor i64 %self, %v
        %is_neg = icmp slt i64 %sgn, 0
        %notzero = icmp ne i64 %rem, 0
        %flag = and i1 %is_neg, %notzero
        %adj = select i1 %flag, i64 -1, i64 0
        %fin = add i64 %quot, %adj
        ret i64 %fin
    
    def bit_length(self) -> int:
        return 64-abs(self).__ctlz__()
    
    def bit_count(self) -> int:
        return self.__ctpop__()

@extend
class list:
    def pb(self, v: T): self.append(v)
    def eb(self, v: T): self.extend(v)
    def __str__(self): return " ".join(map(str, self))

@extend
class float:
    def __str__(self): return f"{self:.15f}"

def _override_pow():
    _builtin_pow = pow
    def codon_pow(base, exp, mod = None):
        if mod is None: return _builtin_pow(base, exp)
        if exp < 0:
            a, b, x, y = base, mod, 1, 0
            while b:
                q = a // b
                a, b, x, y = b, a - q * b, y, x - q * y
            if abs(a) != 1:
                raise ValueError('base is not invertible for the given modulus')
            base, exp = a * x, - exp
        v = _builtin_pow(base, exp, mod)
        return v + mod if (mod < 0 < v) or (v < 0 < mod) else v
    return codon_pow
pow = _override_pow()

