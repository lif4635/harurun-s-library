# 区間のk番目をまとめて求める

## 主な機能

値を更新しない配列と、半開区間・順位の問い合わせをまとめて渡し、各区間のk番目に小さい値を求めます。負数や重複を含む配列も使えます。

N要素、Q問い合わせ、異なる値の個数σに対し、期待O(N+σ log(σ+1)+(N+Q)log(σ+1))時間、O(N+Q)追加空間です。昇順・降順の配列はO(N+Q)で処理します。

## 使い方

```python
from library_codex.range_query.OfflineRangeKth import offline_range_kth

a = [8, -2, 8, 3, 1]
queries = [(0, 5, 0), (0, 5, 3), (1, 4, 1)]
assert offline_range_kth(a, queries) == [-2, 8, 3]
assert a == [8, -2, 8, 3, 1]
```

- 問い合わせは`(left, right, k)`です。区間は半開区間`[left, right)`、`k=0`なら最小値です。
- 返り値は問い合わせ順のlistです。配列内の添字ではなく、選ばれた値そのものを返します。
- 同値も別々の要素として数えます。最初の区間の昇順列は`[-2, 1, 3, 8, 8]`なので、順位3・4はいずれも8です。

## 仕組み

値を座標圧縮し、上位bitから0側・1側へ分けます。各段で全問い合わせの範囲と順位も移し、次の段へ進みます。処理済みの段の情報は保持しません。

`WaveletMatrix`は構築後に問い合わせを追加でき、頻度・前後の値なども求められます。この関数はk番目の一括処理だけに絞ったものです。既存の`WaveletMatrix`はbit圧縮して保持しているため、この関数が常に省メモリになるとは限りません。

## 注意点

- 配列の値はhash可能で全順序比較できることが必要です。NaNは使えません。
- 問い合わせ区間は空にできません。範囲外や不正な順位は`ValueError`です。
- 空の問い合わせ列には空listを返します。
- 入力配列と問い合わせは変更しません。問い合わせはgeneratorでも渡せます。

## 参考

[qandori/cp-libraryの静的区間k番目](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/data_structure/offline_range_kth_smallest.hpp)と、そのscalar処理を参照しています。AVX2命令は使わず、通常のPython配列で各段をまとめて処理します。
