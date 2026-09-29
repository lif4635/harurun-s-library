# 整数multisetとXOR最小値

## 主な機能

重複を含む非負整数を管理する。追加・削除・順位・XORの相手の検索は、ビット幅Bに対してO(B)。全要素へのXORはO(1)。

分岐しない一本道を省略する。異なる値がD個あるとき、生きているノードは空なら0個、それ以外は2D−1個。ノードごとのclassは作らず、整数IDと配列だけを使う。削除した領域を再利用するため、確保領域は過去に同時保持した異なる値の最大数に比例する。

## 使い方

```python
tree = BinaryTrie(30)
tree.add(3, 2)
tree.add(10)
assert tree.tolist() == [3, 3, 10]
assert tree.kth(1) == 3
assert tree.bisect_left(10) == 2
assert tree.xor_min(9) == 10
assert tree.xor_min(9) ^ 9 == 3
assert tree.discard(3) == 1
tree.xor_all(1)
assert tree.tolist() == [2, 11]
```

## 注意点

- 登録値と全体XORのマスクは、0以上2**B未満。
- `xor_min(x)`・`xor_max(x)`はXORした結果ではなく、相手となる登録値を返す。
- `kth`は重複を含む順位。空の最小値・最大値取得と範囲外の順位はIndexError。
- 値に重みを持たせて区間集約したい場合は`BinaryTrieMonoid`を使う。通常版にはモノイド用の値や演算を持たせていない。
- 密な連続整数を構築するだけの場合は、非圧縮版より遅いことがある。圧縮版は疎なキーや削除・再挿入を含む操作を重視している。
