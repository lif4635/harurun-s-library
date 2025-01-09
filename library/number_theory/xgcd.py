def xgcd(a:int, b:int) -> tuple[int,int,int]:
    """
    ans = a*x0 + b*y0
    """
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q, a, b = a//b, b, a%b
        x0, x1 = x1, x0-q*x1
        y0, y1 = y1, y0-q*y1
    return a, x0, y0
