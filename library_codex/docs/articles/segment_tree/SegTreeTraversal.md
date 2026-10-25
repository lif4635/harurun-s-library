# 子孫を参照しながらマージするセグメント木

## 主な機能

配列の一点置換と、半開区間の集約を行うclass。左の集約値だけでは結合できず、左の部分木へ降りて追加情報を調べたい場合に使う。

利用側は結合処理`merge`を1つ書く。配列の確保、葉の配置、構築、更新する祖先の選択、問い合わせ区間の分割はclassが担当する。

高さhの部分木に対する結合がO(h+1)なら、構築はO(N)、一点更新と区間取得はO(log² N)。結合がO(1)なら更新・取得はO(log N)。ノードごとのclassは作らない。

## 使い方

```python
from library_codex.segment_tree.SegTreeTraversal import SegTreeTraversal

def merge(data, left_node, right_value):
    return data[left_node] + right_value

tree = SegTreeTraversal(merge, "", ["a", "b", "c", "d", "e"])
answer = tree.prod(1, 4)
tree.set(2, "X")
changed = tree.prod(1, 4)
whole = tree.all_prod()
```

- `answer`は`"bcd"`、`changed`は`"bXd"`、`whole`は`"abXde"`。
- 第2引数の`""`は空区間を表す値。空区間の`prod`はこの値を返す。
- `set`に渡すのは元の配列の添字。内部の葉番号への変換や、変更後の再構築は不要。
- `get(i)`は現在の1要素、`tolist()`は現在の要素列を返す。

この文字列連結は呼出し方だけの小さい例。文字列の長さに比例する時間がかかるので、大きな文字列を各ノードに保存する用途には向かない。

## mergeに書くこと

`merge(data, left_node, right_value)`には、左のノード番号と右の集約値が渡される。

- `data[left_node]`は左の区間の集約値。
- `left_node`が内部ノードなら、左右の子は`2*left_node`と`2*left_node+1`。必要な側の子へ降り、保存値を参照できる。葉は`len(data)//2`番以降。
- `right_value`は右の区間の集約値。ノード番号ではない。
- 左の区間の後ろに右の区間をつないだ、新しい集約値を返す。親への保存はclassが行う。

構築・一点更新・区間取得のすべてで、この同じ`merge`を使う。`data`や引数の値は書き換えない。返す値の表現は自由だが、同じ列をどのように分割しても、集約結果の意味が一致する必要がある。

`right_value`は、問い合わせ中に複数区間を結合した途中結果の場合もある。そのため、子孫を参照できるのは左側だけ。右側の子孫が必要な処理には、そのまま使えない。

## Keyboardでの利用

[ABC434 Gの実装例](https://github.com/lif4635/harurun-s-library/blob/main/verify/atcoder/abc434_g.py)は、数字の入力と`B`による末尾削除を管理する。`Keyboard`が文字と集約値の変換を受け持ち、内部の`SegTreeTraversal`へ更新と取得を渡す。

```python
from verify.atcoder.abc434_g import Keyboard

tree = Keyboard("123B45")
before = tree.prod(0, 6)
tree.set(1, "B")
after = tree.prod(0, 6)
```

このimportはリポジトリ内で使う場合のもの。提出時は[依存込みコード](https://github.com/lif4635/harurun-s-library/blob/main/verify/atcoder/abc434_g_standalone.py)をコピーできる。

- `before`は`(0, 4, 1245)`、`after`は`(0, 2, 45)`。
- 第1要素: 区間内の数字だけでは消化できず、左側へ持ち越す`B`の個数。
- 第2要素: 残る数字列の長さ。
- 第3要素: 残る数字列を整数とみなした998244353での余り。数字が残らなければ0。

結合処理`_merge`は、右側の`B`が左側の何桁を消すかを調べる。左側を途中まで残すときだけ、左の部分木を降りて先頭の値を取り出す。各段で調べる子は一つなので、降下は木の高さに比例する。

内部の集約値は、上の3要素に「左の子から残った先頭部分の値」を加えた4要素。この第4要素を保存すると、子孫への降下で逆元計算が不要になる。利用側へ返す`prod`では先頭3要素だけを取り出す。

最大800万文字の保存量を抑えるため、この例だけ`storage`で32bit整数配列の保存先を渡している。`_KeyboardData`は木全体で1個の保存先であり、ノードごとのobjectではない。読み書きの際に集約値をtupleとして受け渡すが、tupleを各ノードに保持しない。普通の使い方では`storage`を指定せず、最初の例のようにlistでよい。

## 仕組み

構築と更新では、左の子を`left_node`、右の子の保存値を`right_value`として結合する。

`prod`は区間を覆うノードを右から左へ処理する。途中結果を右側の値として受け渡すので、結合の左側は常に実在するノードになり、子孫を参照できる。再帰や問い合わせ用のノードobjectは作らない。

空でない木の葉数を2の冪Mへ切り上げると、高さhのノードはM/2^h個ある。各結合がO(h+1)なら、M<2Nなので合計はO(N)になる。

$$\sum_{h=1}^{\log_2 M}\frac{M}{2^h}O(h+1)=O(M)=O(N)$$

## 注意点

- `identity`は空区間を表す値。余った葉はclassがこれで埋める。どちらかが空でも`merge`が正しく結合できること。
- `identity`や保存値は共有される場合がある。取得した可変objectを直接書き換えず、`set`で置き換える。
- 時間は結合処理に依存する。子孫をすべて走査する処理を書けば、O(log² N)にはならない。
- `storage`を指定する場合は、`storage(capacity, identity)`で初期化済みの保存先を返す。整数添字の読書きと`len`をO(1)で行え、例外となる書き込みでは内容を変えないこと。
- 通常のモノイド演算だけで済む場合は`SegTree`を使う。境界探索や遅延伝播はこのclassには含めていない。

## 参考

- [ABC434 G Keyboard](https://atcoder.jp/contests/abc434/tasks/abc434_g)
- [Nyaanによる公式解説](https://atcoder.jp/contests/abc434/editorial/14660)
- [よすぽ「ちょっと重いSegTree」](https://yosupo.hatenablog.com/entry/2015/12/02/235855)
