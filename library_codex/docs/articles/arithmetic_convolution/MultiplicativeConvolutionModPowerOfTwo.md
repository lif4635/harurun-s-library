# 2の冪を法とする乗法畳み込み

剰余ごとの出現回数や重みを2列与え、1つずつ選んだ積の剰余ごとに集計する。添字の法は入力列の長さ、係数の法は998244353。

## 主な機能

同じ長さLの整数列から、次の長さLの列を求める。Lは2の冪。

$$
c_k=\sum_{\substack{0\le i,j<L\\ij\equiv k\pmod L}}a_i b_j\pmod{998244353}.
$$

通常の畳み込みのように添字を足すのではなく、掛ける。0や偶数も対象で、逆元を持つ奇数だけに限定しない。時間はO(L log(L+1))、追加メモリはO(L)。

## 使い方

```python
from library_codex.arithmetic_convolution.MultiplicativeConvolutionModPowerOfTwo import multiplicative_convolution_pow2

a = [0, 1, 1, 0]
b = [0, 0, 1, 1]
counts = multiplicative_convolution_pow2(a, b)
```

`a`は数1・2を各1個、`b`は数2・3を各1個持つ。積は2・3・4・6で、4で割った余りは2・3・0・2。したがって`counts`は`[1, 0, 2, 1]`となる。

## 仕組み

添字を2で割れる回数ごとに分け、奇数部分を符号と5の冪で表す。各部分列をNTTで変換してから、積に対応する部分をまとめる。小さい法への折り返しには変換済み配列の一部を再利用し、組ごとのNTTは行わない。

## 注意点

- 入力2列は同じ長さで、長さは`1, 2, 4, ...`のいずれか。空列は不可。
- 負の係数も扱える。返り値は各係数を998244353で正規化した新しいlistで、入力は変更しない。
- 係数の法を変更する引数はない。長さの上限は`2**25`だが、大きい列ではメモリにも注意する。
- 素数を添字の法とする場合は`MultiplicativeConvolutionModPrime`を使う。

## 参考

[Library Checker公式解答](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/mul_mod2n_convolution/sol/correct.cpp)の分解と変換の再利用を参考にしている。
