# 二部グラフの辺彩色

同じ頂点を使う辺どうしが重ならないよう、すべての辺を最小個数のグループに分ける。

## 主な機能

`bipartite_edge_coloring(left_size, right_size, edges)`は、左側・右側の頂点数と`(左頂点, 右頂点)`の辺リストを受け取り、各辺の色番号を返す。同じ頂点に接する辺は必ず異なる色になる。

たとえば、人と機械の組を辺で表したとき、同じ色の作業は人も機械も重複しない。全作業を最小回数に分けて実行したい場合に使える。

- 必要な色数は最大次数Δと一致する。多重辺も1本ずつ異なる作業として扱う。
- 色番号は0以上Δ未満。辺がなければ`[]`を返す。
- 時間 O(V + E√V log(Δ + 1))、追加メモリ O(V + E)。Vは左右を合わせた頂点数、Eは入力辺数。

## 使い方

```python
from library_codex.graph_matching.BipartiteEdgeColoring import bipartite_edge_coloring

edges = [(0, 0), (0, 1), (1, 1), (1, 1)]
colors = bipartite_edge_coloring(2, 2, edges)
count = max(colors, default=-1) + 1
assert count == 3
groups = [[] for _ in range(count)]
for edge_id, color in enumerate(colors):
    groups[color].append(edge_id)
```

- `colors[i]`: 入力`edges[i]`に割り当てた色。リストの長さは入力辺数と同じ。
- `count`: 最小色数。辺がなければ0。
- `groups[c]`: 色cの入力辺番号。同じグループ内の辺は左頂点も右頂点も重複しない。

## 仕組み

同じ側の頂点を、次数の合計がΔ以下になる範囲でまとめる。その後、仮の辺を加えて全頂点の次数をΔに揃える。先に頂点をまとめることで、仮の辺を含めても辺数をO(E)に抑える。

次数が偶数なら、辺を巡回して交互に振り分け、次数が半分の2グラフへ分割する。奇数なら完全マッチングを1色として取り除いてから分割する。分割はスタックで処理し、再帰や頂点ごとのノードクラスは使わない。

## 注意点

- 左右の頂点番号はそれぞれ独立。`(0, 0)`は左の0番と右の0番を結ぶ辺で、自己ループではない。
- 頂点を彩色する関数ではない。返り値の添字は頂点番号ではなく辺番号。
- 入力の辺リストは変更しない。色の割り当て自体は一意ではない。

## 参考

- [maspyの二部グラフ辺彩色](https://maspypy.github.io/library/graph/bipartite_edge_coloring.hpp)
- [Library Checkerの公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/bipartite_edge_coloring/sol/correct.cpp)
