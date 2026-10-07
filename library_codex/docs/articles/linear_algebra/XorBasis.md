# XORで作れる値の集合

整数をいくつか選んでXORしたとき、どの値を作れるかを基底で管理する。

## 主な機能

- `XorBasis(values)` — 非負整数の列から構築するclass。重複・0・ほかの値のXORで作れる値は、独立した基底として数えない。
- `insert(value)` — 作れる値の集合へvalueを追加する。集合が広がったときだけTrue。
- `contains(value)` — 登録値そのものに限らず、それらのXORで作れるかを判定する。
- `kth_smallest(index)`・`rank(value)` — 作れる値を昇順に並べたときの値・位置を取得する。
- `intersection(other)` — 両方で作れる値だけを表す、新しいXorBasisを返す。

基底数D、整数のビット幅B、多倍長整数の1桁の幅wに対し、通常の検索・追加は `O(D ceil(B/w))`。集合の共通部分は基底数D₁、D₂に対し `O((D₁+D₂)^2 ceil(B/w))`。作れる値の個数は2のD乗でも、全列挙はしない。

## 使い方

```python
from library_codex.linear_algebra.XorBasis import XorBasis

a = XorBasis([3, 5])
b = XorBasis([6, 8])
common = a.intersection(b)
assert a.contains(6)
assert common.tolist() == [6]
assert len(common) == 1
assert [common.kth_smallest(i) for i in range(2)] == [0, 6]
assert common.rank(6) == 1
```

- aで作れる値: 0, 3, 5, 6。
- bで作れる値: 0, 6, 8, 14。
- 共通部分: 0, 6。返り値の基底は6だけで、0は基底へ入れない。
- `len(common)`: 作れる値の個数ではなく、独立な基底の本数。
- `tolist()`: 基底を昇順で返すコピー。作れる値すべての列ではない。

## 注意点

- `intersection`は両方の入力を変更しない。返り値には通常の検索・追加も使える。
- `rank(value)`は値の昇順での位置。空間の次元を知りたいときは `len(basis)`。
- 作れない値のrank、範囲外のkthは-1。共通部分が0だけなら空の基底になる。
- `minimum(xor)`・`maximum(xor)`・`xor_kth(xor, index)`は、作れる各値にxorを掛けた集合での検索。
