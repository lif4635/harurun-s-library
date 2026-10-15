# Codon向けコード

現在の`library_codex`から生成したコードは[generated/](generated/)にある。各`.codon`ファイルは依存と補助処理を含むので、末尾に解法を書いて使える。

- [対応状況](generated/manifest.json): 全モジュールを一覧化。`supported`だけが生成対象で、`unsupported`は未対応。
- [使い方と制約](../library_codex/docs/CODON.md): 64bit整数、入力、生成方法。
- [公式ケースのCodon解答と比較結果](../verify/library_checker/codon/README.md): SCC・2-SAT。

`generated/`以外の既存ファイルは旧ライブラリ用の実装。現在のAPIや検証状況とは分けて扱う。ファイルは保持しているが、自動同期の対象ではない。

## 更新

元の実装は`library_codex`側で編集する。生成済みコードは直接編集しない。

```sh
pypy3 library_codex/tools/build_codon.py --build-library
pypy3 library_codex/tools/build_codon.py --check
```

通常のcheckpointで再生成し、ライブラリ検査で同期を確認する。同期検査はコンパイル検証の代わりではない。対応範囲を広げたときはCodon実機で比較テストを行う。
