def partition_num(n:int):
    """
    nの分割を昇順に返す
    """
    a = [1]*n
    yield a
    while len(a) != 1:
        pre = a.pop()
        cnt = pre
        while a and (cnt <= pre or a[-1] == pre):
            pre = a.pop()
            cnt += pre
        else:
            a += [pre+1]
            cnt -= pre+1
            a += [1]*cnt
        yield a
