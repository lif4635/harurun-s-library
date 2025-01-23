# https://judge.yosupo.jp/submission/263000

def Z_algorism(s):
    """
    z[i] = LCP(s,s[i:])
    """
    n = len(s)
    z = [0]*n
    z[0] = n
    l,r = 0,0
    for i in range(1, n):
        t = max(0, min(r-i, z[i-l]))
        while i+t < n and s[t] == s[i+t]:
            t += 1
        if i+t > r:
            l,r = i,i+t
        z[i] = t
    return z

s = input()
print(*Z_algorism(s))