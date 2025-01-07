def manacher(s):
    """
    回分半径
    偶数長のものが知りたいときはダミー文字を挿入する
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
