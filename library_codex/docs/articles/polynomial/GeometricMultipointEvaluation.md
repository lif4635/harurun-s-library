# 等比数列上の多点評価と補間

多項式の値を等比数列上でまとめて求める。また、その値の列から元の係数を復元する。

## 主な機能

- `multipoint_evaluation_geometric` — 係数列から、初項a・公比rの各点での値を求める。係数数N、評価点数Cに対し、998244353では `O((N+C) log(N+C))`。
- `interpolate_geometric` — N個の標本値から次数N未満の多項式を復元する。998244353では `O(N log N)`。評価点は互いに異なる必要がある。

評価点は次の順に並ぶ。

$$
a, ar, ar^2, \ldots
$$

## 使い方

```python
from library_codex.polynomial.GeometricMultipointEvaluation import multipoint_evaluation_geometric, interpolate_geometric

f = [1, 2, 3]
values = multipoint_evaluation_geometric(f, 2, 3, 3)
assert values == [17, 121, 1009]
assert interpolate_geometric(values, 2, 3) == f
```

- `f`: 定数項から順の係数列。例では1+2x+3x²。
- `values`: 評価点2, 6, 18での値。
- 補間の返り値: `values`と同じ長さの係数列。最高次側の0も残る。

## 注意点

- 評価では初項0、公比0・1も使える。
- 補間では、2点以上なら初項は0以外。公比0は2点の場合だけ使える。
- 公比のN乗が1でも、最初のN点が異なれば補間できる。
- 係数の法は素数。省略時は998244353。
- 入力配列は変更しない。

## 仕組み

等比数列の指数を三角数へ分解し、評価をmiddle productに変換する。補間では各点での分母を等比数列の積で作り、middle productと多項式積を1回ずつ使う。

## 参考

- [Library Checker公式解法](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/polynomial/polynomial_interpolation_on_geometric_sequence/sol/correct.cpp)
