# 線形漸化式の推定と遠くの連続項

## 主な機能

先頭D項と漸化式の係数から、離れた添字の値を998244353で割った余りを求める。

$$
a_n=\sum_{j=0}^{D-1}c_j a_{n-1-j}\qquad(n\ge D)
$$

1項だけなら`linear_recurrence_nth`、ある位置からまとめて取得するなら`linear_recurrence_slice`を使う。後者は開始位置K、項数Mに対して`O(D log(D+1) log(K+2)+(D+M) log(D+M+1))`。Kまで順番に生成せず、第n項計算をM回繰り返すこともない。

漸化式が未知の場合は`berlekamp_massey`で観測列に一致する最短の係数列を推定できる。`nth_term`は推定と1項の計算をまとめて行う。有理式の分子・分母が直接分かっている場合は`bostan_mori`で指定次数の係数を求める。

## 使い方

```python
from library_codex.fps998.LinearRecurrence import linear_recurrence_nth, linear_recurrence_slice

initial = [0, 1]
coefficients = [1, 1]
assert linear_recurrence_nth(initial, coefficients, 10) == 55
assert linear_recurrence_slice(initial, coefficients, 10, 5) == [55, 89, 144, 233, 377]
```

- `initial`: 漸化式を適用する前の先頭D項。
- `coefficients`: 直前、2項前、…、D項前に掛ける係数の順。
- 返るlist: 指定した先頭から添字の昇順。例では第10〜14項。

## 仕組み

漸化式の母関数を有理式P/Qで表す。遠くの連続項は、1/Qの必要な係数区間を偶数・奇数の分離で求め、それを使って開始位置を移した分子を計算する。段階ごとのNTT結果を保持し、逆向きの復元でも再利用する。

## 注意点

- `linear_recurrence_slice`の初期値と係数は同じ長さにする。`count=0`なら空list。
- 末尾の係数が0の場合も使える。全係数0なら初期値の後はすべて0。
- 係数の推定は与えた観測列に対するもの。未知の将来の列まで一致する保証には、元の列の漸化式次数などの前提が必要。
- 演算はすべて998244353上。通常の整数値そのものは返さない。

## 参考

[Library Checker公式解答](https://github.com/yosupo06/library-checker-problems/blob/master/other/consecutive_terms_of_linear_recurrent_sequence/sol/correct.cpp)
