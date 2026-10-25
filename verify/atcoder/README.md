# AtCoderの利用例

## ABC434 G — Keyboard

- [問題](https://atcoder.jp/contests/abc434/tasks/abc434_g)
- [ライブラリを使う実装](abc434_g.py)
- [依存を含む提出用コード](abc434_g_standalone.py)
- [共通部品の使い方](../../library_codex/docs/articles/segment_tree/SegTreeTraversal.md)
- [PyPyの比較条件・結果](../../library_codex/docs/SEG_TREE_TRAVERSAL_BENCHMARK.md)

`Keyboard`は文字列の一点変更と、半開区間へ数字入力・末尾削除を適用した結果を扱う。`SegTreeTraversal`が木の構築・祖先の再計算・右からの区間結合を担当し、文字列固有のマージはこの実装例に置く。

リポジトリ直下から実行する場合：

```sh
pypy3 -m verify.atcoder.abc434_g < input.txt
```

提出用コードはライブラリをインストールせず、そのまま実行できる。

```sh
pypy3 verify/atcoder/abc434_g_standalone.py < input.txt
```

sourceを変更した場合の生成・検査：

```sh
pypy3 verify/atcoder/build_keyboard.py
pypy3 verify/atcoder/build_keyboard.py --check
pypy3 -m pytest -q library_codex/verify/segment_tree/test_seg_tree_traversal.py
```

検証範囲は公式サンプル、単純解とのランダム比較、全区間・先頭桁の照合、独立processでの提出コード実行。公式全ケース検査・オンラインACは未実施。
