mod = 998244353

class Comb:
    def __init__(self, lim:int ,mod:int = mod):
        """
        mod : prime
        """
        self.fac = [1]*(lim+1)
        self.inv = [1]*(lim+1)
        self.finv = [1]*(lim+1)
        self.mod = mod
        for i in range(2,lim+1):
            self.fac[i] = self.fac[i-1]*i%self.mod
            self.inv[i] = -self.inv[mod%i]*(mod//i)%self.mod
            self.finv[i] = self.finv[i-1]*self.inv[i]%self.mod
    
    def C(self,a,b):
        assert b >= 0, "The second argument is negative."
        if a < b: return 0
        if a < 0: return 0
        return self.fac[a]*self.finv[b]%self.mod*self.finv[a-b]%self.mod
    
    def P(self,a,b):
        assert b >= 0, "The second argument is negative."
        if a < b: return 0
        if a < 0: return 0
        return self.fac[a]*self.finv[a-b]%self.mod
    
    def H(self,a,b): return self.C(a+b-1,b)
    def F(self,a): return self.fac[a]
    def Fi(self,a): return self.finv[a]
