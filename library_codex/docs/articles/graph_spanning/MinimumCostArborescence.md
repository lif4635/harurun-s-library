# 有向最小全域木

指定した根から全頂点へ到達できるように有向辺を選び、辺の費用の合計を最小にする。

## 主な機能

`minimum_cost_arborescence(n, root, edges)`に、頂点数・根・`(始点, 終点, 費用)`の辺リストを渡す。返る辺は、根以外の各頂点へちょうど1本ずつ入り、全体で有向木になる。

- 負の費用、多重辺を扱える。自己ループは選ばない。
- 根から到達できない頂点があるときは`None`を返す。
- 時間 O((V + E) log(V + E))、追加メモリ O(V + E)。

## 使い方

```python
from library_codex.graph_spanning.MinimumCostArborescence import minimum_cost_arborescence

edges = [(0, 1, 5), (0, 2, 9), (1, 2, 1), (2, 1, 1)]
cost, ids = minimum_cost_arborescence(3, 0, edges)
assert cost == 6
assert ids == [0, 2]
chosen_edges = [edges[i] for i in ids]
assert chosen_edges == [(0, 1, 5), (1, 2, 1)]
```

- `cost`: 選んだ辺の費用の合計。
- `ids`: 入力`edges`における辺番号の昇順リスト。頂点の親番号ではない。
- `None`: その根では全域木を作れない。tupleへ展開する前に確認する。

頂点数が1なら`(0, [])`、空のグラフにも`(0, [])`を返す。

## 仕組み

各頂点へ入る最安の辺を選ぶ。選んだ辺に閉路ができたら閉路を1成分へ縮約し、成分へ入る辺の追加費用を比較する。候補辺は一括加算と併合ができるヒープで管理するため、縮約のたびに全辺を走査し直さない。

縮約の履歴から元の辺番号を復元する。ヒープと履歴は整数IDと配列で保持し、再帰や辺ごとのノードクラスを使わない。

最安の入辺を選んだ時点で閉路がなければ、ヒープを作らずにその木を返す。

## 注意点

- 求めるのは根から外へ向かう全域木。全頂点から根へ向かう木なら、入力の辺を逆向きにする。
- 最小解が複数あれば、そのうち1つを返す。
- 入力の辺リストは変更しない。

## 参考

- [Library Checkerの公式解法](https://github.com/yosupo06/library-checker-problems/blob/master/graph/directedmst/sol/correct.cpp)
- [maspyの有向最小全域木](https://maspypy.github.io/library/graph/directed_mst.hpp)
