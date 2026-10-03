# Library Checker の公式ケース検査

`manifest.json` に公式の全問題と対応状況を記録する。未実装・未検証・失敗を残し、提出コードがあるだけで完了にしない。

`unimplemented` は、その問題の提出コードが未整備であることを表す。既存ライブラリに必要な機能がないという意味ではない。

- `drivers/`: 問題固有の入出力。アルゴリズムは `library_codex` から import する。
- `solutions/`: 依存を展開した提出コード。そのまま単独で実行できる生成物。
- `results/`: 公式全ケースの判定、時間、source hash、公式問題version、実行環境。
- `manifest.json`: 問題一覧と解答・結果の対応。

以前からある問題別 benchmark の解答も生成に利用する。`drivers/` に同名ファイルを置いた場合はそちらを使う。生成済み `solutions/` は直接編集しない。

## 実行

WSL の PyPy、g++、Git と、[公式問題リポジトリ](https://github.com/yosupo06/library-checker-problems)を使う。初回は専用キャッシュへ取得する。

```sh
git clone https://github.com/yosupo06/library-checker-problems.git /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/tools/check_library_checker.py list --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/tools/check_library_checker.py test --official /home/harurun/.cache/harurun-library-checker/problems
```

特定の問題だけ回す場合は名前を指定する。

```sh
pypy3 library_codex/tools/check_library_checker.py test convolution_mod scc --official /home/harurun/.cache/harurun-library-checker/problems
```

公式の `generate.py` で全入力・正解出力・checkerを用意し、公式 `hash.json` と一致することを検査する。その後、各入力に提出コードを起動して、公式checkerで判定する。別解を許す問題も出力文字列の単純一致では判定しない。

- 同じ解答・公式問題version・runner・実行環境で全件通過済みなら再実行しない。`--force` で測り直せる。
- 解答が依存するライブラリを変更すると、展開後のsource hashが変わり再検査される。
- 公式テストやcheckerは、公式生成器の更新判定で再利用する。大きな入出力はGitへ入れない。
- 既存キャッシュがある場合、`--reuse-tests /home/harurun/.cache/online-judge-tools/library-checker-problems` を追加すると、公式hashが一致する入力・正解出力だけをコピーする。コピー元は変更しない。
- テスト実行は逐次。計測には起動・JIT・入出力を含む。

## 解答の追加と更新

1. 未対応問題の制約と高速解法を確認する。既存ライブラリで不足する場合は、再利用可能な実装を `library_codex` へ追加・改善する。
2. 専用の単純解比較test、API説明、記事を追加する。
3. `drivers/<problem>.py` に入出力を書き、提出コードを生成する。
4. 公式全ケースを実行する。TLE・WA・REは結果を残し、成功として扱わない。

```sh
pypy3 library_codex/tools/check_library_checker.py build
pypy3 library_codex/tools/check_library_checker.py check
```

この2コマンドは公式リポジトリなしでも使える。通常の `check_changed.py` と `check_library.py` は提出コードの同期とrunnerのunit testを検査し、重い公式テスト全件を毎回起動しない。`prepare_checkpoint.py` は提出コードも再生成する。

公式問題リポジトリを更新した後は `list` または `test` を実行する。問題一覧はそのcheckout内の `info.toml` から作り直すため、新しい問題も未実装として現れる。

## 判定の範囲

`local_passed` は、その公式revisionの全ケースをローカルchecker・制限時間で通過した状態。オンラインのAC提出ではない。`onlineSubmission` は未提出なら `null`。

時間制限は公式の値を使うが、手元のCPU・PyPy version・OS負荷はオンラインjudgeと異なる。メモリ制限は再現していない。したがってオンラインACや本番環境での同じ実行時間を保証しない。

`stale` は解答または公式問題が変更された状態。`incomplete` は途中までの実行、`failed` は少なくとも一件が不通過、`error` は生成・実行基盤の失敗。結果JSONは一時ファイルから置き換え、途中で壊れたJSONを残さない。
