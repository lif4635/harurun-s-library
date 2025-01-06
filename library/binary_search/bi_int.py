def bi_int(comparison, ok = 0, ng = inf):
    """
    めぐる式二分探索
    """
    if not comparison(ok):
        # okの設定をミスっていませんか？
        return None
    
    while abs(ng - ok) > 1:
        mid = ok + (ng - ok)//2
        if comparison(mid): ok = mid
        else: ng = mid
    
    return ok
