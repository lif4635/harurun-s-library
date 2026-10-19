# 素数列挙と整数の前計算

上限以下の素数を列挙する。整数を繰り返し素因数分解したい場合には、最小素因数・Möbius関数・φ関数の表も作れる。

## 主な機能

- `prime_sieve(limit)`: 上限以下の素数をすべて昇順で返す。
- `enumerate_primes(limit, step, offset)`: 素数の総数と、素数列を指定間隔で間引いたリストを返す。返さない素数を大きなリストに保持しない。
- `LinearSieve(limit)`: 各整数の最小素因数・Möbius関数・φ関数を O(N) 時間・メモリで前計算するclass。`factor_count(value)`で範囲内の整数を素因数分解できる。

素数列挙は O(N log log N) 時間。区間ごとに奇数だけをふるい、作業領域は O(√N + B)、返す素数K個の保存に O(K) を使う。Bは区間内の奇数の数で、既定は262144以上・√N以上。

## 使い方

```python
from library_codex.prime.Sieve import prime_sieve, enumerate_primes, LinearSieve

assert prime_sieve(20) == [2, 3, 5, 7, 11, 13, 17, 19]
count, selected = enumerate_primes(30, step=3, offset=1)
assert count == 10
assert selected == [3, 11, 19]

sieve = LinearSieve(100)
assert sieve.factor_count(72) == [(2, 3), (3, 2)]
assert sieve.phi[12] == 4
assert sieve.mobius[6] == 1
```

- `count`: 間引く前の、上限以下の素数の総数。
- `selected[i]`: 素数列の`offset + step * i`番目。たとえば上の例は1・4・7番目の素数。
- `factor_count`の各要素: `(素因数, 指数)`。素因数の昇順で並ぶ。

素数列を次で定める。

$$
p_0=2,\quad p_1=3,\quad p_2=5,\quad \ldots
$$

`step`は整数の間隔ではなく、素数の番号の間隔。`step=1, offset=0`なら全素数を返す。

## 個数や総和だけ欲しい場合

- `prime_count(number)`: 素数を列挙せず、その個数を求める。O(N^(3/4) / log N) 時間、O(√N) メモリ。
- `count_square_free(number)`: 1以上number以下で、1以外の平方数を因子に持たない整数を数える。O(N^(2/5) log log N) 時間、O(N^(2/5)) メモリ。
- `sum_totient(limit, mod=None)`: 1からlimitまでのφ関数の総和。O(N^(2/3) log log N) 時間、O(N^(2/3)) メモリ。上限までの表は作らない。

```python
from library_codex.prime.Sieve import prime_count, count_square_free, sum_totient

assert prime_count(10**11) == 4118054813
assert count_square_free(10) == 7
assert count_square_free(10**12) == 607927102274
assert sum_totient(10) == 32
assert sum_totient(10, mod=12) == 8
assert sum_totient(10**10, mod=998244353) == 866849765
```

φ(i)は、1以上i以下でiと互いに素な整数の個数。返り値は次の総和で、`mod`を指定した場合だけその余りを返す。素数でない法も使える。

$$
S(N)=\sum_{i=1}^{N}\varphi(i),\qquad \varphi(1)=1
$$

たとえば、1以上N以下の整数a, bについて、互いに素な順序付きペアの個数は `2 * sum_totient(N) - 1` で求められる。

総和の計算では、小さい値だけをふるいで前計算し、残りを次の式で求める。同じ商になる項をまとめ、必要な商の総和を小さい順に計算するため、再帰や辞書は使わない。

$$
S(N)=\frac{N(N+1)}{2}-\sum_{d=2}^{N}S\left(\left\lfloor\frac{N}{d}\right\rfloor\right)
$$

## 平方因子を持たない整数の個数

`count_square_free(10)`が数えるのは`1, 2, 3, 5, 6, 7, 10`。`4, 8, 9`は4または9で割り切れるため含めない。上限は含み、0以下なら0を返す。返り値は剰余を取らない整数。

Möbius関数を使うと、求める個数は次の式になる。

$$
Q(N)=\sum_{d=1}^{\lfloor\sqrt N\rfloor}\mu(d)\left\lfloor\frac{N}{d^2}\right\rfloor
$$

平方根までの表は作らず、小さいdだけをふるう。残りは同じ商になる範囲をMöbius関数の累積和でまとめる。[Pawlewiczの計数法](https://arxiv.org/abs/1107.4890)の基本版を用いており、論文後半のブロック分割による省メモリ版ではない。

たとえば上限が10^18でも、作る表は約1585万要素。0から上限までの判定表や、対象の整数一覧を返す関数ではない。

## 注意点

- `limit`を含む。`limit < 2`なら素数は0個。
- `limit >= 0`、`step > 0`、`0 <= offset < step`を満たす整数を渡す。
- 素数だけ欲しいなら`LinearSieve`は不要。最小素因数などの表も必要なときに使う。
- `factor_count(1)`は`[]`。前計算範囲外の値は渡せない。
