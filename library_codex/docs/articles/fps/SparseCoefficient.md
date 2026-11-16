# 逆数・log・exp・冪の遠い係数

## 主な機能

低次数の多項式から、展開後の指定した1係数を求めます。返り値は係数listではなく、modの余りの整数1個です。

- `inv_coeff(f, k)`は1/fのk次係数です。
- `log_coeff(f, k)`はlog(f)のk次係数です。定数項は1です。
- `exp_coeff(f, k)`はexp(f)のk次係数です。定数項は0です。
- `pow_coeff(f, exponent, k)`は非負整数冪のk次係数です。定数項0も扱います。

## 使い方

```python
from library_codex.fps.SparseCoefficient import inv_coeff, log_coeff, exp_coeff, pow_coeff

assert inv_coeff([1, -1], 10**18) == 1
assert log_coeff([1, -1], 2) == 499122176
assert exp_coeff([0, 1], 2) == 499122177
assert pow_coeff([0, 0, 2, 3], 5, 11) == 240
assert exp_coeff([0, 0, 1], 999999) == 0
```

最後の例ではxの偶数乗しか出ないため、奇数次の係数は0です。非零の次数の最大公約数で変数を圧縮できる場合は、圧縮後に計算します。

## 仕組みと計算量

逆数はBostan–Mori、logは微分後の有理式の係数取得を使います。入力の有効次数d、取得次数Kに対し、O(M(d)log(K+2))時間・O(d)空間です。M(d)はd項程度の畳み込み時間です。

expと冪では係数比較により、一次式の係数を持つ漸化式ができます。expの場合は次の形です。

$$
n g_n=\sum_{j=1}^{d}j f_jg_{n-j}.
$$

圧縮後のdが8以下でKが200万を超える場合、一次式行列の平方分割を使います。B=ceil(sqrt(K))に対しO(d³ M(B)log(B+2))時間・O(d²B+B log(B+2))空間です。それ以外は、既存の疎漸化式でKまで進めます。非零項数sに対してO((K+1)(s+1))時間・O(K+d)空間です。

100万次の比較では平方分割が既存の疎漸化式より遅かったため、小さいKへ一律には適用しません。単項取得でも、常にK未満のメモリで計算するわけではありません。

## 注意点

- 入力は次数順の係数listです。非零項数だけでなく、最後の非零項の次数dも重要です。
- modは素数とします。log・expはK<mod、冪は先頭の零によるシフト後のK<modが基本条件です。素数判定は行いません。
- 高次数の疎入力では平方分割の行列が大きくなるため、通常の疎漸化式を使います。極端に遠い係数での時間・メモリに注意してください。
- 全係数が必要なら`SparseFormalPowerSeries`を使います。単項用の重い依存をprefix用moduleへ追加しないため、別moduleにしています。

## 参考

[kemunikuの疎FPS](https://github.com/kemuniku/cplib/blob/f835598fec8e14039cf654a67f0244e0a654d035/src/cplib/fps/sparse_formal_power_series.nim)の単項取得を参照しています。SIMDやNim固有の最適化は使用していません。
