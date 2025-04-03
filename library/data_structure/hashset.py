
import random
class hashset(set):
    def __init__(self, iter = None):
        self.b = random.randint(0, 1 << 30)
        super().__init__()
        if iter != None:
            for v in iter:
                super().add(v ^ self.b)
    
    def add(self, elem):
        super().add(elem ^ self.b)
    
    def discard(self, elem):
        return super().discard(elem ^ self.b)
    
    def pop(self):
        return super().pop() ^ self.b
    
    def __contains__(self, elem):
        return super().__contains__(elem ^ self.b)
    
    def __iter__(self):
        for v in super().__iter__():
            yield v ^ self.b
    
    def __str__(self):
        return str({v ^ self.b for v in super().__iter__()})
    
    def __len__(self):
        return super().__len__()