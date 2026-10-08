# 隣接頂点を異なる色で塗る最小色数

単純無向グラフの頂点を塗り分けるために必要な最小色数を求める。各頂点に何色を割り当てるかは返さない。

## 主な機能

- `chromatic_number(graph, exact=False)` — 隣接listから彩色数を求めるfunction。
- `chromatic_number_from_edges(n, edges, exact=False)` — 辺listを受け取るfunction。
- O(N 2^N)回の整数演算、O(2^N)個の整数を使う。全頂点部分集合を作るので、小さいグラフ向け。公式問題ではN=20まで検証している。

## 使い方

```python
from library_codex.graph_enumeration.ChromaticNumber import chromatic_number

assert chromatic_number([[1, 2], [0, 2], [0, 1]], exact=True) == 3
assert chromatic_number([[], []], exact=True) == 1
assert chromatic_number([], exact=True) == 0
```

## 判定の違い

- exact=TrueはPythonの任意精度整数で計算し、厳密な答えを返す。今回の公式検証とベンチマークもこの設定。
- 省略時は固定した2つの法で計算する。両方の剰余が0になる衝突によって、理論上は必要色数を過大評価する場合がある。
- 剰余版が常に速いとは限らない。厳密さが必要な場合はexact=Trueを明示する。
