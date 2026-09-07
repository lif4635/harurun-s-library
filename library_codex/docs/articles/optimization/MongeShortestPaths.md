# 辺数を固定したMonge DAGの最短路

## 主な機能

頂点 $0,1,\ldots,N$ と、すべての $i<j$ に辺 $i\to j$ があるDAGを扱う。辺重みは配列に展開せず、`cost(i, j)`で計算する。

- `monge_d_edge_shortest_path(N, k, cost)` — 0からNまで、ちょうどk辺を使う最短距離を返す。整数重みでは `O(N log N min(k, log(2+NW)))` 回の重み計算。Wは辺重みの絶対値の最大値で、上限を渡す必要はない。
- `monge_shortest_paths(N, cost)` — 辺数を制限せず、0から各頂点への最短距離を返す。`O(N log N)` 回の重み計算。
- `enumerate_monge_d_edge_shortest_paths(N, cost)` — すべてのkについて最短距離を返す。`O(N^2 log N)` 回の重み計算。特定のkだけが必要なら単一問合せを使う。

いずれも追加領域は `O(N)`。重み計算にTかかるなら、時間計算量にはその分を掛ける。

## 使い方

```python
from library_codex.optimization.MongeShortestPaths import monge_d_edge_shortest_path

def cost(i, j):
    return (j - i) ** 2

answer = monge_d_edge_shortest_path(10, 3, cost)
```

`answer`は34。たとえば $0\to3\to6\to10$ と進むと $3^2+3^2+4^2=34$ になる。返るのはコスト一つで、経路の頂点列ではない。

## 注意点

- 重みはMonge性を満たす必要がある。すべての $a<b<c<d$ に対し、$w(a,c)+w(b,d)\le w(a,d)+w(b,c)$ が条件。
- 辺重みはすべて有限値。辺の削除を無限大で表した任意のDAGには、そのまま使えない。
- 既定の `integer=True` は全辺の重みが `int` である場合の高速版。負の整数や大整数も使える。
- 非整数の重みは `integer=False` を指定する。従来の辺数別DPで同じ問いを解き、重み計算は `O(k N log N)` 回。floatは浮動小数点演算の誤差を伴う。
- 頂点Nまで到達できる辺数は1からN。N=k=0の場合だけ、0辺のコストが0となる。

## 仕組み

各辺に整数ペナルティpを加え、辺数を制限しない最短路を解く。pを増やすほど選ばれる辺数が減るため、二分探索でk辺に対応する境界を探す。同点では少ない辺数を選び、kが飛び越された場合もMonge性による辺数別最適値の凸性からコストを復元する。

ペナルティの範囲は倍々に広げて求める。重みが非常に大きい場合などは探索をk回で打ち切り、辺数別DPへ切り替える。すべて非再帰で処理する。

## 参考

- [maspypy: Monge DAGのd辺最短路](https://maspypy.github.io/library/convex/monge/monge_shortest_path_d_edge.hpp.html)
