def bi_float(comparison, ok = 0, ng = inf, eps = 10**(-9)):
    """
    めぐる式二分探索
    """
    if not comparison(ok):
        # okの設定をミスっていませんか？
        return None

    # 相対誤差と絶対誤差のどちらかがeps以下で終了
    while abs(ng - ok)/max(1, abs(ng)) > eps:
        mid = ok + (ng - ok)/2
        if comparison(mid): ok = mid
        else: ng = mid
    
    return ok
