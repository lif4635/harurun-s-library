def tri_float(solve, l = 0, r = inf, eps = 10**(-9)):
    while abs(r - l)/max(1, abs(r)) > eps:
        l2 = (l*2+r)/3
        r2 = (l+r*2)/3
        if solve(l2) > solve(r2): l = l2
        else: r = r2
    
    return l, solve(l)