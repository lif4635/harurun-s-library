# 合成数の法での二項係数

## 主な機能

`ArbitraryModBinomial(mod)`は、素数とは限らない固定の法で二項係数を繰り返し求める。nは法より大きくてもよい。

$$\binom{n}{k}\bmod\mathrm{mod}$$

- `ArbitraryModBinomial`: 法を素数冪へ分解し、各結果を中国剰余定理で合成するclass。
- `PrimePowerBinomial(prime, exponent)`: 法が素数冪と分かっているときに直接使えるclass。
- `LargePrimeFactorial(mod)`: 大きい素数の法で、階乗と二項係数を平方根程度のサイズの多項式演算で求めるclass。

素数冪の法をM、底の素数をpとすると、`PrimePowerBinomial.C`は表の拡張を除いてO(log_p(n+1))時間。階乗表は必要になった部分だけ増やし、最大O(M)領域を使う。法が大きい場合に必ず省メモリになるわけではない。

## 使い方

```python
from library_codex.combinatorics.ArbitraryBinomial import ArbitraryModBinomial, PrimePowerBinomial

table = ArbitraryModBinomial(12)
assert table.C(10, 3) == 0
assert table.C(10, 4) == 6
assert table.C(10**18, 1) == 10**18 % 12

table = PrimePowerBinomial(2, 3)
assert table.C(10, 4) == 2
```

返り値は`0`以上、法未満の整数。nが負、kが負、kがnを超える場合は0を返す。法が1の場合はすべて0。

## 仕組み

素数pの倍数を取り除いた階乗と、その逆元の表を持つ。n・k・n-kをpで割りながら、表の積と繰り上がり数から素数冪での剰余を求める。逆元を毎回計算せず、法の合成に使うCRT係数も構築時に計算しておく。

## 注意点

- `prime`は素数、`exponent`は1以上。`PrimePowerBinomial`自身は素数判定をしない。
- `ArbitraryModBinomial`の法は正で、素因数分解の保証範囲である64ビット以内を使う。
- 大きな素数冪では表が非常に大きくなることがある。巨大な法かつkが小さい用途の専用実装ではない。
- 素因子が2000000を超え、指数が1なら`LargePrimeFactorial`を使う。大きい合成数の素数冪にはこの省メモリ処理を使わない。
- `LargePrimeFactorial.factorial(n)`は範囲外のnに0を返す。計算済みのnはキャッシュする。
- 初回や表の拡張時の負担は、問い合わせごとの計算量に含めて考える。
