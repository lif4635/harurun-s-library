# 大規模畳み込みの検証

`LargeConvolution.multiply`は998244353上で、出力が2^23項を超える積を求める。4列分割に加え、逆NTT後の保存方法を変えて最大公式入力のRSSを約1002MiBから746MiBへ減らした。最新の比較では中央値16.29秒で、公式10秒制限には届いていない。

## 条件

- 公式問題revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
- WSL2・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。
- 入出力は公式hashと照合。提出用standaloneを新しいPyPyプロセスで起動し、出力は公式checkerで検査する。
- 壁時計時間には起動・JIT・入出力を含む。RSSはGNU timeで測る。メモリ制限の強制、オンライン提出は行っていない。C++上位提出は方式の参照であり、同じ環境での速度比較ではない。
- 公式全54ケースのうち、選択したケースだけを生成・測定する。診断用の時間上限と公式制限を区別する。

## C++上位提出を参考にした4列分割

2026-10-20に公式APIで、最新問題版のAC・C++23を時間順に取得した。[409657](https://judge.yosupo.jp/submission/409657)と[409616](https://judge.yosupo.jp/submission/409616)を確認し、順位・取得日時・source hashを[取得記録](../benchmarks/results/large_convolution_cpp_reference.json)へ保存した。他のC++言語IDを含めた全体順位とは区別する。

参照実装はNTTを途中で止め、葉で8次未満の多項式を掛ける。AVX2・専用の入出力・キャッシュ内での変換処理も使う。PyPy版では外部packageや機械語を追加せず、4次未満の多項式を掛ける部分を独立に実装した。

入力を添字の4剰余で分ける。

$$
A(x)=\sum_{r=0}^{3}x^r A_r(x^4)
$$

各列を長さSでNTTし、その評価点wごとに次を求める。

$$
\left(\sum_{r=0}^{3}a_r x^r\right)
\left(\sum_{r=0}^{3}b_r x^r\right)\bmod(x^4-w)
$$

4列を逆変換して交互に並べると元の積になる。最大入力ではS=2^23で、順NTTは8回、逆NTTは従来の7回から4回へ減る。入力・出力の意味は変えない。同じobjectの二乗では順NTTを4回へ減らす。従来のブロック分割の方が変換回数の少ない形では切り替えない。

変更前はGit `120cdb8`。各3回、新規PyPyプロセスで順序を入れ替え、全12回答を公式checkerで検査した。

| ケース | 変更前の中央値 | 採用版の中央値 | 変更前の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| max_random_00 | 19.216秒 | 15.713秒 | 1,015,912 KiB | 1,025,648 KiB |
| small_and_large_00 | 5.167秒 | 5.304秒 | 461,228 KiB | 461,076 KiB |

この段階の最大ケースは約18.2%短縮。片方100項の経路は変更しておらず、この比較でも改善はない。最大RSSは約1002 MiBだった。現在は次節の保存方法へ変更している。

[各回の値とhash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-comparison.json)・[変更前の単独コード](../benchmarks/baselines/large_convolution_before_interleaving.py)・[4列分割の試作](../benchmarks/experiments/large_convolution_interleaved.py)を保存した。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 small_and_large_00 --variant baseline=library_codex/benchmarks/baselines/large_convolution_before_interleaving.py --variant candidate=verify/library_checker/solutions/convolution_mod_large.py --repeat 3 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-interleaved-comparison.json
```

## 逆変換後のメモリ削減

2026-10-21、Git `498a2ce`を基準に最大公式入力`max_random_00`で各3回比較した。逆NTTの結果を既存の`array("I")`へ戻し、一時listを解放してから返却listを作る。4列の値は出力の隣接する4要素へまとめて書く。返り値の型・順序・値とNTT回数は変えない。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前 | 16.688秒 | 1,025,836 KiB |
| 保存方法変更後 | 16.290秒 | 763,576 KiB |

最大RSSは約25.6%減少。速度差は約2.4%で、初回は変更後の方が遅かったため、速度の大幅改善とは扱わない。メモリ制限ぎりぎりの状態を改善する目的で採用した。全6回答が公式checkerに一致した。前節とは別の測定であり、日をまたいだ絶対時間の差を速度比には使わない。

[各回の時間・RSS・hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-contiguous-comparison.json)、[変更前の単独コード](../benchmarks/baselines/large_four_lanes_standalone.py)、[比較した単独コード](../benchmarks/experiments/large_contiguous_standalone.py)を保存している。

採用版の提出コードでも`example_00`、`example_01`、`small_15`、`medium_00`、`small_and_large_00`、`small_and_large_01`を各1回検査し、全6回答が一致して10秒以内だった。[選択検査の記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-contiguous-probe.json)。最大入力との比較を含め7/54ケースの確認で、全件通過ではない。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/large_convolution_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_mod_large --cases max_random_00 --variant baseline=library_codex/benchmarks/baselines/large_four_lanes_standalone.py --variant contiguous=library_codex/benchmarks/experiments/large_contiguous_standalone.py --repeat 3 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-contiguous-comparison.json
```

## 初期実装

以下は変更前の実装の記録で、採用版との同時比較ではない。

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

ブロック解放は速度と引き換えにメモリを減らす変更として採用した。[比較結果](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-memory-comparison.json)と[その段階の単独コード](../benchmarks/experiments/large_convolution_release_only.py)を保存した。その後、作業配列の再利用、片方が短い場合の逐次処理を加えた。次の表は4列分割を加える前の測定で、上の旧実装との同時比較ではない。

## 4列分割を加える前の選択検査

公式7ケースを3回ずつ、計21回測定し、すべての出力が公式checkerと一致した。10秒制限を満たしたのは最大ランダム以外の6ケース。最大ランダムは3回とも制限超過である。

| 公式ケース | 入力長 | 中央値 | 最大RSS |
| --- | --- | ---: | ---: |
| max_random_00 | 2^24と2^24 | 20.231秒 | 1,015,008 KiB |
| small_and_large_00 | 100と2^24 | 5.602秒 | 461,176 KiB |
| small_and_large_01 | 1000と2^24 | 6.229秒 | 462,488 KiB |

残りは`example_00`・`example_01`・`small_15`・`medium_00`。最大ケースの時間は18.860〜20.343秒にばらついた。速度優先の旧試作へ戻すだけでも10秒には届かない。

[全21回の値・source hash・入力hash](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-current-probe.json)を保存した。公式全件の検証結果や、全件通過済み問題のベンチマーク一覧には混ぜていない。

この段階では通常のquick検査339件と性能回帰検査を通過した。

## 採用版の選択検査

最大ランダムと`small_and_large_00`の反復比較に加え、`example_00`、`example_01`、`small_15`、`medium_00`、`small_and_large_01`を各1回検査した。5回答とも公式checkerに一致し、10秒以内。`small_and_large_01`は6.166秒・462,304 KiBだった。[選択検査の記録](../../verify/library_checker/benchmarks/comparisons/convolution_mod_large-optimized-probe.json)。

今回確認した入力は合計7/54ケース。最大ランダムは制限超過で、公式全件の通過は確認していない。専用testは、4列分割の単純解との比較、変換回数、負の係数、入力の非破壊、単独bundleを含み、GF(2^64)畳み込みと合わせて18件が成功した。

2026-10-20の全体回帰testは1,289件成功し、full性能回帰検査も通過した。API・catalog・提出コード・Codon索引の同期検査と説明品質監査も成功した。

## 再実行

リポジトリ直下で実行する。診断用に上限を延ばしても、公式制限超過の判定は残る。

```sh
pypy3 library_codex/benchmarks/official_probe.py convolution_mod_large --official /home/harurun/.cache/harurun-library-checker/problems --cases example_00 example_01 small_15 medium_00 small_and_large_01 --repeat 1 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_mod_large-optimized-probe.json
```

## 残る問題

- 大規模畳み込みの全公式ケース検証と、最大ケースの10秒制限。
- `convolution_F_2_64`は別の問題。整数を2^64で割った余りの畳み込みでもnim積でもなく、二元体上の既約多項式による剰余体を使う。加法FFTを使うPyPy版は`BinaryFieldConvolution`へ追加した。[検証と未達の範囲](BINARY_FIELD_CONVOLUTION_BENCHMARK.md)を参照。

## 参照

- [大規模畳み込みの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_mod_large/sol/correct.cpp)
- [GF(2^64)畳み込みの公式実装](https://github.com/yosupo06/library-checker-problems/blob/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_F_2_64/sol/correct.cpp)
