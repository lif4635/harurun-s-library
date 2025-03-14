def DFS(edge):
    stack = [(0,-1,0)]
    while stack:
        now,par,flag = stack.pop()
        if flag == 0:
            stack.append((now,par,1))
            # 行きがけ
            for chi in edge[now]:
                if chi != par:
                    # 通りがけ
                    stack.append((chi,now,0))
        else:
            if par == -1:
                return 
            # 帰りがけ
            pass