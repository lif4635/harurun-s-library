"""
ACL依存注意
いずれ書き直します
"""

from atcoder.scc import SCCGraph
def DAG_constract(edge):
    """
    SCC -> DAG構築
    """
    n = len(edge)
    
    g = SCCGraph(n)
    for pre in range(n):
        for to in edge[pre]:
            g.add_edge(pre,to)
    
    groups = g.scc()
    nl = len(groups)
    label = [-1]*n
    for idx,group in enumerate(groups):
        for x in group:
            label[x] = idx    
    
    nedge = [set() for i in range(nl)]
    for group in groups:
        for pre in group:
            for to in edge[pre]:
                if label[pre] == label[to]:
                    continue
                nedge[label[pre]].add(label[to])
    
    return nedge,groups