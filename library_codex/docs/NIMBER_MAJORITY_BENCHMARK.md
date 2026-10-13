# 64bit nim積・区間過半数検索の検査と比較

測定日: 2026-10-13。変更前のlibrary revision: `0635c98`。

## 変更と公式検証

- `nim_product_64`: 公式10ケース通過。既存の`Nimber.py`へ16bitの対数表・指数表・固定乗数の表を追加した。64bit積を初めて必要としたときだけ準備する。
- `majority_voting`: 公式12ケース通過。既存の`RangeMajority`へ`set`を追加した。候補のセグ木は値と残り個数を別配列に保持し、値ごとの出現位置は1本の配列にまとめたtreap群で管理する。
- いずれもオンライン提出はしていない。公式revisionは`1814c4e5205517e368bb57a8d1127eb961cfeaae`。

新しい類似classや互換aliasは増やしていない。RangeMajorityは更新しない間、従来同様に出現位置を二分探索し、更新用の木の配列を確保しない。更新後もノード数は常に配列長Nで、値の変更履歴に比例して増えない。

`prepare_checkpoint.py --profile full`で全992テスト・性能回帰検査・API/catalog同期検査が成功。説明監査は0件、6281関数に直接・相互再帰なし。

nim積は全4096組の64bit基底対、ランダム2000組、16bit固定乗数の全65536値を従来方式と照合した。既存のmex定義・体の公理・逆元・基底変換の検査も維持する。RangeMajorityはCounterとの比較、更新後の木の構造、ノード再利用、全優先度が同じ場合、空区間、Noneを値に持つ場合を検査する。

## 比較条件

公式APIから、取得時に最新テストでACのPyPy提出を時間順で取得し、sourceを確認してから実行した。

| 問題 | 比較提出 | 取得時のjudge時間 |
| --- | --- | ---: |
| nim_product_64 | [249477](https://judge.yosupo.jp/submission/249477) | 1.004秒 |
| majority_voting | [291308](https://judge.yosupo.jp/submission/291308) | 2.589秒 |

- WSL2、AMD Ryzen 7 3700X、PyPy 3.10.14 / 7.3.16。同じ公式入力を同じ実行環境で比較。
- 1プロセスずつ、各ケース5回。実装順を入れ替え、起動・JIT・入出力を含む時間の中央値を使う。
- 各実行の出力を公式checkerで検査。時間上限・メモリ上限を変更してAC扱いにはしていない。比較時の監視timeoutは30秒、メモリ制限は強制せず最大RSSを記録した。
- judge時間とローカル時間は直接比較しない。全公式ケースの反復測定ではなく、比較表の3ケースずつが対象。
- treapの優先度は実行ごとに生成する乱数。乱数で変わるのは木の形と実行時間であり、答えは厳密。

## nim_product_64

単位は秒。

| 公式ケース | 変更前 | 採用版 | 比較提出 |
| --- | ---: | ---: | ---: |
| random_00 | 1.903 | 1.249 | 0.955 |
| large_00 | 2.357 | 1.359 | 0.921 |
| small_00 | 0.563 | 0.312 | 0.281 |

採用版は変更前の約0.55〜0.66倍の時間。この3ケースではすべて速くなったが、比較提出にはまだ約1.11〜1.48倍かかる。比較提出は多項式基底の表と展開した64bit式、専用の一括入力を使う。今回の実装は既存の16bit積から表を構築し、32bit部分積の関数を再利用した。専用入出力・式展開の追加効果は切り分けていない。

最大RSSは、random_00で変更前182.1MiB、採用版184.8MiB、比較提出158.8MiB。追加表は無償ではなく、小さい件数では初回の前計算が相対的に重くなる。8bit・16bit・32bitのみの利用には追加表を作らない。

- [同条件比較の全測定](../benchmarks/results/nim_product_64-comparison.json)
- [変更前の公式全件検証](../benchmarks/results/nim_product_64-before-lookup.json)
- [変更前の単独実行コード](../benchmarks/baselines/nim_product_64.py)
- [採用版の公式検証](../../verify/library_checker/results/nim_product_64.json)
- [採用版の遅かった3ケース・各5回](../../verify/library_checker/benchmarks/nim_product_64.json)

## majority_voting

単位は秒。メモリはプロセス全体の最大RSS。

| 公式ケース | 採用版 | 比較提出 | 採用版MiB | 比較提出MiB |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 2.620 | 3.38 | 196.8 | 359.7 |
| max_random_01 | 2.553 | 3.046 | 198.9 | 377.0 |
| top2_killer_00 | 1.059 | 1.425 | 177.0 | 149.5 |

今回の3ケースでは比較提出より速かった。最大入力のメモリも小さくできたが、top2_killerでは比較提出のほうが小さい。全入力で時間・メモリとも優位とは言わない。

候補の合成は、異なる値を同数ずつ打ち消す操作。一般には結合的なモノイドではないため、そのように書いていた説明を訂正した。過半数の値があるときに候補として残る性質を使い、最終的な出現回数で確認する。

- [同条件比較の全測定](../benchmarks/results/majority_voting-comparison.json)
- [公式検証](../../verify/library_checker/results/majority_voting.json)
- [遅かった3ケース・各5回](../../verify/library_checker/benchmarks/majority_voting.json)

## 再実行

```sh
pypy3 library_codex/tools/check_library_checker.py test majority_voting nim_product_64 --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py majority_voting nim_product_64 --official /path/to/library-checker-problems --repeat 5
```

比較提出の取得日時・sourceのSHA-256・問題version・各回の時間とRSS・入力hashは比較JSONに保存している。再取得時はSHA-256を照合し、取得したsourceを確認してから`official_comparison.py`へ渡す。
