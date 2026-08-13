# 二頂点間にある橋を調べる

## 主な機能

無向グラフを、橋で分かれない2-edge-connected componentごとに縮約して森を作ります。元の二頂点 $u,v$ を指定すると、次を求められます。

- $u$ から $v$ へ行くとき必ず通る橋の本数
- その橋を通る順に並べた、入力辺のedge ID列
- $k$ 番目に通る橋
- 指定した一本の辺を消すと $u,v$ が分断されるか

構築は $O((V+E)\log V)$、本数と $k$ 番目のqueryは $O(\log V)$ です。橋の列挙は出力する本数を $K$ として $O(\log V+K)$ です。

## 使い方

```python
from library_codex.graph_connectivity.BridgeForest import BridgeForest

edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4)]
bridge = BridgeForest(5, edges)

assert bridge.bridge_distance(0, 4) == 2
assert bridge.bridge_path(0, 4) == [3, 4]
assert bridge.kth_bridge(0, 4, 0) == 3
assert bridge.is_bridge_separator(3, 0, 4)
```

edge IDは`edges`へ渡した順番です。平行辺を含む多重グラフも扱えます。

## 返り値の境界

- 二頂点が同じ2-edge-connected component: `bridge_distance`は`0`、`bridge_path`は空list。
- 二頂点がもともと非連結: `bridge_distance`は`-1`、`bridge_path`は`None`。
