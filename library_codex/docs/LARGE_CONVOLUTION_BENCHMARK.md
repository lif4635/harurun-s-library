# 大規模畳み込みの検証

`LargeConvolution.multiply`は998244353上で、出力が2^23項を超える積をブロック分割で求める。Library Checkerの`convolution_mod_large`について、最大ケースの出力一致を確認したが、公式10秒制限には届いていない。全件通過ではない。

## 条件

- 公式問題revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
- WSL2・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。
- 入出力は公式hashと照合。提出用standaloneを新しいPyPyプロセスで起動し、出力は公式checkerで検査する。
- 壁時計時間には起動・JIT・入出力を含む。RSSはGNU timeで測る。メモリ制限の強制、オンライン提出、上位提出との比較は行っていない。
- 公式全54ケースのうち、選択したケースだけを生成・測定する。診断用の時間上限と公式制限を区別する。

## 初期実装

`example_00`・`example_01`・`small_15`・`medium_00`は通過。`max_random_00`は10秒でtimeoutした。

診断上限を300秒へ延ばした同じ最大ケースは17.584秒で出力が一致した。最大RSSは1,156,148 KiB。入力は2^24項の列が2本、出力は2^25-1項。

関数の前後を計時した別実行では、全体18.025秒、入力2.006秒、順NTT6.857秒、逆NTT5.948秒、畳み込み全体15.021秒だった。順変換8回・逆変換7回であり、ブロックの組ごとに変換し直してはいない。この内訳は計測用wrapper付きのimport実行で、standaloneの時間とは区別する。

- [10秒制限の選択検査](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-probe.json)
- [最大ケースの延長測定](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-extended-probe.json)
- [処理時間の内訳](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-profile.json)
- [初期実装の単独コード](../benchmarks/baselines/large_convolution_unplanned.py)

## 比較した変更

同じ最大ケースを各実装3回、新しいプロセスで順序を入れ替えて測った。全出力が公式checkerを通過した。

| 比較 | 変更前の中央値 | 変更後の中央値 | 変更前の最大RSS | 変更後の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| 回転係数表の共有 | 17.589秒 | 17.142秒 | 1,147,664 KiB | 1,215,376 KiB |
| 出力の逐次追加とブロック解放 | 18.071秒 | 19.257秒 | 1,154,796 KiB | 990,792 KiB |

係数表の共有は速度差が小さく、メモリが増えたため不採用。[比較結果](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-plan-comparison.json)と[試作コード](../benchmarks/experiments/large_convolution_planned.py)を残す。

ブロック解放は速度と引き換えにメモリを減らす変更として採用した。[比較結果](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-memory-comparison.json)と[その段階の単独コード](../benchmarks/experiments/large_convolution_release_only.py)を保存した。その後、作業配列の再利用、片方が短い場合の逐次処理を加えた。次の表が現在のsourceに対する測定で、上の旧実装との同時比較ではない。

## 採用版の選択検査

公式7ケースを3回ずつ、計21回測定し、すべての出力が公式checkerと一致した。10秒制限を満たしたのは最大ランダム以外の6ケース。最大ランダムは3回とも制限超過である。

| 公式ケース | 入力長 | 中央値 | 最大RSS |
| --- | --- | ---: | ---: |
| max_random_00 | 2^24と2^24 | 20.231秒 | 1,015,008 KiB |
| small_and_large_00 | 100と2^24 | 5.602秒 | 461,176 KiB |
| small_and_large_01 | 1000と2^24 | 6.229秒 | 462,488 KiB |

残りは`example_00`・`example_01`・`small_15`・`medium_00`。最大ケースの時間は18.860〜20.343秒にばらついた。速度優先の旧試作へ戻すだけでも10秒には届かない。

[全21回の値・source hash・入力hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-current-probe.json)を保存した。公式全件の検証結果や、全件通過済み問題のベンチマーク一覧には混ぜていない。

通常のquick検査339件と性能回帰検査を通過した。分割境界・単純解との比較・変換の再利用・入力の非破壊・bundle単独実行・診断スクリプトの失敗状態と終了codeを検査する専用13件も通過した。全ライブラリのfull検査は再実行していない。

## 再実行

リポジトリ直下で実行する。診断用に上限を延ばしても、公式制限超過の判定は残る。

```sh
pypy3 library_codex/benchmarks/official_probe.py convolution_mod_large --official /home/harurun/.cache/harurun-library-checker/problems --cases example_00 example_01 small_15 medium_00 max_random_00 --repeat 3 --timeout 60 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-current-probe.json
```

## 残る問題

- 大規模畳み込みの全公式ケース検証と、最大ケースの10秒制限。
- `convolution_F_2_64`は別の問題。整数を2^64で割った余りの畳み込みでもnim積でもなく、二元体上の既約多項式による剰余体を使う。加法FFTを使うPyPy版は`BinaryFieldConvolution`へ追加した。[検証と未達の範囲](BINARY_FIELD_CONVOLUTION_BENCHMARK.md)を参照。

## 参照

- [大規模畳み込みの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_mod_large/sol/correct.cpp)
- [GF(2^64)畳み込みの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_F_2_64/sol/correct.cpp)
