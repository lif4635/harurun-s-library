# GF(2^64)畳み込みの検証

`BinaryFieldConvolution.multiply`はLibrary Checkerの`convolution_F_2_64`と同じ体・bit表現で畳み込む。選択した公式入力で出力一致を確認したが、最大ケースの公式10秒制限は未達で、全件通過ではない。

## 条件

- 公式問題revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
- WSL2・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。
- 公式入力・期待出力のhashを照合し、提出用standaloneを新しいPyPyプロセスで実行。出力を公式checkerで検査する。
- 壁時計時間は起動・JIT・入出力込み。RSSはGNU time。メモリ制限の強制やオンライン提出は行っていない。
- 診断用timeoutは120秒。出力一致と公式10秒以内の判定を分ける。延長測定を全件通過一覧へ混ぜない。

## 実装

Cantor基底による加法FFTを使う。FFT自体は`O(S log S)`回の体演算、今回の通常基底との変換は`O(S log^2 S)`時間が上界。Sは出力長以上の最小の2の冪。

体の係数を7bit間隔へ展開し、整数乗算後の各桁の偶奇からcarryless積を取り出す。1桁に加わる積は最大64個で、7bit以内に収まる。t^64+t^4+t^3+t+1による剰余を取り、展開表現のままFFTを続ける。整数mod 2^64やnim積へ置き換えていない。

基底生成の初期値`1 << 61`は、この体でtraceが1になるtの61乗。二乗して元の値とXORする操作を63回たどると1になり、逆順に並べた64要素がCantor基底になる。この関係と線形独立性は専用testで確認する。

同じobjectを渡す二乗では、標数2なので偶数番目へ各係数の二乗を書くだけでよい。長さが4倍以上異なる場合は短い側に合わせて分割し、その変換を再利用する。これらは入力の形から選ぶ一般の処理で、公式ケース名による分岐はない。

## 初期版の選択検査

次の7ケースを各1回実行し、全出力が一致した。

`example_00`、`example_01`、`small_16`、`medium_02`、`gen_max_00`、`small_and_large_00`、`all_ones_00`。

最大ケースは30.860秒・884,344 KiB。100項と524,288項のケースは25.369秒・821,460 KiB。`all_ones_00`も24.346秒で、これら3ケースは10秒を超過した。

[全測定値とhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-initial-probe.json)・[その時点の単独コード](../benchmarks/baselines/binary_field_unblocked.py)を保存した。

## 長さが異なる入力の分割

新旧を同じ公式入力、新しいPyPyプロセスで各3回、実行順を入れ替えて比較した。単発の初期測定との差を速度比には使わない。

| ケース | 分割なしの中央値 | 採用版の中央値 | 分割なしの最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| small_and_large_00 | 25.277秒 | 5.027秒 | 821,012 KiB | 360,168 KiB |
| gen_max_00 | 31.045秒 | 31.099秒 | 884,536 KiB | 885,116 KiB |

100項と524,288項の組合せでは、約5.0倍速くなり、採用版は3回とも10秒以内。全12回答が公式checkerを通った。524,288項ずつの最大ケースでは処理経路は変わらず、約31秒のまま。最大ケースを高速化したとは扱わない。

[各回の時間・RSS・sourceと入出力のhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-block-comparison.json)。

## 採用版の選択検査

公式全51ケースのうち9ケースを各1回実行し、9回答すべてが公式checkerと一致した。6ケースは10秒以内、次の3ケースは制限超過だった。

| ケース | 時間 | 最大RSS |
| --- | ---: | ---: |
| gen_max_00 | 31.265秒 | 885,064 KiB |
| gen_2_x_3_11_01 | 28.782秒 | 870,364 KiB |
| all_ones_00 | 24.701秒 | 898,812 KiB |

1000項と524,288項の`small_and_large_01`は7.963秒・364,264 KiB。これは単発値で、前節の3回測定とは区別する。残りのケース名、時間、hashは[選択検査の全記録](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-current-probe.json)にある。

公式全件の検査は未実行。`convolution_mod_large`も前回の時間制限未達を引き継いでおり、今回その実装・測定値は変更していない。

## 再実行

リポジトリ直下で実行する。公式生成器とcheckerのためにC++環境、時間とRSSのためにLinuxのGNU timeが必要。

```sh
pypy3 -m pytest -q library_codex/verify/convolution/test_binary_field_convolution.py
pypy3 library_codex/benchmarks/official_probe.py convolution_F_2_64 --official /home/harurun/.cache/harurun-library-checker/problems --cases example_00 example_01 small_16 medium_02 gen_max_00 small_and_large_00 small_and_large_01 all_ones_00 gen_2_x_3_11_01 --repeat 1 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-current-probe.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/binary_field_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_F_2_64 --cases small_and_large_00 gen_max_00 --variant unblocked=library_codex/benchmarks/baselines/binary_field_unblocked.py --variant candidate=verify/library_checker/solutions/convolution_F_2_64.py --repeat 3 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-block-comparison.json
```

`official_probe.py`は、診断timeout内に正しい出力が得られても、公式制限を超えれば終了code 1を返す。

## 検証内容

専用testでは、carryless積の単純解、64個の基底の独立性と関係式、FFT値と直接の多項式評価、基底変換の往復、畳み込みの単純解、双線形性、非破壊、空列、二乗、不正な係数、末尾0、単独bundleを検査する。

専用7件を含むquick検査348件と性能回帰検査が成功した。API・catalog・提出コード・Codon索引の同期、説明品質、非再帰の監査も通過。サイトはビルドと59件のtestが成功し、全402モジュールのページ描画とコピー用コードを確認した。全ライブラリのfull検査は再実行していない。

## 参照

- [公式の問題・実装](https://github.com/yosupo06/library-checker-problems/tree/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_F_2_64)
- [Lin・Chung・Hanの多項式基底と加法FFT](https://arxiv.org/abs/1404.3458)
- [8bit間隔での初期試作](../benchmarks/experiments/binary_field_convolution.py)。各乗算で展開・圧縮する形と、途中で展開表現を保つ形の小入力比較器を含む。最大入力の公式制限通過を示すものではない。
