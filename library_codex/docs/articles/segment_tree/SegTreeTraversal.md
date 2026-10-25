# 子孫を参照しながらマージするセグメント木

## 主な機能

左右の集約値だけでは結合できず、片方の部分木へ降りて追加情報を調べたいときの、構築・一点更新・区間取得を共通化する。

通常の`SegTree`とは別の、3つの関数からなる部品。データ配列は利用側で持ち、ノードは整数添字で扱う。`list`でも複数の`array`でもよく、ノードごとのclass instanceは作らない。

高さhの部分木の再計算・結合がO(h+1)なら、構築はO(N)、一点更新と区間取得はO(log² N)。通常のO(1)マージなら更新・取得はO(log N)になる。

## 使い方

```python
from library_codex.segment_tree.SegTreeTraversal import build, fold, update

values = ["a", "b", "c", "d", "e"]
size = 1 << (len(values) - 1).bit_length()
data = [""] * (2 * size)
data[size:size + len(values)] = values

def pull(node):
    data[node] = data[node * 2] + data[node * 2 + 1]

def prepend(node, result):
    return data[node] + result

build(size, pull)
answer = fold(size, 1, 4, prepend, "")
data[size + 2] = "X"
update(size, 2, pull)
changed = fold(size, 1, 4, prepend, "")
```

- `answer`は`"bcd"`、`changed`は`"bXd"`。
- `pull(node)`は、子が正しい状態になった後に呼ばれる。左右の子は`2*node`と`2*node+1`。必要ならさらに子孫へ降り、親の保存値を書き換える。返り値は使わない。
- `prepend(node, result)`は、実在する部分木を`result`の左へつなげた集約値を返す。木の保存値を変更しない。
- `update`は葉を書き換えない。葉の変更を済ませてから呼ぶ。

文字列連結は呼出し方を示す小さい例。長い文字列そのものを結合すると、その文字数に比例する時間がかかる。

## Keyboardでの利用

[ABC434 Gの実装例](https://github.com/lif4635/harurun-s-library/blob/main/verify/atcoder/abc434_g.py)では、数字の入力と`B`による末尾削除を管理する。文字列の一点変更と、任意の半開区間を入力した後に残る数字列の取得ができる。

```python
from verify.atcoder.abc434_g import Keyboard

tree = Keyboard("123B45")
before = tree.prod(0, 6)
tree.set(1, "B")
after = tree.prod(0, 6)
```

この例のimportはリポジトリ内で実行する場合のもの。提出時は[依存込みコード](https://github.com/lif4635/harurun-s-library/blob/main/verify/atcoder/abc434_g_standalone.py)を使える。

- `before`は`(0, 4, 1245)`、`after`は`(0, 2, 45)`。
- 第1要素は、区間内の数字だけでは消化できず、左側へ持ち越す`B`の個数。
- 第2要素は、残る数字列の長さ。
- 第3要素は、残る数字列を整数とみなした998244353での余り。数字が残らなければ0。

右の区間の`B`が左の数字を消すとき、左の集約値だけからは残る先頭の数字を復元できない。左の部分木を降りて必要な桁数だけ取り出す。左右のうち次に調べる子は一つなので、降下は木の高さに比例する。

実装例は個数・長さ・値を32-bit整数配列へ保存し、左右の境界で残った左側の値も内部ノードに保存する。これにより降下時の逆元計算と再帰を避ける。tupleを作るのは区間取得の途中結果で、各ノードには置かない。

## 仕組み

`fold`は区間を覆うノードを右から左へ処理する。途中結果同士は結合せず、左側が必ず実在するノードなので、その子孫を参照できる。途中結果に元の木の添字があるとは限らない点に注意する。

構築では高さhのノードが高々N/2^h個ある。各再計算がO(h+1)なら、合計は次のようにO(N)になる。

$$\sum_{h=1}^{\lceil\log_2 N\rceil}\frac{N}{2^h}O(h+1)=O(N)$$

## 注意点

- `size`は葉の容量で、正の2の冪。根は1、葉は`size`から`2*size-1`。0番は使わない。
- 要素数が`size`未満なら、残りの葉には空区間に相当する値を配置する。要素数0でも`size=1`を使う。
- 各関数が検査する添字の範囲は`size`まで。実際の要素数を超えた操作の防止は利用側で行う。
- `initial`は右端の後ろにつなぐ初期状態。普通の区間取得では空区間を表す値を渡す。空区間ならそのまま返る。
- `pull`と`prepend`は同じ列の意味を表すように書く。何を渡してもO(log² N)になるわけではなく、子孫を調べる計算量にも依存する。
- 通常のモノイド演算だけで済む場合は`SegTree`を使う。境界探索や遅延伝播はこの部品には含めていない。

## 参考

- [ABC434 G Keyboard](https://atcoder.jp/contests/abc434/tasks/abc434_g)
- [Nyaanによる公式解説](https://atcoder.jp/contests/abc434/editorial/14660)
- [よすぽ「ちょっと重いSegTree」](https://yosupo.hatenablog.com/entry/2015/12/02/235855)
