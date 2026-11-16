# 添字の大小を制限する畳み込み

## 主な機能

左の添字が右の添字より小さい係数対だけを足します。

$$c_k=\sum_{i+j=k,\ i<j}a_i b_j\pmod{998244353}.$$

時間順の2列で「前の位置と後の位置」の寄与だけが必要な場合に使えます。通常の畳み込みから対角項を引くだけでは、向きの異なる寄与を区別できません。

最大列長をLとしてO(L log²(L+2))時間・O(L)追加空間です。添字区間を二分し、左半分のaと右半分のbを既存NTTで畳み込みます。再帰は使いません。

## 使い方

```python
from library_codex.convolution.OrderedConvolution import ordered_conv

assert ordered_conv([1, 2, 3], [4, 5, 6]) == [0, 5, 6, 12, 0]
assert ordered_conv([1], [4, 5, 6]) == [0, 5, 6]
assert ordered_conv([], [4, 5]) == []
```

- 長さ`len(a)+len(b)-1`のlistです。どちらかが空なら空listです。
- 添字の和がkになる寄与が`result[k]`へ入り、該当する組がなければ0です。
- 同じ添字の積は含みません。入力は変更しません。

## 注意点

- 法は998244353固定です。整数としての正確な係数畳み込みではありません。
- 内部の各NTT長は2の23乗以下である必要があります。超過時はエラーになります。

## 参考

[qandori/cp-libraryのordered convolution](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/convolution/ordered_convolution.hpp)の分割方法を参照しています。
