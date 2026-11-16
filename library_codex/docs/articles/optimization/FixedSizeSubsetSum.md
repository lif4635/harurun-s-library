# 異なる値をk個選ぶ部分和

## 主な機能

整数集合からちょうどk個の異なる値を選び、作れる和を重複なく列挙します。選び方の個数を法で数える`fps998/SubsetSum`とは別の問題です。

選ぶ個数と選ばない個数の小さい方をk'として計算します。組合せ数が32768以下なら列挙、等差数列なら和の範囲を直接生成、それ以外は個数ごとのbitset DPを使います。平行移動と最大公約数で、扱う和の幅を縮めます。

## 使い方

```python
from library_codex.optimization.FixedSizeSubsetSum import fixed_size_subset_sums

assert fixed_size_subset_sums([1, 3, 5, 7], 2) == [4, 6, 8, 10, 12]
assert fixed_size_subset_sums([2, 2, 3], 2) == [5]
assert fixed_size_subset_sums([-3, 2, 8], 2) == [-1, 5, 10]
assert fixed_size_subset_sums([], 0) == [0]
```

- 返り値は作れる和を昇順に並べた整数listです。
- 入力は集合です。`[2, 2, 3]`から2個選んでも、2を2回選ぶ和4は含みません。
- kが異なる値の個数を超えれば空listです。k=0なら0だけです。

## 注意点

- 重複除去後の値数をN、圧縮後の大きいk'個の和をH、出力数をRとします。bitset DPはO(Nk' ceil((H+1)/w)+H+R)時間、O(k' ceil((H+1)/w)+N+R)空間です。wは多倍長整数の内部桁のbit数です。
- 圧縮後の和の範囲に依存します。ばらばらの巨大整数が多い入力には適しません。
- 負数も含められます。入力は変更しません。

## 参考

[qandori/cp-libraryの個数指定部分和](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/math/fixed_size_subset_sum.hpp)の集合としての仕様・補集合・gcd圧縮を参照しています。一般の場合はこちらではbitset DPを使い、参照先の多法NTTと同じ実装ではありません。
