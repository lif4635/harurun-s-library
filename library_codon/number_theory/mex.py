def mex(s:list) -> int:
    s = set(s)
    ans = 0
    while ans in s: ans += 1
    return ans
