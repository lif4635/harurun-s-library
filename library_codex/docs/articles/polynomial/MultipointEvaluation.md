# 多点評価・補間と標本点のシフト

多項式を複数の点で評価する。また、点と値の組から多項式の係数を復元する。

## 主な機能

- `multipoint_evaluation(f, points)` — 各点での値を、pointsの順に返す。
- `polynomial_interpolation(points, values)` — 異なるN点の値から次数N未満の係数を復元する。
- `ProductTree(points)` — 評価点を固定し、積木を複数回の評価・補間で使い回すclass。
- `interpolate_consecutive(values, point)` — f(0), …, f(N-1)から1点の値を `O(N + log mod)` で求める。
- `sample_point_shift(values, point, count)` — 標本値を連続した別の点へずらす。998244353でcount<modなら `O((N+count) log(N+count) + log mod)`。

一般のN点での評価・補間は、多項式積の時間をM(N)として `O(M(N) log(N+1))` が目安。入力多項式が点数より長い場合の剰余計算は別途必要。

## 使い方

```python
from library_codex.polynomial.MultipointEvaluation import ProductTree, sample_point_shift

tree = ProductTree([2, 4, 7])
values = tree.evaluate([1, 2, 3])
assert values == [17, 57, 162]
assert tree.interpolate(values) == [1, 2, 3]
assert sample_point_shift([1, 6, 17], 3, 3) == [34, 57, 86]
```

- `evaluate`の入力: 定数項から順の係数列。例ではf(x)=1+2x+3x²。
- `interpolate`の入力: 登録済みの各点での値。返り値は長さNの係数列。
- `sample_point_shift`の入力: f(0), f(1), f(2)。出力はf(3), f(4), f(5)。
- `tree.polynomial`: 各(x-points[i])を掛けた多項式の係数列のコピー。

## 注意点

- 係数列を受け取るTaylor shiftと、標本値を受け取る `sample_point_shift` は別の操作。
- 評価点の重複は評価だけならよい。補間では法上で互いに異なる必要がある。
- 連続点の補間・シフトは標本数N以上の次数を持つ多項式には使えない。
- 法は素数。省略時は998244353。
- 入力配列は変更しない。
