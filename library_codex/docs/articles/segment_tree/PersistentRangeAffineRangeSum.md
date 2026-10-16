# 履歴を残す区間更新と区間コピー

配列の過去の状態を残したまま、区間のアフィン変換・別の版からの区間コピー・区間和を処理する。

## 主な機能

`PersistentRangeAffineRangeSum(values, mod=998244353)`は、初期配列を版0として保持するclass。`apply`と`copy`は元の版を変更せず、新しい版番号を返す。どの版からでも分岐できるので、過去の状態から別の更新を試したり、一部分だけ以前の値へ戻したりできる。

アフィン変換は区間内の各値を次の式で置き換える。倍率0なら区間代入、倍率1なら区間加算になる。

$$
a_i \gets (\mathrm{multiplier}\,a_i+\mathrm{addend})\bmod\mathrm{mod}
$$

配列長をNとすると、構築はO(N)時間・メモリ。更新・区間コピー・区間和はいずれもO(log N)。1回の更新で追加する領域もO(log N)で、配列全体をコピーしない。Nが0または1ならO(1)。

## 使い方

```python
from library_codex.segment_tree.PersistentRangeAffineRangeSum import PersistentRangeAffineRangeSum

tree = PersistentRangeAffineRangeSum([1, 2, 3, 4])
v1 = tree.apply(1, 4, 2, 1, version=0)
v2 = tree.copy(2, 4, source=0, version=v1)
assert tree.tolist(0) == [1, 2, 3, 4]
assert tree.tolist(v1) == [1, 5, 7, 9]
assert tree.tolist(v2) == [1, 5, 3, 4]
assert tree.prod(1, 4, version=v2) == 12
```

- `v1`: 版0の半開区間`[1, 4)`を2倍して1を足した版の番号。
- `v2`: 版v1の半開区間`[2, 4)`だけを、版0の同じ位置の値へ戻した版の番号。
- `prod(1, 4, version=v2)`: 版v2の添字1・2・3の合計。返るのは版番号ではなく、modで割った余り。
- `tolist(version)`: 指定版の配列のコピー。確認用でO(N)かかる。

## 仕組み

変更した区間の境界にある経路だけを作り直し、変わらない部分は既存の木と共有する。遅延中の変換を子への参照と一緒に持つため、変換を下ろすだけのために子ノードを複製しない。版を読む操作ではノードを追加しない。

## 注意点

- 版番号はこのinstanceの中だけで有効。0が初期状態で、更新のたびに1つ増える。`version`省略時は最後に作った版を使う。
- `copy`は同じ添字の区間をコピーする。別位置への移動や、別instanceからのコピーは扱わない。
- `prod`・`get`・`tolist`は新しい版を作らず、最後に作った版も切り替えない。
- 値と変換係数はmodで正規化する。modは正の整数で、素数でなくてもよい。
- 履歴を削除する操作はない。更新回数をQとして、保持メモリはO(N + Q log(N+2))。

## 参考

- [maspyの永続遅延セグメント木](https://maspypy.github.io/library/ds/segtree/dynamic_lazy_segtree.hpp)
- [Library Checkerの問題](https://judge.yosupo.jp/problem/persistent_range_affine_range_sum)
