class eraseble_heapq:
    def __init__(self, a = []):
        self.que = a.copy()
        heapify(self.que)
        self.erase = []
    
    def append(self, x):
        heappush(self.que, x)
    
    def remove(self, x):
        heappush(self.erase, x)
    
    def heappop(self):
        while self.erase and self.que[0] == self.erase[0]:
            heappop(self.que)
            heappop(self.erase)
        return heappop(self.que)
    
    def top(self):
        while self.erase and self.que[0] == self.erase[0]:
            heappop(self.que)
            heappop(self.erase)
        return self.que[0]
    
    def __len__(self):
        return len(self.que) - len(self.erase)
    
    def __str__(self):
        res = [x for x in self.que if not x in self.erase]
        res.sort()
        return str(res)