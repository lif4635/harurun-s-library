# 互いに隣接しない頂点を最大限選ぶ

単純無向グラフから、選んだ頂点同士を結ぶ辺が一本もない頂点集合を求める。要素数を最大化する場合と、頂点重みの合計を最大化する場合を扱う。

## 主な機能

- `maximum_independent_set(graph)` — 最大個数の頂点番号listを返すfunction。
- `maximum_independent_set_mask(graph)` — 同じ問題の答えを要素数とbit集合で返すfunction。
- `maximum_weight_independent_set(graph, weight)` — 重み合計とbit集合を返すfunction。空集合も許す。

いずれも厳密解だが、最悪では指数時間。最大個数版は補グラフ上のクリーク探索に彩色による枝刈りを使う。公式問題ではN=40まで検証しているが、すべてのグラフで同じ速さになるわけではない。

## 使い方

```python
from library_codex.graph_enumeration.MaximumIndependentSet import maximum_independent_set, maximum_weight_independent_set

graph = [[1], [0, 2], [1]]
assert maximum_independent_set(graph) == [0, 2]
value, mask = maximum_weight_independent_set(graph, [2, 10, 3])
assert value == 10
assert [v for v in range(3) if mask >> v & 1] == [1]
```

- list版は選んだ頂点番号の昇順。
- maskのbit vが1なら頂点vを選ぶ。各頂点の所属番号を返す配列ではない。
- 最適解が複数ある場合の選び方は保証しない。
- 重み付き版は0以下の頂点を選ばなくてよいので、全重みが負なら(0, 0)になる。
