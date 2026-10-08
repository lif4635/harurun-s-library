# 指定頂点をすべて結ぶ最小費用の辺集合

無向グラフの一部の頂点を必ず結びたいとき、そのために使う辺の費用を最小化する。指定していない頂点を中継点として使ってよい。

## 主な機能

- `minimum_steiner_tree(n, edges, terminals)` — 最小費用と使用する辺番号を返すfunction。
- `steiner_tree_dp(n, edges, terminals)` — 指定頂点の各部分集合と終点について、最小費用を返すfunction。
- 指定頂点数Kに対して指数時間なので、グラフ全体ではなく「必ず結ぶ頂点」が少ない場合に使う。公式問題ではK=12まで検証している。

## 使い方

```python
from library_codex.graph_spanning.MinimumSteinerTree import minimum_steiner_tree, steiner_tree_dp

edges = [(0, 1, 2), (1, 2, 3), (1, 3, 4), (0, 3, 10)]
cost, edge_ids = minimum_steiner_tree(4, edges, [0, 2, 3])
assert cost == 9
assert set(edge_ids) == {0, 1, 2}
table = steiner_tree_dp(4, edges, [0, 2])
assert table[3][3] == 9
```

- costは選んだ辺の費用の合計。指定頂点を結べなければfloat('inf')。
- edge_idsは元のedgesの添字。順序は保証しないが、重複はない。
- table[mask][v]はmaskに含まれる指定頂点とvをすべて結ぶ最小費用。上のtable[3][3]は0・2・3を結ぶ費用。

## 仕組み

同じ頂点で二つの指定頂点集合を結合する部分集合DPと、そこから辺に沿って延ばすDijkstra法を組み合わせる。

辺集合だけを求める場合は、指定頂点を一つ終点に固定する。残りK-1頂点だけをDPに入れるため、全表を作る場合より状態数が半分になる。復元情報は各状態に整数一つを持ち、node objectは作らない。

## 注意点

- 辺費用は非負整数。0、多重辺、非連結グラフも扱える。
- terminalsの重複は除く。0個または1個なら費用0・辺なし。
- 全表のmaskのbit順は、terminalsの重複を除いた最初の出現順。mask=0の行は未定義状態としてすべてfloat('inf')。
