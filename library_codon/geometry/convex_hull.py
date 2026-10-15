def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (b[0] - o[0]) * (a[1] - o[1])

def convex_hull(p):
    p.sort()
    lower = []
    for i in range(n):
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p[i]) <= 0:
            lower.pop()
        lower.append(p[i])
    
    upper = []
    for i in reversed(range(n)):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p[i]) <= 0:
            upper.pop()
        upper.append(p[i])
    
    return lower + upper