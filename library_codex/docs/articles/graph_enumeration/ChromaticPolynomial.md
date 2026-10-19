# 色数を変えたときの塗り分け数

無向グラフをk色で正しく塗る方法の個数を、kの多項式として求める。隣接頂点には異なる色を使い、使えるk色は区別する。すべての色を使う必要はない。

## 主な機能

`chromatic_polynomial(graph, mod=998244353)`へ隣接リストを渡すと、彩色多項式の係数を定数項から順に返す。

$$
P(k)=c_0+c_1k+\cdots+c_Nk^N.
$$

返り値の`result[i]`が係数`c_i`に対応する。最小の色数だけを求める`chromatic_number`とは異なり、色数ごとの塗り方の数を扱う。

## 使い方

```python
from library_codex.graph_enumeration.ChromaticPolynomial import chromatic_polynomial

triangle = [[1, 2], [0, 2], [0, 1]]
coefficients = chromatic_polynomial(triangle)
colors = 4
count = sum(c * colors**i for i, c in enumerate(coefficients)) % 998244353
```

- `coefficients`は`[0, 2, 998244350, 1]`。負の係数−3は法で正規化して返す。
- 三角形の彩色多項式は次の通りで、`count`は`24`。

$$
P(k)=k(k-1)(k-2)=k^3-3k^2+2k.
$$

## 仕組み

各色の頂点集合は独立集合になる。集合冪級数を使って独立集合への分割を数え、色の割り当て数を掛けて多項式に変換する。

連結成分ごとに計算し、最後に多項式を掛け合わせる。木の成分はk(k−1)^(c−1)、完全グラフはk(k−1)…(k−c+1)を直接構築し、部分集合の計算を省く。

頂点数N、入力の隣接要素数M、各成分の頂点数cに対して、時間はO(M + N² + Σ c²2^c)、追加メモリはO(N + max(c2^c))。木・完全グラフの成分はO(c²)時間で処理する。

## 注意点

- 一般の連結成分では頂点数に対して指数時間なので、20頂点程度までを想定する。
- 片方向だけ記載した隣接リストも無向辺として扱う。要素は頂点番号の整数を渡す。
- 重複辺は1本と同じ。自己ループが1本でもあれば全係数が0になる。
- 頂点数0なら`[1]`。頂点があるが辺がない場合はkのN乗になる。
- 係数の法は2以上なら合成数でもよい。入力のグラフは変更しない。

## 参考

[Library Checker公式解答](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/graph/chromatic_polynomial/sol/correct.cpp)の独立集合と集合冪級数による計算を参考にしている。
