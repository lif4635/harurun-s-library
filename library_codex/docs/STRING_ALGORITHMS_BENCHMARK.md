# 文字列6問題の公式検査と両端回文木の比較

2026-10-05。PyPy 7.3.16 / Python 3.10.14、WSL Linux、Ryzen 7 3700X。公式問題revisionは `1814c4e5205517e368bb57a8d1127eb961cfeaae`。オンライン提出は行っていない。

## 公式全ケース

| 問題 | ケース数 | 結果 |
| --- | ---: | --- |
| aho_corasick | 72 | 全件通過 |
| eertree | 24 | 全件通過 |
| palindromes_in_deque | 24 | 全件通過 |
| prefix_substring_lcs | 11 | 全件通過 |
| runenumerate | 24 | 全件通過 |
| wildcard_pattern_matching | 19 | 全件通過 |

計174ケースを追加し、累計136問題・3073ケース、未実装117問題。`DequePalindromicTree`だけを新規実装し、ほかの5問題には既存のライブラリを使うdriverを追加した。

公式全件の判定・単発時間・source hashは `verify/library_checker/results/`、単独で動く解答は `solutions/` に保存している。メモリ制限はローカルで再現しておらず、オンラインACと同じ意味ではない。

各問題で遅かった公式3ケースを各5回測り直した。計90回で、[標準ベンチマーク](../../verify/library_checker/benchmarks/README.md)の記録は累計60問題になった。136問題すべてを反復測定したわけではない。

| 問題 | 3ケース中の最大中央値 | 測定中の最大RSS |
| --- | ---: | ---: |
| aho_corasick | 2.762秒 | 642668 KiB |
| eertree | 1.424秒 | 738772 KiB |
| palindromes_in_deque | 0.742秒 | 291736 KiB |
| prefix_substring_lcs | 0.739秒 | 131880 KiB |
| runenumerate | 2.749秒 | 290956 KiB |
| wildcard_pattern_matching | 0.853秒 | 135080 KiB |

Aho-Corasickと通常の回文木は最大規模でメモリが多い。今回は既存実装を変更せずに公式全件を確認した段階で、上位実装との定数倍比較・軽量化はまだ行っていない。

## 両端回文木

`DequePalindromicTree`は、列の両端への追加・削除と、回文の種類数・最長回文接頭辞長・最長回文接尾辞長の取得に対応する。

- 回文ごとのclassを作らず、整数IDと平坦な配列で管理する。
- ランダムアクセスできるリングバッファを使う。
- 消えた回文のIDを再利用し、保持領域を操作回数ではなく列の最大長に比例させる。
- surface方式とquick linkを使い、追加を償却期待O(log(L+2))、削除を償却期待O(1)で行う。Lは列の最大長、hash・等値比較はO(1)とする。
- 固定26文字の専用実装ではなく、hash可能な一般の要素を受け取る。

公式24ケースの最大時間は0.745秒。制限時間は10秒。

取得時点の最速PyPy提出 [391665](https://judge.yosupo.jp/submission/391665) と、同じ公式4ケースで各5回比較した。参照sourceは実行前に全体を確認した。時間は新規プロセスの起動・JIT・入出力を含む中央値。各回の順番を入れ替え、全出力を公式checkerで検査した。

| ケース | 採用版 | 参照391665 | 採用版最大RSS | 参照最大RSS |
| --- | ---: | ---: | ---: | ---: |
| short_period_04 | 0.705秒 | 1.280秒 | 291872 KiB | 278352 KiB |
| small_all_00 | 0.841秒 | 1.410秒 | 109340 KiB | 134472 KiB |
| bad_failure_link_00 | 0.521秒 | 1.082秒 | 199688 KiB | 205040 KiB |
| random_01 | 0.465秒 | 0.828秒 | 129760 KiB | 152564 KiB |

- 測定した4ケースでは採用版が約1.68〜2.08倍速かった。
- `short_period_04`のメモリは参照より約4.9%多い。他の3ケースでは少なかった。
- 参照は2本のlistに符号・端点情報を96bit整数へまとめて格納し、回文のIDを再利用しない。採用版はリングバッファの3本の配列とID再利用を使う。入出力処理も異なり、差をデータ構造だけの効果とは断定しない。
- 出力hashの違いは末尾改行などによる。答えの一致は公式checkerで確認した。
- 上位比較は24ケース中4ケースに限る。全ケース・全言語で最速とは主張しない。

[比較の全測定値と参照snapshot](../benchmarks/results/deque-palindromic-tree-comparison.json)に、各回の時間・最大RSS・入力hash・source hash・ランキング取得時刻を保存している。

## 再実行

文字列実装と公式検査runnerの関連テストは66件通過した。新しい両端回文木には、6操作の全探索、ランダム更新、空列、異種のhash可能な要素、リングバッファの拡張・折返し、削除後のID再利用、長い同一文字列への失敗探索、記事の使用例を残している。

通常のquickテスト144件と性能回帰検査も通過した。source・API・catalog・提出コードの同期、説明監査、5113関数の再帰監査も成功。全ライブラリのfull検査は今回再実行していない。

```sh
pypy3 library_codex/tools/check_library_checker.py test aho_corasick eertree palindromes_in_deque prefix_substring_lcs runenumerate wildcard_pattern_matching --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py aho_corasick eertree palindromes_in_deque prefix_substring_lcs runenumerate wildcard_pattern_matching --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/library_checker.py fetch --problem palindromes_in_deque --language pypy3 --top 2 --cache ../lc-matching-reference
```

取得した外部sourceを確認した後、比較対象のIDを明示する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot ../lc-matching-reference/palindromes_in_deque-pypy3.json --reviewed 391665 --problem /home/harurun/.cache/harurun-library-checker/problems/string/palindromes_in_deque --cases short_period_04 small_all_00 bad_failure_link_00 random_01 --variant library=verify/library_checker/solutions/palindromes_in_deque.py --repeat 5 --timeout 90 --output library_codex/benchmarks/results/deque-palindromic-tree-comparison.json
```

ランキングは変化するので、再取得時に同じIDが含まれるとは限らない。保存したsnapshotとsource hashで比較対象を区別する。
