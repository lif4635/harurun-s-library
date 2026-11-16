# 過去の森から分岐する辺更新と経路積

## 主な機能

辺の追加・削除、頂点値の代入、経路積、経路上のk番目の頂点を扱います。任意の過去版から分岐でき、変更前の森も照会できます。

`prod(u, v)`は、uからvへ順に頂点値を畳み込みます。結合則と単位元があれば、文字列連結など非可換の演算も使えます。両端の頂点値を含みます。

## 使い方

```python
from library_codex.tree.PersistentLinkCutTree import PersistentLinkCutTree

t = PersistentLinkCutTree([1, 2, 4], edges=[(0, 1)])
v1, linked = t.link(1, 2, 0)
assert linked
v2, total = t.prod(0, 2, v1)
assert total == 7
v3 = t.set(1, 20, v2)
v4, total = t.prod(0, 2, v3)
assert total == 25
v5, total = t.prod(0, 2, v2)
assert total == 7
v6, connected = t.same(0, 2, 0)
assert not connected
v7, vertex = t.jump(0, 2, 1, v4)
assert vertex == 1
```

- `set`は新しい版番号を返します。
- `link`・`cut`は`(新しい版番号, 辺を変更できたか)`を返します。閉路を作るlinkや、存在しない直接辺へのcutはFalseです。
- `prod`・`same`・`path_size`・`jump`は`(探索後の版番号, 答え)`を返します。問い合わせでも内部の木を調整するため、版が増えます。
- `path_size`の答えは頂点数です。`jump`の答えは頂点番号で、経路の範囲外なら-1です。別成分への経路照会はValueErrorです。
- `get`・`tolist`は頂点値だけを読み、新しい版を作りません。`tolist`の順序は頂点番号順です。

## 速度の条件

返された版を次の操作へ引き継ぐ場合、splayの償却が働きます。N頂点へのQ操作の合計はO((N+Q)log²(N+2))で、opをO(1)とした評価です。初期の長い経路を初めて辿る操作は重くなることがあります。

毎回同じ古い未調整の版に戻る場合、この償却は使えません。1操作最悪O(N log(N+2))時間・追加保存領域です。過去版への反復照会を含む比較では、既存LinkCutTreeを全コピーする方式より遅くなるケースもあります。

## 仕組み

頂点状態は整数IDの配列で保持し、版ごとに永続配列で対応先を管理します。1操作中に触れた頂点だけを作業用配列へ読み、終了時に保存します。頂点ごとのNodeクラスや再帰は使いません。

## 注意点

- 初期版は0。`version`を省略すると、問い合わせも含め最後に作成した版を使います。
- opは引数を書き換えず、値も外から変更しないでください。
- 過去版の保存と経路更新を同時に扱うため、通常のLinkCutTreeより保存量が増えます。過去版が不要なら通常版を使います。
- 経路一括作用・部分木集約・LCAは、この版には含めていません。
- 読み出した版や内部記録は自動破棄しません。`node_count()`で永続配列と頂点記録の個数を確認できます。

## 参考

[qandの永続Link-Cut Tree](https://github.com/qandori/cp-library/blob/ceec97a52d734d23f762b9c5e322b2b53df0cf9e/tree/persistent_link_cut_tree.hpp)の操作中cacheと永続配列への保存、返却版を引き継ぐ契約を参照しています。
