# ライブラリ記事

このdirectoryは、Webサイトとcatalogが共通で使う、人が書いたmodule記事の正本です。signature・依存・standalone codeなどsourceから分かる情報は記事へ複製せず、catalog生成時に自動で合成します。

記事はsourceと同じcategory・module名で置きます。

```text
library_codex/range_query/WeightedWaveletMatrix.py
library_codex/docs/articles/range_query/WeightedWaveletMatrix.md
```

新しい公開moduleには記事が必須です。既存moduleは`legacy_modules.txt`に残っている間だけ従来表示を許し、記事へ移行するときに対応する行を削除します。記事とlegacy指定の両方がある状態、どちらもない状態、削除済みmoduleを指す状態はcatalog検査で失敗します。

## 必須の形

- 先頭を、利用者が探す目的を表すH1 titleにする。file名をそのまま繰り返す必要はない。
- `## 主な機能`を必ず置き、入力・処理できる問い・代表的な計算量を説明する。
- `## 使い方`で、競技中に実際に書く最小のcodeと返り値の読み方を示す。
- 必要に応じて`## 仕組み`、`## 注意点`、`## 参考`を追加する。
- 複数の返り値や返り値の各要素は、長い段落へ詰め込まず`名前: 意味`の箇条書きにする。
- 複数の公開APIがある場合は、signatureを行頭の同じ位置へ揃え、function・class・methodの種別はsignatureの後ろで説明する。「入口」「機能」のような語だけで実装単位を隠さない。
- `## 注意点`は一項目一判断の箇条書きにする。条件・例外・別moduleとの違いを文章で連結しない。
- 短い配列や隣接listの例は一行に置く。横に長すぎる場合だけ改行し、縦方向へ一要素ずつ展開しない。
- MarkdownとTeXを使い、raw HTMLは前提にしない。
- API一覧を本文へ転記しない。各methodのsignature・引数・返り値・計算量は自動生成されるAPI Referenceに任せる。

雛形は`tools/create_module_article.py category/Module`で作れます。生成されたplaceholderを具体的な説明へ書き換えるまで検査は通りません。

文章、Arguments、Returns、Complexity、数式、見た目の詳しい基準は[`PAGE_CONTENT_GUIDE.md`](../PAGE_CONTENT_GUIDE.md)を正本とします。
