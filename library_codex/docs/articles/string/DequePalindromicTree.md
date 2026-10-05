# 両端を更新できる回文木

文字列や整数列の両端へ要素を追加・削除しながら、回文の種類数と、最長の回文接頭辞・接尾辞を求めます。

## 主な機能

- `append(symbol)`・`appendleft(symbol)`で末尾・先頭へ1要素追加します。
- `pop()`・`popleft()`で末尾・先頭の1要素を削除します。
- `query()`で、現在の列にある異なる非空回文の種類数、最長の回文接頭辞の長さ、最長の回文接尾辞の長さを取得します。
- 追加は償却期待O(log(L+2))、削除は償却期待O(1)、取得はO(1)です。Lはこれまでの列の最大長で、hash・等値比較1回をO(1)とします。保持領域はO(L+1)です。

同じ回文が複数の位置に現れても1種類です。例えば`ababa`には`a`・`b`・`aba`・`bab`・`ababa`の5種類があります。ここでいう回文は、文字を飛ばさずに取り出す連続部分列です。

## 使い方

```python
tree = DequePalindromicTree("ababa")
count, prefix_length, suffix_length = tree.query()
assert (count, prefix_length, suffix_length) == (5, 5, 5)

tree.append("c")
assert tree.query() == (6, 5, 1)
assert tree.popleft() == "a"
assert tree.query() == (5, 3, 1)

tree.appendleft("c")
assert tree.query() == (5, 1, 1)
assert tree.tolist() == list("cbabac")
```

`query()`の返り値は次の3要素です。

- `count`: 現在の列に含まれる、異なる非空回文の種類数。
- `prefix_length`: 先頭から始まる最長回文の長さ。
- `suffix_length`: 末尾で終わる最長回文の長さ。

個別には`distinct_count`・`longest_prefix`・`longest_suffix`で取得できます。空の列ではいずれも0です。

## 仕組み

回文を整数IDで管理し、長さ・suffix link・出現を保つためのカウンタを平坦な配列に格納します。列の両端に関係する回文だけを更新するsurface方式と、同じ文字で伸ばせない候補を飛ばすquick linkを使います。

列はランダムアクセスできるリングバッファに置きます。削除で消えた回文のIDを再利用するため、短い列への追加・削除を何度繰り返しても、ノード領域が操作回数に比例して増え続けることはありません。

## 注意点

- 最長の回文接頭辞・接尾辞を返します。列の途中も含めた最長回文の長さではありません。
- 空の列への`pop()`・`popleft()`は`IndexError`です。
- 要素はhash可能で、格納中にhash値や等値比較の意味が変わらない必要があります。
- `append("ab")`は2文字追加ではなく、文字列`"ab"`を1要素として追加します。
- 各回文の出現回数やノード一覧を取得する場合は`PalindromicTree`を使います。そちらは両端削除には対応しません。

## 参考

- [Double-Ended Palindromic Trees: A Linear-Time Data Structure and Its Applications](https://arxiv.org/abs/2210.02292)
- [EERTREE: An Efficient Data Structure for Processing Palindromes in Strings](https://arxiv.org/abs/1506.04862)
- [Library Checkerの公式解法](https://github.com/yosupo06/library-checker-problems/blob/master/string/palindromes_in_deque/sol/correct.cpp)
