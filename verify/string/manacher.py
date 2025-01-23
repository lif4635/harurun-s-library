# https://judge.yosupo.jp/submission/263001

def manacher(s):
    """
    Palindromes radius
    Even length : insert dummy
    """
    ls = len(s)
    red = [0]*ls
    
    # i : center, j : redius
    i,j = 0,0 
    while i < ls:
        while i - j >= 0 and i + j < ls and s[i-j] == s[i+j]:
            j += 1
        red[i] = j
        k = 1
        while i - k >= 0 and i + k < ls and k + red[i-k] < j:
            red[i+k] = red[i-k]
            k += 1
        i += k
        j -= k
    return red

s = input().replace("", "*")
res = manacher(s)
print(*[res[i]-1 for i in range(1,len(s)-1)])