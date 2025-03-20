from collections import defaultdict
import random

class hasedict(defaultdict):
    def __init__(self, type):
        self.b = random.randint(0, 1 << 30)
        super().__init__(type)

    def __getitem__(self, key):
        return super().__getitem__(key ^ self.b)
    
    def __setitem__(self, key, value):
        super().__setitem__(key ^ self.b, value)

    def __delitem__(self, key):
        return super().__delitem__(key ^ self.b)
    
    def get(self, key):
        return super().get(key ^ self.b)
    
    def pop(self, key):
        return super().pop(key ^ self.b)
    
    def __contains__(self, key):
        return super().__contains__(key ^ self.b)
    
    def __repr__(self):
        return str({k ^ self.b: v for k, v in super().items()})
    
    def __str__(self):
        return str({k ^ self.b: v for k, v in super().items()})