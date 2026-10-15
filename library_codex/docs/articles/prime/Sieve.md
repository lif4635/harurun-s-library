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

- `prime_count(number)`: 素数を列挙せず、その個数を求める。
- `count_square_free(number)`: 1以上number以下で、1以外の平方数を因子に持たない整数を数える。
- `sum_totient(limit)`: 1からlimitまでのφ関数の総和。線形ふるいを作るため O(N) 時間・メモリを使う。

## 注意点

- `limit`を含む。`limit < 2`なら素数は0個。
- `limit >= 0`、`step > 0`、`0 <= offset < step`を満たす整数を渡す。
- 素数だけ欲しいなら`LinearSieve`は不要。最小素因数などの表も必要なときに使う。
- `factor_count(1)`は`[]`。前計算範囲外の値は渡せない。
