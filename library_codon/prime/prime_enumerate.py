def prime_enumerate(lim:int, get:int = 0) -> list[int]:
    """
    get = 0 : enumerate
    get = 1 : flag
    """
    lim += 1
    prime_flag = [1]*lim
    prime_enu = []
    prime_flag[0] = 0
    prime_flag[1] = 0
    for p in range(2,lim):
        if prime_flag[p]:
            prime_enu.append(p)
            for q in range(2*p,lim,p):
                prime_flag[q] = 0
    if get == 0:
        return prime_enu
    else:
        return prime_flag  
