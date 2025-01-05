def partition_num(n:int):
    """
    nの分割を昇順に返す
    """
    a = [1]*n
    
    while len(a) != 1:
        yield a
        
        pre = a.pop()
        cnt = pre
        l = len(a)
        for i in range(l-1,-1,-1):
            if a[-1] == pre:
                cnt += a.pop()
            else:
                if cnt >= pre+1:
                    a += [pre+1]
                    cnt -= pre+1
                    a += [1]*cnt
                    break
                else:
                    pre = a.pop()
                    cnt += pre
        else:
            a = [pre+1]
            cnt -= pre+1
            a += [1]*cnt
    yield a
