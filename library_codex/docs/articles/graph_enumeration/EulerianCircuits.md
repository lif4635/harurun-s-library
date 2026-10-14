# 有向オイラー閉路の個数

有向グラフの全辺を一度ずつ使って出発点へ戻る巡回路が、何通りあるかを求める。

## 主な機能

`count_eulerian_circuits(n, edges, mod)`は、頂点数と有向辺の列を受け取り、閉路の個数をmodで割った余りを返す。

- 並行辺は1本ずつ区別する。自己ループも使える。
- 同じ辺順を巡回シフトしたものは同一と数える。1本の辺を先頭に固定して数えることと等しい。
- 辺を持たない孤立頂点は無視する。全辺を通れない場合と、辺が1本もない場合は0。

辺を持つ頂点数をK、全頂点数をN、辺数をMとして、時間は`O(N + M + K³ + K log mod)`、追加領域は`O(N + M + K²)`。行列式で数えるため、大きな疎グラフ向けの線形時間アルゴリズムではない。

## 使い方

```python
from library_codex.graph_enumeration.EulerianCircuits import count_eulerian_circuits

edges = [(0, 1), (0, 1), (1, 0), (1, 0)]
assert count_eulerian_circuits(2, edges) == 2
assert count_eulerian_circuits(5, edges) == 2
assert count_eulerian_circuits(1, [(0, 0)] * 4) == 6
assert count_eulerian_circuits(2, [(0, 1)]) == 0
```

最初の例では0→1の並行辺を別々の辺として扱う。頂点だけを並べると同じに見えても、通る辺の順序が異なれば別の閉路。

## 仕組み

各頂点の入次数と出次数が一致するかを確かめ、孤立頂点を除いた有向ラプラシアンの余因子から、根に向かう全域木の個数を求める。BEST定理により、答えは次になる。

$$
\tau_r\prod_v (d_v-1)!
$$

ここで、積は辺を持つ頂点について取り、dは出次数、τは任意の根rへ向かう全域木の個数。辺を持つ成分が分かれている場合は余因子が0になり、答えも0になる。

## 注意点

- `edges`の各要素は`(出発頂点, 到着頂点)`。辺の重みや重複度を3要素目に指定する形式ではない。
- `mod`には素数を指定する。既定値は998244353。素数判定は行わない。
- 巡回シフト前の始点・開始辺まで区別したい場合、辺が1本以上なら結果に辺数を掛ける。
- 閉路の辺順自体は返さない。順序を構築する場合は`EulerianTrail`を使う。

## 参考

[Library Checkerの定義と公式解答](https://github.com/yosupo06/library-checker-problems/tree/master/graph/counting_eulerian_circuits)
