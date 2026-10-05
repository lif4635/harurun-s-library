# Library Checker の公式ケース検査

`manifest.json` に公式の全問題と対応状況を記録する。未実装・未検証・失敗を残し、提出コードがあるだけで完了にしない。

`unimplemented` は、その問題の提出コードが未整備であることを表す。既存ライブラリに必要な機能がないという意味ではない。

2026-10-05時点の公式revision `1814c4e`では、150問題・3440ケースがローカル全件通過、103問題が未実装。

木・区間・群の差の7問題、192ケースを追加した。距離範囲和と区間最頻値の時間超過を解消した。[検査・比較結果](../../library_codex/docs/TREE_RANGE_BENCHMARK.md)に記録している。

行列の7問題、175ケースを追加した。行列累乗の時間超過を解消し、行列積も高速化した。[行列の検査・比較結果](../../library_codex/docs/MATRIX_ALGORITHMS_BENCHMARK.md)に記録している。

前回の文字列6問題と両端回文木は[文字列の検査・比較結果](../../library_codex/docs/STRING_ALGORITHMS_BENCHMARK.md)に記録している。

前回の辺追加SCCと重み付き一般マッチングのTLE修正は[高速化と上位PyPy実装との比較](../../library_codex/docs/GRAPH_ALGORITHMS_BENCHMARK.md)に記録している。

前回の最近点対の高速化は[変更前・上位PyPy実装との比較](../../library_codex/docs/CLOSEST_PAIR_BENCHMARK.md)に記録している。

動的列と区間頻度の前回の高速化は[比較結果](../../library_codex/docs/DATA_STRUCTURE_BENCHMARK.md)に記録している。

- `drivers/`: 問題固有の入出力。アルゴリズムは `library_codex` から import する。
- `solutions/`: 依存を展開した提出コード。そのまま単独で実行できる生成物。
- `results/`: 公式全ケースの判定、時間、source hash、公式問題version、実行環境。
- [`benchmarks/`](benchmarks/README.md): PyPyで反復測定した時間・最大RSS・各回の生データ。
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
5. PyPyで時間のかかった公式ケースを反復測定し、`benchmarks/`へ記録する。オンライン提出は行わない。

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

## PyPyベンチマーク

公式全件検証を終えた問題に対して、次で測定する。

```sh
pypy3 library_codex/benchmarks/official_benchmark.py matrix_product_mod_2 inverse_matrix_mod_2 --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

- 既定では直前の全件検証で遅かった3ケースを各5回実行する。`--slowest 0`なら全公式ケースを反復する。
- 各回は新しいPyPy processで、起動・JIT・入出力を含む。ケース順を入れ替え、逐次実行する。ほかの重いテストと同時に測らない。
- 全出力を公式checkerで検査する。入力・期待出力は公式hashと照合する。
- CPU、OS、PyPy version、公式revision、source・入力・checkerのhash、各回の時間とRSS、中央値・最小値・最大値をJSONへ保存する。
- 現在のsourceで公式全件検証が済んでいなければ測定しない。失敗した測定で以前の正常なベンチマークJSONを上書きしない。
- `benchmarks/README.md`へ一覧を生成する。既存結果が現在のsourceと異なる場合は「要再測定」と表示する。
- 測定用timeoutは最低30秒。公式の制限時間内に通るかどうかは`results/`の全件検証で判断する。RSSは記録するがメモリ制限は強制しない。

これは全入力の最悪時間やオンラインjudgeでの速度を保証するものではない。上位提出との同一入力比較は[比較記録](../../library_codex/docs/LIBRARY_CHECKER_COMPARISON.md)へ分けて残す。

## 性能上の注意

`bipartitematching` は次数優先の初期マッチングと、距離ラベルによる再割当を行い、走査上限に達したらHopcroft–Karpへ戻る。`a1076d2`との同条件5回比較では、`augmented_cycle_02`の中央値が2.976秒から0.558秒になった。PyPy最速提出は同じ入力で0.396秒だった。公式44ケースは全件通過し、その実行の最大は0.678秒。詳細は[上位提出との比較](../../library_codex/docs/LIBRARY_CHECKER_COMPARISON.md)へ保存している。オンライン環境の速度は未確認。

`range_affine_point_get` の追加時に、`DualSegTree`で包含する区間と部分区間の更新順序が逆転する不具合を修正した。区間更新前に境界まで保留中の作用を下ろし、非可換なaffine変換も入力順に適用する。専用の小入力比較と公式全件検査で検証する。

`range_parallel_unionfind` も最速PyPy提出を参照した。代表探索の重複を除き、階層を固定幅の整数配列へまとめ、driverの入力は1行ずつ処理する。同じ大規模3ケースの比較で約1.9〜2.2倍高速化し、最大RSSを約44%削減した。時間・メモリ・最速提出との差は同じ[比較記録](../../library_codex/docs/LIBRARY_CHECKER_COMPARISON.md)へ保存している。
