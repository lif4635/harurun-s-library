# 凸列・凹列とのmin-plus畳み込み

添字の和ごとに、2つの列から選んだ値の和の最小値を求める。

## 主な機能

入力をa、bとすると、返り値のk番目は次の値になる。

$$c_k=\min_{i+j=k}(a_i+b_j)$$

- `minplus_conv(arbitrary, convex)` — 第2引数が凸列。隣接差分が広義単調増加する列に使う。
- `minplus_conv_concave(arbitrary, concave)` — 第2引数が凹列。隣接差分が広義単調減少する列に使う。一般列の長さをA、凹列の長さをCとして `O(A log(C+1)+C)`。
- `minplus_conv_convex(first, second)` — 両方が凸列なら、差分を併合して `O(N+M)`。

凸列と凹列では使う処理が異なる。どちらの列にも条件がない一般のmin-plus畳み込みは対象外。

## 使い方

```python
from library_codex.convolution.MinPlusConvolution import minplus_conv_concave

a = [4, -2, 9]
b = [5, 7, 7, 4]
values, indices = minplus_conv_concave(a, b, return_argmin=True)
```

- `values` は `[9, 3, 5, 5, 2, 13]`。長さは `len(a)+len(b)-1`。
- `indices[k]` は、最小値を作ったb側の添字。a側の添字は `k-indices[k]`。
- たとえば `values[4] == 2` は `a[1]+b[3]` から得られる。
- `return_argmin` を省略すると、`values` だけを返す。

## 凹列の場合の仕組み

一般列を凹列の長さ以下の区間に分け、各区間の寄与を左右から計算する。片側の走査では、後から現れた候補が古い候補より良い範囲は、走査開始側の連続した範囲になる。凹性から候補間の差が単調になるため、その範囲の終端を二分探索できる。

候補の添字と有効範囲の終端だけを配列に保持する。各候補は高々1回追加・削除され、再帰は使わない。

## 注意点

- 凸性・凹性は入力の前提であり、関数内では検査しない。
- 負の値や大きな整数も使える。入力列は変更しない。
- どちらかが空なら空列を返す。
- 同値の最小値が複数あるとき、復元する添字の選び方は保証しない。
- 浮動小数点では丸め誤差で差分の単調性や大小関係が崩れることがある。無限大・NaNは対象外。

## 参考

- [Library Checker: Min Plus Convolution (Concave and Arbitrary)](https://judge.yosupo.jp/problem/min_plus_convolution_concave_arbitrary)
