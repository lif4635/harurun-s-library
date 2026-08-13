# 値域と順位を指定した区間重み和

## 主な機能

変更されない列について、位置の半開区間 $[l,r)$ と値の半開区間 $[a,b)$ を同時に指定し、条件を満たす要素の重みを合計します。

各位置 $i$ に検索用の値 $x_i$ と加算用の重み $w_i$ を持たせます。`range_sum(l, r, a, b)` が返す値は次の通りです。

$$
\sum_{l\le i<r,\ a\le x_i<b} w_i
$$

さらに、$x_i$ が小さい方から $k$ 個、または大きい方から $k$ 個を選んだときの重み和も求められます。前処理は $O(N\log S)$、各queryは $O(\log S)$ です。$S$ は異なる値の種類数です。

## 使い方

```python
from library_codex.range_query.WeightedWaveletMatrix import WeightedWaveletMatrix

values = [8, 2, 6, 2, 5]
weights = [10, 20, 30, 40, 50]
wm = WeightedWaveletMatrix(values, weights)

# index 1, 2, 3, 4 のうち、3 <= value < 8 を満たす重み
assert wm.range_sum(1, 5, 3, 8) == 80

# 同じ位置区間で、value が小さい方から3個の重み
assert wm.sum_k_smallest(1, 5, 3) == 110
```

`weights`を省略すると、各要素の値自身を重みとして使います。その場合は通常の区間値域和や、区間内の小さい方から $k$ 個の総和として利用できます。

## 注意点

- 選択順を決めるのは`values`であり、`weights`の大小ではありません。
- 重みは負でも構いません。
- 同じ値が境界に並ぶ場合、`sum_k_smallest`は元のindexが小さい要素から選びます。
