# 最大流と最小カット

各辺の容量を守って始点から終点へ流せる最大量と、そのときの辺ごとの流量を求める。

## 主な機能

- `MaxFlowGraph(n)`へ有向辺を追加し、`flow(source, sink, limit)`で追加の流量を求める。`limit`省略時は流せるだけ流す。
- `get_edge(i)`で元の辺の容量・流量、`min_cut(source)`で残余辺を通って到達できる頂点を取得する。
- 同じ始点・終点なら、流量制限付きの計算後や辺の追加後にも続けて流せる。
- 整数IDと配列を使う非再帰Dinic。最大流は最悪`O(V²E)`、保持する領域は`O(V+E)`。

## 使い方

```python
g = MaxFlowGraph(4)
first = g.add_edge(0, 1, 5)
g.add_edge(1, 3, 5)
g.add_edge(0, 2, 3)
g.add_edge(2, 3, 3)
part = g.flow(0, 3, 2)
rest = g.flow(0, 3)
edge = g.get_edge(first)
side = g.min_cut(0)
```

- `part`: 今回追加した流量`2`。
- `rest`: 続きで追加した流量`6`。累計は`part + rest`。
- `edge`: `(始点, 終点, 元の容量, 現在の流量)`。この例では`(0, 1, 5, 5)`。
- `side[v]`: 残余グラフで始点から到達できるか。最大まで流した後は最小カットの始点側を表す。

## 下限のある辺

`feasible_circulation(n, edges)`は各辺に`(始点, 終点, 下限, 上限)`を与え、全頂点で流入と流出が一致する流量のlistを返す。`max_flow_with_bounds(n, edges, source, sink)`は同じ辺形式で始点・終点を指定し、`(最大流量, 辺ごとの流量)`を返す。どちらも条件を満たせなければ`None`。

## 注意点

- 容量は非負の有限値。平行辺・自己ループを追加できる。
- `flow`の返り値は累計ではなく、その呼出しで追加した量。
- `change_edge`は指定辺だけを変更する。利用者が流量保存則を壊す変更をすると、その後の最大流の前提も崩れる。
- 流量上限で途中終了した場合、`min_cut`は到達可能性だけを表し、最小カットとは限らない。
- 内部の`graph`は残余辺IDの隣接list。辺の情報は`get_edge`・`edges`・`residual_graph`から取得する。
