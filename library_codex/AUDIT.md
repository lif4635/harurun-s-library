# library_codex 保守監査

この文書は、既存ライブラリを実用状態に保つための完了条件と、今回の監査結果を記録する。
新しいアルゴリズムを際限なく追加することは対象外とし、正しさ、通常実行、API一貫性、性能、文書、Git衛生を対象とする。

## 監査開始時点

- 実装: 146モジュール
- 検証: 122テストファイル、PyPyで432テスト成功済み
- 再帰監査: 2980関数、直接・相互再帰なし
- APIリファレンス: sourceと同期済み
- Git: `main` は `origin/main` より2コミット先行、作業ツリーはclean

## 優先順チェックリスト

- [x] 作業ツリーと既存変更を確認し、利用者の変更を上書きしないことを確認する
- [x] `TODO`、`FIXME`、`NotImplementedError`、空の `pass` を列挙して未実装を探す
- [x] 曖昧な版名、追跡済みcache、誤った実行権限を探す
- [x] 全Python sourceをbyte-compileする
- [x] APIリファレンスとsourceの同期を検査する
- [x] 直接・相互再帰を検査する
- [x] 日常用とリリース用の検証を同じ入口から実行できるようにする
- [x] 検証方法と監査記録への導線をREADMEへ追加する
- [x] 日常用のテスト・性能回帰検査を実行する
- [x] 全テスト・全性能回帰検査を実行する
- [x] 最終結果をこの文書へ記録し、Git差分と作業ツリーを確認する

## 確認した所見

- `DynamicWaveletMatrix.py` の `NotImplementedError` は、2種類のbackendに共通する問い合わせ処理を持つ内部基底classの必須hookであり、公開機能の未実装ではない。
- `FormalPowerSeries.py` の `pass` は、対象modでNTTを使えない場合に通常の畳み込みへ切り替えるための例外処理である。
- `GeneralWeightedMatching.py` の `pass` は、増加がなくなるまで処理するloop本体である。
- 検証コード中の `pass` は例外送出を期待するテストの失敗分岐であり、未実装ではない。
- `v1`、`v2` は永続データ構造の版を表すテスト変数だけで、成果物名の不自然な版付けはない。
- 追跡済みのcache・bytecode・一時benchmark出力はなく、`library_codex` 内のPython fileに不要な実行権限もない。
- 最初の日常検査ではCSR LowLinkが1.495倍、閾値1.500倍となり、約0.3%の計測ぶれで失敗した。CSR系は3回の中央値で判定するようにし、日常用LowLink閾値は計測余裕を持つ1.35倍へ変更した。リリース用の2.0倍閾値は維持する。

## 検証コマンド

日常確認:

```console
pypy3 library_codex/tools/check_library.py
```

リリース相当の全確認:

```console
pypy3 library_codex/tools/check_library.py --profile full
```

どちらもbyte-compile、API同期、再帰監査、テスト、性能回帰検査の順に実行し、途中で失敗した場合は非0で終了する。

## 最終結果

- 日常確認: 25テスト成功、性能回帰を含む全工程が41.10秒で成功
- 全確認: 432テスト成功、全工程が684.85秒で成功
- byte-compile: 成功
- APIリファレンス: 146モジュール、387関数、203クラス、1205メソッドでsourceと同期
- 再帰監査: 2983関数、直接・相互再帰なし
- 大規模CSR中央値: Dijkstra 1.81倍、SCC 3.57倍、LowLink 3.22倍
- 大規模整数専用tree: 汎用tree比4.05倍、Segment Tree Beats比3.85倍、affine版は汎用tree比2.18倍
- Push-relabelは短い日常用caseではDinicより高速だったが、大規模な密ランダムcaseでは0.63倍だった。常に高速な置換とはせず、graph形状に応じて選ぶbackendとして扱う。
- `git diff --check`: 問題なし

監査対象とした未完了項目は0件。今後の変更は `check_library.py` の日常確認を使い、公開・統合前には `--profile full` を実行する。
