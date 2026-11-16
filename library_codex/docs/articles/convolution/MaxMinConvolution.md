# max-min・min-max畳み込み

## 主な機能

2つを組み合わせた品質が「弱い側」で決まるとき、添字の和ごとに最も良い組合せを求めます。aとbが使用量別の性能なら、合計使用量ごとの最大のボトルネック性能が得られます。

$$c_k=\max_{i+j=k}\min(a_i,b_j).$$

逆に、組合せの負担が「大きい側」で決まるときには次を使います。

$$d_k=\min_{i+j=k}\max(a_i,b_j).$$

入力長の合計をL、多倍長整数の内部桁のbit数をwとして、O(L log(L+2)+L ceil(L/w))時間・O(L)空間です。NTTを使ったO(L sqrt(L log L))方式と同じ計算量ではありません。

## 使い方

```python
from library_codex.convolution.MaxMinConvolution import max_min_conv, min_max_conv

assert max_min_conv([3, 1], [2, 4]) == [2, 3, 1]
assert min_max_conv([3, 1], [2, 4]) == [3, 2, 4]
assert max_min_conv([], [1]) == []
```

- 長さ`len(a)+len(b)-1`のlistです。空列を含めば空listです。
- 各要素は入力の値のいずれかです。負数や重複も扱え、剰余を取りません。
- min-plus畳み込みとは異なり、組合せの値に加算を使いません。

## 仕組み

max-min版は値の大きい順に添字を有効にします。新しい添字iに対し、反対側の有効添字のbit集合をiだけshiftすると、作れる添字の和が分かります。初めて作れた和に現在の値を入れると、それが最適値です。min-max版は小さい順で同じ処理を行います。

## 注意点

- 値は相互に比較でき、順序が一貫している必要があります。NaNは使えません。
- 最大規模でNTT方式より速いことは保証しません。測定条件は比較記録へ残します。

## 参考

[qandori/cp-libraryのmax-min畳み込み](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/convolution/max_min_convolution.hpp)を仕様と比較候補として参照しています。こちらは多倍長整数による実装です。
