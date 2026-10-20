# 乗法的関数の値と総和

素数冪に対する値から乗法的関数を計算する。全整数の値が必要なら列挙、上限までの和だけなら`MultiplicativePrefixSum`を使う。

## 主な機能

- `MultiplicativePrefixSum(N, mod=None)` — 素数に対する累積和と`f(p**e)`を渡し、1からNまでの総和を求めるclass。約数個数・約数和・φ関数などに使える。
- `enumerate_multiplicative_function(N, prime_power)` — `f(0), …, f(N)`のlistを作るfunction。callbackは`prime_power(p**e, p, e)`。総和用classのcallbackとは引数が異なる。
- `DirichletQuotientSeries(N)` — Nを整数で割った商の位置だけに累積和を保持するclass。`dirichlet_multiply`・`dirichlet_divide`でDirichlet積や除算を扱う。
- `EnumerateMultiplicativePrefixSum(N, prefix_g, prefix_h)` — Dirichlet積`h=f*g`の累積和から、各商におけるfの累積和を復元するclass。

乗法性は、互いに素なa・bについて次が成り立つことを指す。`f(1)=1`とする。

$$
f(ab)=f(a)f(b)\quad(\gcd(a,b)=1).
$$

## 使い方

約数個数は、素数pで2、素数冪`p**e`で`e+1`。素数の個数の表を2倍して渡す。

```python
from library_codex.number_theory.MultiplicativeFunctions import MultiplicativePrefixSum

engine = MultiplicativePrefixSum(10)
counts = engine.prime_count_table()
prefix = [2 * x for x in counts]
answer = engine.run(prefix, lambda p, e: e + 1)
print(answer)
```

`answer`は27。1から10までの約数個数を足した整数で、各整数の約数個数のlistではない。

素数冪の値が`a*e+b*p`の場合は、個数と素数和の表を組み合わせる。

```python
mod = 469762049
engine = MultiplicativePrefixSum(10**11, mod)
a, b = 123, 456
counts = engine.prime_count_table()
sums = engine.prime_sum_table()
prefix = [(a * x + b * y) % mod for x, y in zip(counts, sums)]
answer = engine.run(prefix, lambda p, e: (a * e + b * p) % mod)
```

## Dirichlet積と逆算

`DirichletQuotientSeries`は乗法的とは限らない数列を扱う。各商までの累積和だけを渡すと、次の積の累積和を計算できる。

$$
h(n)=\sum_{ab=n}f(a)g(b),\qquad H(x)=\sum_{ab\le x}f(a)g(b).
$$

```python
from library_codex.number_theory.MultiplicativeFunctions import (
    DirichletQuotientSeries, dirichlet_multiply, dirichlet_divide,
)

n, mod = 10, 998244353
ones = DirichletQuotientSeries(n, mod=mod)
ones.data = [ones.value(i) for i in range(ones.size)]
divisors = dirichlet_multiply(ones, ones)
answer = divisors.data[divisors.index(10)]
recovered = dirichlet_divide(divisors, ones)
unit = DirichletQuotientSeries(n, [0] + [1] * (ones.size - 1), mod)
mobius = dirichlet_divide(unit, ones)
```

- `ones.data`: `[0, 1, 2, 3, 5, 10]`。定数列f(n)=1の累積和を、0と商の昇順に格納する。
- `divisors.data`: `[0, 1, 3, 5, 10, 27]`。各商までの約数個数の和。`answer`は27。
- `recovered.data`: `ones.data`と同じ。Dirichlet積を片方の数列で割って復元した累積和。
- `mobius.data`: `[0, 1, 0, -1, -2, -1]`を法で減らした列。各商までのMöbius関数の和。

`data`は各整数の値そのものではなく累積和。先頭に0を置き、残りを異なる商の昇順にする。積・除算は新しいseriesを返し、入力の表は変更しない。`result[i]`は表の添字iへのアクセスであり、整数iまでの累積和が欲しいときは`result[result.index(i)]`を使う。ただしiは商集合の要素に限る。

積・除算はともに`O(N^(2/3))`回の算術演算と`O(sqrt(N))`追加メモリ。除算には、除数の1番目の値の逆元計算が1回加わる。法を指定する場合はその値と法が互いに素でなければならない。法なしで厳密な除算が必要なら`Fraction`を使う。

## 総和用の表と返り値

- `counts[engine.index(x)]`: x以下にある素数の個数。
- `sums[engine.index(x)]`: x以下にある素数の和。法を指定した場合はその余り。
- `prefix[engine.index(x)]`: x以下の素数pについて、`f(p)`を足した値。`run`へ渡すのはこちら。
- `run(prefix, prime_power)`: 1からNまでの`f(i)`の総和。N=0なら0。

表は長さ`engine.size`。0番は未使用で、1番から正の商が降順に対応する。`index(x)`に渡せるxは、次の集合に属する値だけ。

$$
Q_N=\left\{\left\lfloor\frac{N}{i}\right\rfloor:1\le i\le N\right\}.
$$

## 仕組み

素数の集計表は商集合を使う篩で作る。素因数を小さい順に選び、以降に素数を1個掛ける分は表の差でまとめて加算する。さらに素因数を選べる場合だけ探索を続け、再帰は使わない。

個数・素数和の表はそれぞれ`O(N^(3/4)/log(N+2))`回の算術演算、`O(sqrt(N))`個の整数を使う。`run`の仕事量は、次のDと、callback1回の時間Tを用いて`O((D+1)(T+1))`。表作成の計算量と同じとは限らない。

$$
D=\#\{x:2\le x\le N,\ xP^+(x)\le N\},
$$

ここでP⁺(x)はxの最大素因数。Dは高々Nであり、実際には素数の集計で多くの整数をまとめられる。[公式入力でのPyPy測定](https://github.com/lif4635/harurun-s-library/blob/main/library_codex/docs/MULTIPLICATIVE_SUM_BENCHMARK.md)で、上限10¹¹と10¹³の検証範囲・時間を確認できる。

## 注意点

- `prime_power(p, e)`は同じ引数に同じ値を返す関数にする。呼出し回数や順序は保証しない。
- `mod=None`では剰余を取らない。巨大整数の計算時間は、値の桁数にも依存する。
- `prime_count_table`は法を指定していても個数をそのまま返す。
- `prime_sum_table`は法を指定すると途中の集計値も余りで保持する。法を省略した場合は正確な整数の和を返す。
- `DirichletQuotientSeries`の表は昇順、`MultiplicativePrefixSum`の表は降順。両者の配列をそのまま交換しない。

## 参考

- [Library CheckerのMin 25実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/sum_of_multiplicative_function/sol/min_25_sieve.cpp)
- [Nyaan's Libraryの乗法的関数の総和](https://nyaannyaan.github.io/library/multiplicative-function/sum-of-multiplicative-function.hpp.html)
- [Library CheckerのDirichlet積の区間分割](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/dirichlet_convolution_and_prefix_sums/sol/correct.cpp)
