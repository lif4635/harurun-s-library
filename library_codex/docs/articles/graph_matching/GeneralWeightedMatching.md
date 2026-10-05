# 一般グラフの最大重みマッチング

端点を共有しない辺の組を選び、重みの合計を最大にします。二部グラフでなくても使えます。

## 主な機能

- 整数の重みを持つ無向辺を登録し、各頂点が誰と組になったかを求めます。
- 構築は O(N²)時間・領域、辺の追加は O(1)、最大重みマッチングの計算は O(N³)です。
- Blossomの縮約・展開を使い、奇数長の閉路を含むグラフも扱います。辺情報を整数配列に保持し、再帰は使いません。

## 使い方

```python
from library_codex.graph_matching.GeneralWeightedMatching import GeneralWeightedMatching

matching = GeneralWeightedMatching(4)
edges = [(0, 1, 9), (0, 2, 8), (1, 2, 10), (2, 3, 7)]
for u, v, weight in edges:
    matching.add_edge(u, v, weight)
mate = matching.run()
pairs = [(v, u) for v, u in enumerate(mate) if v < u]
```

- `mate = [1, 0, 3, 2]`: 頂点0と1、頂点2と3がそれぞれ組になります。
- `pairs = [(0, 1), (2, 3)]`: 各辺を1回だけ取り出したlistです。重みの合計は16です。
- `mate[v] = -1`: 頂点vはどの辺にも使われていません。

## 注意点

- 最大化するのは重みの合計です。辺数を最優先にする最大マッチングや、全頂点を必ず組にする完全マッチングとは異なります。
- 自己ループと重み0以下の辺は無視します。同じ端点間の辺は最大の重みだけを使います。
- すべての辺を登録してから `run()` を呼びます。実行後の辺追加には対応しません。
- 複数の最適解があるとき、どの組を返すかは保証しません。
