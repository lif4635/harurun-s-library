class BinaryTrie:
    def __init__(self, bit_len=30):
        self.bit_len = bit_len
        self.lazy_xor = 0
        self.nodes = [-1, -1]
        self.count = [0]

    def add(self, x):
        v = x ^ self.lazy_xor
        curr = 0
        self.count[0] += 1
        for i in range(self.bit_len - 1, -1, -1):
            b = (v >> i) & 1
            idx = (curr << 1) | b
            nxt = self.nodes[idx]
            if nxt == -1:
                nxt = len(self.count)
                self.nodes[idx] = nxt
                self.nodes.extend([-1, -1])
                self.count.append(0)
            curr = nxt
            self.count[curr] += 1

    def find(self, x):
        v = x ^ self.lazy_xor
        curr = 0
        for i in range(self.bit_len - 1, -1, -1):
            b = (v >> i) & 1
            curr = self.nodes[(curr << 1) | b]
            if curr == -1:
                return 0
        return self.count[curr]

    def delete(self, x):
        if self.find(x) == 0:
            return
        v = x ^ self.lazy_xor
        curr = 0
        self.count[0] -= 1
        for i in range(self.bit_len - 1, -1, -1):
            b = (v >> i) & 1
            curr = self.nodes[(curr << 1) | b]
            self.count[curr] -= 1

    def get_kth(self, k, xor_val=0):
        if k < 1 or k > self.count[0]:
            return None
        curr = 0
        res = 0
        v = self.lazy_xor ^ xor_val
        for i in range(self.bit_len - 1, -1, -1):
            b = (v >> i) & 1
            left_node = self.nodes[(curr << 1) | b]
            left_cnt = self.count[left_node] if left_node != -1 else 0
            
            if k <= left_cnt:
                curr = left_node
            else:
                k -= left_cnt
                curr = self.nodes[(curr << 1) | (1 - b)]
                res |= (1 << i)
        return res

    def min_element(self, xor_val=0):
        return self.get_kth(1, xor_val)

    def max_element(self, xor_val=0):
        return self.get_kth(self.count[0], xor_val)

    def operate_xor(self, x):
        self.lazy_xor ^= x

    def count_leq(self, val, xor_val=0):
        v = self.lazy_xor ^ xor_val
        curr = 0
        res = 0
        for i in range(self.bit_len - 1, -1, -1):
            if curr == -1:
                break
            b = (v >> i) & 1
            val_b = (val >> i) & 1
            
            if val_b == 1:
                left_node = self.nodes[(curr << 1) | b]
                if left_node != -1:
                    res += self.count[left_node]
                curr = self.nodes[(curr << 1) | (1 - b)]
            else:
                curr = self.nodes[(curr << 1) | b]
                
        if curr != -1:
            res += self.count[curr]
            
        return res