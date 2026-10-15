def bell(now,x):
    """
    number of ways to partition a set of n labeled elements.
    """
    if x == n:
        calc(now)
        return
    
    for i in range(len(now)):    
        now[i] += 1<<x
        bell(now,x+1)
        now[i] -= 1<<x
    
    now.append(1<<x)
    bell(now,x+1)
    now.pop()
    return