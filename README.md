# harurun-s-library

[ライブラリサイト](https://haruruns-library.star-mido-322.chatgpt.site/) · [API索引](library_codex/docs/README.md) · [Library Checkerの解答](verify/library_checker/solutions/)

## 使う

- コピーして提出する：サイトで使いたいモジュールを開き、依存込みのコードをコピーする。インストールは不要。
- 手元でimportする：[library_codexの使い方](library_codex/README.md)。
- 問題の解答を見る：[Library Checker](verify/library_checker/README.md)。単独実行できるコードと検証結果を問題名で探せる。

## ファイルの場所

| 場所 | 内容 |
| --- | --- |
| [library_codex/](library_codex/) | 現在の実装。PyPy向け |
| [library/](library/) | 以前の実装。現在の実装とはAPIが異なる |
| [verify/library_checker/](verify/library_checker/) | 問題別の解答・公式ケースの検証結果・測定値 |
| [library_codex/docs/](library_codex/docs/) | API、使い方、保守手順 |

## 変更する

[実装と文書の更新手順](library_codex/docs/CONTRIBUTING.md)に従う。変更範囲の検査は、リポジトリ直下から実行する。

```sh
pypy3 library_codex/tools/check_changed.py
```
