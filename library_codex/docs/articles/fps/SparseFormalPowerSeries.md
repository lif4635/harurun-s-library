# 非零項が少ない形式的冪級数

## 主な機能

非零係数の少ない列について、逆数・除算・exp・log・整数冪を求めます。打ち切り次数をN、入力の非零項数をKとして、基本演算はO(NK)時間で計算します。入力自体は次数順の通常の係数listです。

`sparse_differential(A, B, degree, constant=1)` は次の微分方程式を満たす係数列を求めます。

$$B(x)F'(x)=A(x)F(x),\qquad F(0)=\mathrm{constant}.$$

A、Bの非零項数をそれぞれKa、Kbとすると、打ち切り後の入力走査を含めO(N(Ka+Kb+1))時間、O(N)追加空間です。F自体が密でも、AとBが疎なら使えます。

## 使い方

```python
from library_codex.fps.SparseFormalPowerSeries import sparse_differential, sparse_inverse

assert sparse_inverse([1, -1], 6) == [1, 1, 1, 1, 1, 1]
assert sparse_differential([1], [1, -1], 6) == [1, 1, 1, 1, 1, 1]
assert sparse_differential([3], [1, -1], 6) == [1, 3, 6, 10, 15, 21]
```

3つ目は `(1-x)^(-3)` の展開です。返り値は長さdegreeのlistで、`result[i]` がxのi乗の係数です。全係数はmodの余りです。

## 仕組み

微分方程式の係数を比較すると、既に求めた係数だけから次の係数を計算できます。

$$nB_0 F_n=\sum_{j=0}^{n-1} A_jF_{n-1-j}-\sum_{j=1}^{n-1}B_j(n-j)F_{n-j}.$$

例えば `F=exp(P/Q)` なら、Aに `P'Q-PQ'`、Bに `Q^2` を与えます。これらが疎でなくなる場合は、通常のFPS演算の方が適しています。

## 注意点

- differential版ではmodを素数とし、`degree <= mod`、`B[0] != 0 mod mod` を満たしてください。素数判定は行いません。
- `constant=0` なら全係数が0になります。
- 入力を疎辞書にするAPIではありません。長い係数listの不要な末尾は渡さなくて構いません。
- 密な入力でこの方法を使うとO(N^2)になります。mod 998244353の密な演算は `fps998/FPS.py` を使います。

