# 差分制約の解と上下限

## 主な機能

変数間の差について「2以上5以下」のような条件を登録し、全条件を満たす整数値を求めます。条件が矛盾するときは `None` になります。

`add(u, v, upper, lower=lower)` が表す条件は次です。

$$\mathrm{lower}\le x_v-x_u\le\mathrm{upper}.$$

`None` の上限・下限は制限なしです。頂点に `None` を渡すと定数0を表し、1変数だけへの上下限にも使えます。

解が存在する場合、`bounds(source)` で全変数とsourceとの差の最小値・最大値を調べられます。負辺を含む系は最初にBellman–Ford法で解を求め、その解で辺を非負に変換して以後の上下限をDijkstra法で求めます。

## 使い方

```python
from library_codex.shortest_path.DifferenceConstraints import DifferenceConstraints

system = DifferenceConstraints(3)
system.add(0, 1, 5, lower=2)
system.add(1, 2, 3)
system.fix(0, 10)

values = system.solve()
assert values[0] == 10
assert 2 <= values[1] - values[0] <= 5
assert values[2] - values[1] <= 3
assert system.bounds() == [(10, 10), (12, 15), (None, 18)]
assert system.bounds(0) == [(0, 0), (2, 5), (None, 8)]
```

- `solve()`: 長さNの整数list。添字vに変数vの値が入ります。解の一つであって、全変数を最大化した値ではありません。
- `bounds()`: 長さNの `(lower, upper)` のlist。各変数自身の取り得る限界です。
- `bounds(source)`: 同じ形式で、各変数からsourceを引いた差の限界です。
- 限界の `None` は、その方向にいくらでも大きく／小さくできることを表します。有限な両端は含みます。

## 注意点

- N変数・M制約辺として、初回の `solve` は最悪O(N+NM)、全辺が非負ならO(N+M)です。
- 解が計算済みなら `bounds` はO(N+M log(N+M+2))です。未計算なら先に `solve` 相当の処理を行います。
- `add` と `fix` は計算済みの解を無効にします。上下限を両方指定すると2辺になります。
- 矛盾した系の `bounds` は `ValueError` になります。
- 整数の係数を渡してください。厳密な不等式は、たとえば差が5未満なら上限4として登録します。

## 参考

[qandori/cp-library: 差分制約](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/graph/difference_constraints.hpp)。差の範囲取得を参考にし、解専用objectを増やさず同じclassで扱います。

