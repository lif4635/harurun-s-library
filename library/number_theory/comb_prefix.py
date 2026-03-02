class Combprefix:
    def __init__(self, lim, mod=mod):
        self.n = 0
        self.k = 0
        self.c = 1
        self.s = 1
        self.mod = mod
        self.inv = [1] * (lim + 2)
        for i in range(2, lim + 2):
            self.inv[i] = mod - self.inv[mod % i] * (mod // i) % mod
    
    def move(self, n, k):
        while self.n < n:
            self.s = (2 * self.s - self.c) % self.mod
            self.c = self.c * (self.n + 1) % self.mod * self.inv[self.n + 1 - self.k] % self.mod
            self.n += 1
        while self.k > k:
            self.s = (self.s - self.c) % self.mod
            self.c = self.c * self.k % self.mod * self.inv[self.n - self.k + 1] % self.mod
            self.k -= 1
        while self.n > n:
            self.c = self.c * (self.n - self.k) % self.mod * self.inv[self.n] % self.mod
            self.s = (self.s + self.c) * self.inv[2] % self.mod
            self.n -= 1
        while self.k < k:
            self.c = self.c * (self.n - self.k) % self.mod * self.inv[self.k + 1] % self.mod
            self.s = (self.s + self.c) % self.mod
            self.k += 1
        return self.s
        
    def get(self):
        return self.s