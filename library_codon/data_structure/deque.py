class deque:
    def __init__(self, data=[], max_size=10**6):
        self.size = max_size
        self.head = 0
        self.tail = len(data)
        self.data = [-1]*self.size
        self.data[:self.tail] = data
    
    def __len__(self):
        return (self.tail - self.head) % self.size
    
    def __getitem__(self, i):
        l = len(self)
        if not -l <= i < l: raise IndexError(f"index out of range: {i}")
        if i < 0: i += l
        return self.data[(self.head + i) % self.size]
    
    def __setitem__(self, i, x):
        l = len(self)
        if not -l <= i < l: raise IndexError(f"index out of range: {i}")
        if i < 0: i += l
        self.data[(self.head + i) % self.size] = x
    
    def append(self, x):
        self.data[self.tail] = x
        self.tail += 1
        self.tail %= self.size
    
    def appendleft(self, x):
        self.head -= 1
        self.head %= self.size
        self.data[self.head] = x
    
    def pop(self):
        assert self.head != self.tail
        self.tail -= 1
        self.tail %= self.size
        return self.data[self.tail]
        
    def popleft(self):
        assert self.head != self.tail
        res = self.data[self.head]
        self.head += 1
        self.head %= self.size
        return res
        
    def __str__(self):
        return str(list(self))
    
    def __repr__(self):
        return f"deque({list(self)})"
