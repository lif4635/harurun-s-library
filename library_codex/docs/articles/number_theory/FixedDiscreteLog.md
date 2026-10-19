# 固定した素数と原始根での離散対数

素数と原始根が同じ問い合わせを大量に処理するときに使う。前計算した表を共有し、1回の離散対数をO(1)で求める。

## 主な機能

`log = FixedDiscreteLog(prime, root)`で前計算し、`log(value)`で次の条件を満たす最小の非負整数を得る。

$$
\mathrm{root}^{x}\equiv \mathrm{value}\pmod{\mathrm{prime}}.
$$

`prime`は2以上10の9乗以下の素数、`root`はその原始根を指定する。合成数の法や原始根でない底を使う場合は、既存の`discrete_log`を使う。

## 使い方

```python
from library_codex.number_theory.FixedDiscreteLog import FixedDiscreteLog

log = FixedDiscreteLog(17, 3)
exponent = log(13)
identity = log(1)
missing = log(0)
```

- `exponent`は`4`。3の4乗を17で割った余りは13。
- `identity`は`0`。原始根の0乗は1。
- `missing`は`-1`。原始根の冪は0にならない。
- 負数や法以上の値も正規化する。`log(-4)`と`log(30)`も`4`。

## 仕組み

小さい素数の離散対数を、探索表を共有するbaby-step giant-stepでまとめて求める。その後、小さい整数の対数表を積と剰余の関係から埋める。

問い合わせの値は、小さい整数同士の比として表す。Farey近似の表で分母と符号付きの分子を見つけ、それぞれの離散対数を引くことで答える。浮動小数点は使わない。

Pを法、Rを√P以下の素数の個数とすると、構築は期待O(P^(2/3) + √(P R))時間・一時メモリ。構築後に保持する表はO(P^(2/3))メモリ。整数演算とdictの探索をそれぞれO(1)・期待O(1)として数える。

## 注意点

- 前計算は軽くないため、同じ法・原始根でオブジェクトを使い回す。
- 素数と原始根は構築時に検査する。不正な指定は`ValueError`。
- `prime`と`root`を構築後に書き換えない。別の組を使うときは別オブジェクトを作る。
- `repr(log)`には法と原始根だけを表示し、大きな前計算表は出力しない。

## 参考

[Library Checker公式実装のFarey近似](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/number_theory/discrete_logarithm_fixed_mod/bsdsdblib/numtheo/farey_tech.hpp)と、複数の離散対数で探索表を共有する方法を参考にしている。
