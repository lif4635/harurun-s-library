def Cartesian_Tree(a):
    n = len(a)
    par = [-1]*n
    
    st = []
    for i, v in enumerate(a):
        s = -1
        while st and a[st[-1]] > v:
            s = st.pop()
        if s != -1:
            par[s] = i
        if st:
            par[i] = st[-1]
        st.append(i)
    return par