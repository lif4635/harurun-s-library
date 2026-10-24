# library_codex

[API索引](docs/README.md) · [ライブラリサイト](https://haruruns-library.star-mido-322.chatgpt.site/) · [問題別の解答](../verify/library_checker/solutions/)

## 使い方

### コピーして使う

サイトのモジュールページ下部から、依存込みのコードをコピーして解法の前に置く。ライブラリをインストールしていない提出先でも使える。

実装ファイルだけをコピーすると、別モジュールへのimportが残る場合がある。依存込みのコードを選ぶ。

### importして使う

リポジトリ直下に解法ファイルを置くか、リポジトリ直下を`PYTHONPATH`へ追加する。`library_codex`自体ではなく、その親ディレクトリを指定する。

```python
from library_codex.segment_tree.SegTree import SegTree

seg = SegTree(lambda a, b: a + b, 0, [2, 7, 1])
print(seg.prod(0, 3))
seg.set(1, 4)
print(seg.prod(0, 2))
```

出力は順に`10`、`6`。実行は`pypy3 main.py`。提出先にこのリポジトリがない場合は、依存込みのコードへ展開して使う。

## APIを調べる

[API索引](docs/README.md)からカテゴリとモジュールを選ぶ。引数、返り値、計算量は各APIの説明を参照する。

- [使い方の記事](docs/articles/)：使用例と、返り値の読み方。
- [デバッグ出力](docs/DEBUG_OUTPUT.md)：`str`・`repr`・`tolist()`・`items()`。
- [VS Codeでの可視化](docs/articles/debug/DebugView.md)：フロー・グラフ・配列をHaru Deskへ表示。
- [Codon対応](docs/CODON.md)：変換方法と対応範囲。全モジュール対応ではない。

## 検証を確認する

- [Library Checker](../verify/library_checker/README.md)：問題別の提出コード、公式ケースの判定、再実行方法。
- [PyPyベンチマーク](../verify/library_checker/benchmarks/README.md)：入力・環境を記録した反復測定。
- [実装の比較記録](docs/BENCHMARKS.md)：高速化の根拠と、比較対象・適用条件。

PyPy 全検証: 1303 passed（2026-10-24）。この値は全体検査を実行した時点の記録で、Library Checkerの問題数ではない。

## 変更する

実装はここを正本とし、`../library`は旧実装の参照に使う。設計・テスト・文書・生成物の更新は[保守手順](docs/CONTRIBUTING.md)に従う。

リポジトリ直下で実行する。

```sh
pypy3 library_codex/tools/check_changed.py
```

APIや記事を変えた場合は、生成と差分検査をまとめて行える。

```sh
pypy3 library_codex/tools/prepare_checkpoint.py --no-benchmarks
```

[共通catalog](library-catalog.json)はサイトとHaru Deskが読む生成物。直接編集しない。
