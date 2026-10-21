# GF(2^64)畳み込みの検証

`BinaryFieldConvolution.multiply`はLibrary Checkerの`convolution_F_2_64`と同じ体・bit表現で畳み込む。上位段の定数乗算を4bit単位の表引きへ置き換え、最大公式入力のPyPy中央値を16.068秒から8.208秒へ短縮した。配布用コードの3回測定はすべて10秒以内で、公式checkerに一致した。

切り替え条件も調整した最終コードは、公式全51ケースをローカルの10秒制限内で通過した。全件検査で遅かった3ケースを各5回測り直しても、15回すべて10秒以内だった。オンライン提出とメモリ制限の強制は行っていない。

## 最新コードの全件検証と反復測定

2026-10-21、[全51ケースの検証](../../verify/library_checker/results/convolution_F_2_64.json)は最長7.899秒。ここで遅かった`gen_max_00`、`many_ones_01`、`random_01`を各5回、新しいPyPyプロセスで測り直した。

3ケースの中央値の最大は7.648秒、15回の最長は7.906秒、最大RSSは850,460 KiB（約831MiB）だった。すべて公式checkerに一致した。[各回の時間・RSS・hash](../../verify/library_checker/benchmarks/convolution_F_2_64.json)に、最終source、公式入力・出力、checker、実行環境と全件検証のhashを記録している。

```sh
pypy3 library_codex/tools/check_library_checker.py test convolution_F_2_64 --official /home/harurun/.cache/harurun-library-checker/problems
pypy3 library_codex/benchmarks/official_benchmark.py convolution_F_2_64 --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

## 定数乗算の線形変換表

2026-10-21、Git `a5d2d17`と同じ処理の保存済み単独コードと、新しい配布用コードを同一環境・同一入力で比較した。各3回、新しいPyPyプロセスで起動・JIT・入出力を含め、実行順を入れ替えている。

| 最大入力 gen_max_00 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前 | 16.068秒 | 795,900 KiB |
| 4bit表を上位15段に適用 | 8.208秒 | 778,300 KiB |

時間は約48.9%短縮し、最大RSSも約2.2%減少した。採用版の3回は8.048〜8.239秒だった。過去の測定日との絶対時間の差から速度比を求めてはいない。

もう一つの大きいケース`gen_2_x_3_11_01`は15.925秒から8.138秒へ短縮した。採用版は7.977〜8.505秒、最大RSSは757,016 KiBから744,396 KiB。2ケースの新旧各3回、計12回答が公式checkerに一致し、採用版6回はすべて10秒以内だった。

体の定数cとの乗算は、64bit列上の線形変換になる。入力を4bitずつに分け、各位置の16通りの積を表から読み、XORで足せば同じ積になる。符号付き64bit整数で保持するが、各部分はシフト後に15でマスクするため、符号によってbit列は変わらない。

定数もCantor基底のXORで構成される。基底定数の表だけ体の乗算で作り、残りの表は既存の2表をXORして構築する。大きな整数の乗算と展開・圧縮は下位段と係数同士の積に限る。FFT本体は共通化し、上位段だけこの乗算を選ぶ。近似や確率的な判定は使わない。

表は上位15段までに制限し、各呼出し内で生成する。64bitの数値データだけなら最大約32MiBで、別途listの管理領域が必要になる。下位段は32要素以下の区画で処理する。公開API、扱う体、返り値の長さは変更しない。

- [配布用コードの反復比較とhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-linear-production-comparison.json)
- [14・15・16段の3回比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-nibble-comparison.json)
- [表の幅の比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-linear-width-screen.json)
- [8bit表の適用段数の比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-linear-depth-screen.json)

16段まで表にする試作は中央値8.177秒・最大875,948 KiB、15段は8.132秒・782,280 KiBだった。速度の上積みがなくメモリが増えたため、15段を選んだ。これらはFFT処理を共通化する前の試作であり、配布用コードの測定とは区別する。

5bit間隔の整数を条件に応じて分割する案は23.060秒で、同時比較の変更前17.267秒より遅かった。8bit間隔に広げ、整数乗算の桁数を保ったまま還元する案も16.712秒で、変更前15.554秒より遅かった。3段融合だけの改善は小さく、採用しない。[演算方式の予備比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-arithmetic-screen.json)、[整数還元の比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-integer-fold-screen.json)、[最初の表引き比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-linear-screen.json)と各候補のコードを保存している。これらの予備比較は各1回。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/binary_field_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_F_2_64 --cases gen_max_00 gen_2_x_3_11_01 --variant baseline=library_codex/benchmarks/experiments/binary_field_fold_tile256.py --variant candidate=verify/library_checker/solutions/convolution_F_2_64.py --repeat 3 --seed 21983 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-linear-production-comparison.json
```

## 長さが偏った入力の切り替え

上位段を高速化した直後の全51ケース検査では49件が10秒以内、`random_02`と`random_03`が時間超過になった。長さの比が4以上なら従来のブロック処理を選んでいたため、これらは新しい上位段の表を使っていなかった。

短い側が2,048項を超え、長い側がその32倍未満の場合も、新しい変換を使うようにした。短い側が小さい場合や32倍以上に偏る場合はブロック処理を残す。境界の2,048／2,049項、長さの比32の前後、引数を逆にした場合を独立した旧実装と比較する。

| 公式ケース | 配列長 | 切り替え前の中央値 | 切り替え後の中央値 | 前／後の最大RSS |
| --- | --- | ---: | ---: | ---: |
| random_02 | 53,336・382,347 | 10.736秒 | 3.855秒 | 452,336／402,336 KiB |
| random_03 | 429,249・25,839 | 11.548秒 | 3.826秒 | 431,716／415,012 KiB |

各3回、計12回答が公式checkerに一致した。[比較記録とhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-unbalanced-comparison.json)。上の最大入力の比較はこの切り替えを加える前の記録であり、最新の配布コードのhashと全件検証は[公式検証結果](../../verify/library_checker/results/convolution_F_2_64.json)を参照する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/binary_field_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_F_2_64 --cases random_02 random_03 --variant baseline=library_codex/benchmarks/experiments/binary_field_nibble_shared.py --variant candidate=library_codex/benchmarks/experiments/binary_field_linear_unbalanced.py --repeat 3 --seed 21985 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-unbalanced-comparison.json
```

## 還元の表引き

2026-10-21、Git `767e374`の実装と最大公式入力`gen_max_00`で各3回比較した。順序を入れ替え、新しいPyPyプロセスで起動・JIT・入出力を含めて測定した。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 変更前 1024要素区画 | 18.787秒 | 775,300 KiB |
| 256要素区画のみ | 17.953秒 | 781,876 KiB |
| 還元表のみ | 16.246秒 | 788,752 KiB |
| 還元表と256要素区画 | 15.299秒 | 796,108 KiB |

最後の組合せを採用する。中央値は約18.6%短縮、最大RSSは約2.7%増加した。12回答すべてが公式checkerに一致した。過去の別測定の絶対時間とは速度比を取らない。

64次未満の多項式同士の積は高々126次。最初の還元後に64次以上へ残る部分は高々2次であり、6bit間隔の表現では添字0〜4161に収まる。最後のシフトとXORを4162項の固定表へ置き換えた。可能な8通りをすべて検査し、高位bitの積とcarryless積の独立実装でも照合する。

- [3回ずつの時間・RSS・hash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-fold-comparison.json)
- [採用した単独コード](../benchmarks/experiments/binary_field_fold_tile256.py)
- [初回の候補比較](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-layout-screen.json)

初回比較では、還元の整数乗算をシフトとXORへ置き換える案は18.803秒から21.880秒へ悪化した。ゼロの最上段を複製で省く案は18.619秒で差が小さく、RSSが増えた。4096要素区画も19.546秒だった。これらは採用しない。試作コードと入力・出力のhashは比較記録に残す。

5bit間隔へ縮めて上位・下位32bitの2回に分けて掛ける案も試した。32bitすべて1の部分がある場合はcarryless積を直接計算し、桁上がりを無視しない。境界値と公式最大入力の回答は一致したが、1回の予備比較では採用版15.322秒に対して19.045秒だった。RSSは796,028 KiBから738,864 KiBへ減ったものの、今回は速度優先で採用しない。[測定記録](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-fivebit-screen.json)と[試作](../benchmarks/experiments/binary_field_fivebit_split.py)を保存する。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/binary_field_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_F_2_64 --cases gen_max_00 --variant baseline=library_codex/benchmarks/experiments/binary_field_tiled.py --variant tile256=library_codex/benchmarks/experiments/binary_field_tile256.py --variant fold=library_codex/benchmarks/experiments/binary_field_fold_table.py --variant fold256=library_codex/benchmarks/experiments/binary_field_fold_tile256.py --repeat 3 --seed 21961 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-fold-comparison.json
```

## 還元表を追加した時点の最大入力以外の比較

最大ランダム以外の公式3ケースも、旧版と配布用コードで各3回比較した。全18回答が一致した。全要素が等しいケースでは中央値が約0.048秒増えており、すべての入力で高速化したわけではない。

| ケース | 変更前 | 採用版 |
| --- | ---: | ---: |
| gen_2_x_3_11_01 | 18.016秒 | 15.011秒 |
| small_and_large_00 | 5.156秒 | 4.501秒 |
| all_ones_00 | 1.159秒 | 1.207秒 |

[各回の値とhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-fold-regression.json)。今回の反復比較の対象は計4/51ケースであり、全件通過の検査ではない。

## 測定環境

- 公式問題revision: `1814c4e5205517e368bb57a8d1127eb961cfeaae`。
- WSL2・AMD Ryzen 7 3700X・PyPy 3.10.14 / 7.3.16。
- 公式入力・期待出力のhashを照合し、提出用standaloneを新しいPyPyプロセスで実行。出力を公式checkerで検査する。
- 壁時計時間は起動・JIT・入出力込み。RSSはGNU time。メモリ制限の強制やオンライン提出は行っていない。
- 診断用timeoutは120秒。出力一致と公式10秒以内の判定を分ける。延長測定を全件通過一覧へ混ぜない。

## 実装

Cantor基底による加法FFTを使う。FFT自体は`O(S log S)`回の体演算、今回の通常基底との変換は`O(S log^2 S)`時間が上界。Sは出力長以上の最小の2の冪。

体の係数を6bit間隔へ展開し、整数乗算後の各桁の偶奇からcarryless積を取り出す。桁上がりが起きる唯一の入力対は別処理する。t^64+t^4+t^3+t+1による剰余を取り、展開表現のままFFTを続ける。整数mod 2^64やnim積へ置き換えていない。

基底生成の初期値`1 << 61`は、この体でtraceが1になるtの61乗。二乗して元の値とXORする操作を63回たどると1になり、逆順に並べた64要素がCantor基底になる。この関係と線形独立性は専用testで確認する。

係数列が等しい場合は、標数2なので偶数番目へ各係数の二乗を書くだけでよい。別のlistやtupleでも係数が等しければこの処理を使う。長さが4倍以上異なる場合は短い側に合わせて分割し、その変換を再利用する。これらは入力の形から選ぶ一般の処理で、公式ケース名による分岐はない。

## C++上位提出と採用した変更

2026-10-20に、公式APIの最新問題版・AC・C++23を時間順に取得した。[409339](https://judge.yosupo.jp/submission/409339)と[409295](https://judge.yosupo.jp/submission/409295)を調べ、[順位・日時・source hash](../benchmarks/results/binary_field_cpp_reference.json)を保存した。他のC++言語IDを含む全体順位ではない。C++のjudge時間とローカルPyPyの時間は直接比較しない。

参照実装はCantor基底の加法FFTに、2〜3段の融合、キャッシュ内での変換と積の処理、疎な入力の省略、専用のcarryless乗算命令、SIMD入出力を組み合わせる。今回は命令列や外部packageを追加せず、次を独立に実装した。

- FFTの2段をまとめ、配列の読み書きを減らす。係数0の最初のブロックでは不要な体の乗算を省く。
- 基底変換のXORを、依存しない半分ごとにまとめる。入力は必要な2冪長で基底変換してから、積の長さまで0を補う。
- XORだけの基底変換では符号付き64bit整数を使い、PyPyが通常の整数listとして処理できるようにする。FFTに入るときだけ7bit間隔の表現へ展開する。返り値は従来どおり符号なし64bit。
- 同じobjectに限らず、係数列が等しい場合も二乗として線形時間で求める。

符号付き表現は同じ64個のbitの読み方を変えるだけであり、別の体への変換や64bitを超えた切り捨てではない。最上位bitを含む境界値、変換の往復、旧基底変換との一致をtestする。

## 乗算の6bit幅への圧縮

従来の7bit幅を6bit幅へ縮め、乗算する整数を最大448bitから384bitへ減らす。整数積の各桁に加わる項数は、中央の63次だけ最大64、それ以外は最大63。63次で64になるのは、入力2個がともに64bitすべて1のときだけである。

この1組だけは標数2の二乗として偶数次に1を並べてから剰余を取る。それ以外では各桁が64未満なので、隣の桁へのcarryはない。剰余計算の乗算は最大4項の和なので6bit幅で収まる。確率的に桁上がりを無視する方法ではない。

全bitが1の値、そこから1bitを落とした64種類、0、1のすべての組とランダム1,000組をcarryless積の単純解と比較する。これらを係数に含む畳み込みも7bit版と照合する。

## 1024要素区画を採用した時点の比較

2026-10-21、Git `498a2ce`の7bit版、6bit版、6bit化と区画分割を加えた版を、最大公式入力`gen_max_00`で各3回比較した。

全体の上位段を変換した後、1024要素以下の区画ごとに2列の下位段、係数ごとの積、積の下位逆変換を済ませる。最後に上位逆変換を行う。C++上位提出のキャッシュ内で処理をまとめる方式を参考にしたが、機械語のcarryless乗算やSIMDは使わない。新たな再帰や要素ごとのobjectは追加しない。

| 実装 | 中央値 | 最大RSS |
| --- | ---: | ---: |
| 7bit版 | 21.666秒 | 826,840 KiB |
| 6bit版 | 20.662秒 | 785,824 KiB |
| 6bit化と区画分割 | 20.083秒 | 775,124 KiB |

最後の版を採用。時間は約7.3%、最大RSSは約6.3%減少した。全9回答が公式checkerに一致した。[各回の値とhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-tiled-comparison.json)、[7bit版](../benchmarks/baselines/binary_field_signed.py)、[6bit版](../benchmarks/experiments/binary_field_sixbit.py)、[区画分割版](../benchmarks/experiments/binary_field_tiled.py)を保存する。

その前の6bit単独比較では25.387秒から22.428秒だったが、両実装の初回が遅かった。初回も削除せず[元の測定](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-sixbit-comparison.json)へ残し、採用判断は上表の追加比較でも改善が出たことに基づく。日をまたいだ過去の20.027秒とは直接比べない。

同じ7bit版と採用版の提出コードを、形の異なる公式2ケースでも各3回比較した。全12回答が一致した。[測定記録](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-sixbit-regression-comparison.json)。

| ケース | 7bit版の中央値 | 採用版の中央値 | 7bit版の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| all_ones_00 | 1.488秒 | 1.215秒 | 260,540 KiB | 259,640 KiB |
| small_and_large_00 | 5.640秒 | 5.288秒 | 350,196 KiB | 334,808 KiB |

さらに採用版の提出コードで`example_00`、`example_01`、`small_16`、`medium_02`、`small_and_large_01`、`gen_2_x_3_11_01`を各1回確認した。6回答とも一致し、最後のケースだけ20.072秒で公式10秒制限を超過した。[選択検査](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-sixbit-probe.json)。最大入力の比較と合わせて9/51ケースの確認であり、全件通過ではない。

```sh
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/binary_field_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_F_2_64 --cases gen_max_00 --variant baseline=library_codex/benchmarks/baselines/binary_field_signed.py --variant sixbit=library_codex/benchmarks/experiments/binary_field_sixbit.py --variant tiled=library_codex/benchmarks/experiments/binary_field_tiled.py --repeat 3 --seed 21957 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-tiled-comparison.json
```

## 7bit段融合版の比較

Git `120cdb8`と採用版を、同じ公式入力・別processで各3回比較した。

| ケース | 変更前の中央値 | 採用版の中央値 | 変更前の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| gen_max_00 | 31.245秒 | 20.027秒 | 884,992 KiB | 827,196 KiB |
| all_ones_00 | 24.614秒 | 1.357秒 | 899,076 KiB | 260,544 KiB |
| small_and_large_00 | 5.201秒 | 5.260秒 | 360,168 KiB | 350,240 KiB |

最大ケースは約35.9%短縮。等しい係数列の二乗は約18.1倍になったが、一般の入力への速度比ではない。長さの偏ったケースでは改善はない。全18回答が公式checkerに一致した。[各回の値とhash](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-signed-comparison.json)・[変更前の単独コード](../benchmarks/baselines/binary_field_before_fusion.py)を保存した。

さらに`example_00`、`example_01`、`small_16`、`medium_02`、`small_and_large_01`、`gen_2_x_3_11_01`を各1回検査し、すべて出力が一致した。最後のケースは19.538秒で10秒制限を超過した。[選択検査の記録](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-optimized-probe.json)。

今回確認した入力は合計9/51ケース。うち7ケースは10秒以内、最大ランダムと`gen_2_x_3_11_01`は制限超過。公式全件の通過は確認していない。

## 64bit化前の段融合の比較

Git `120cdb8`と、段融合・ゼロ部分の省略・等しい係数列の二乗を加えた段階を各3回比較した。基底変換はまだ7bit間隔の大整数で実行している。

| ケース | 変更前の中央値 | 段融合までの中央値 | 変更前の最大RSS | 段融合までの最大RSS |
| --- | ---: | ---: | ---: | ---: |
| gen_max_00 | 31.685秒 | 26.952秒 | 884,996 KiB | 869,884 KiB |
| all_ones_00 | 24.772秒 | 1.675秒 | 899,260 KiB | 298,544 KiB |
| small_and_large_00 | 5.235秒 | 5.246秒 | 360,212 KiB | 362,048 KiB |

全18回答が公式checkerに一致。[測定値](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-fused-comparison.json)と[この段階の単独コード](../benchmarks/experiments/binary_field_fused_standalone.py)を保存した。`all_ones_00`の改善は等しい係数列の二乗によるもので、一般の入力への速度比ではない。

## 見送った試作

`benchmarks/experiments`へ残した次の案は、今回の通常実装には組み込んでいない。

- `binary_field_packed.py`: 同じ係数を掛ける16要素を大整数へ詰めてFFTを行う。展開・取り出しと下位段の処理が残り、単発の探索では採用できる差が出なかった。
- `binary_field_taylor.py`: C++版のTaylor展開による基底変換を平坦な操作列で実装。PyPyでは小さな区間ごとのループが多く、今回の形では採用しなかった。
- `binary_field_bulk.py`: 基底変換を巨大な整数へのmaskとshiftでまとめる。mask生成と大きな整数の走査が重く、符号付き64bitのlist上のXORを選んだ。

`convolution_trial.py`で正解照合と工程別の探索測定を再実行できる。初回JITや計測用wrapperを含むため、採否の速度比には公式入力での別process比較を使う。

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

## 段融合前の選択検査

公式全51ケースのうち9ケースを各1回実行し、9回答すべてが公式checkerと一致した。6ケースは10秒以内、次の3ケースは制限超過だった。

| ケース | 時間 | 最大RSS |
| --- | ---: | ---: |
| gen_max_00 | 31.265秒 | 885,064 KiB |
| gen_2_x_3_11_01 | 28.782秒 | 870,364 KiB |
| all_ones_00 | 24.701秒 | 898,812 KiB |

1000項と524,288項の`small_and_large_01`は7.963秒・364,264 KiB。これは単発値で、前節の3回測定とは区別する。残りのケース名、時間、hashは[選択検査の全記録](../../verify/library_checker/benchmarks/comparisons/convolution_F_2_64-current-probe.json)にある。

この時点では公式全件の検査は未実行。`convolution_mod_large`の更新は[大規模畳み込みの比較記録](LARGE_CONVOLUTION_BENCHMARK.md)を参照。

## 再実行

リポジトリ直下で実行する。公式生成器とcheckerのためにC++環境、時間とRSSのためにLinuxのGNU timeが必要。

```sh
pypy3 -m pytest -q library_codex/verify/convolution/test_binary_field_convolution.py
pypy3 library_codex/benchmarks/official_probe.py convolution_F_2_64 --official /home/harurun/.cache/harurun-library-checker/problems --cases example_00 example_01 small_16 medium_02 small_and_large_01 gen_2_x_3_11_01 --repeat 1 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-optimized-probe.json
pypy3 library_codex/benchmarks/official_comparison.py --snapshot library_codex/benchmarks/baselines/binary_field_snapshot.json --problem /home/harurun/.cache/harurun-library-checker/problems/convolution/convolution_F_2_64 --cases gen_max_00 all_ones_00 small_and_large_00 --variant baseline=library_codex/benchmarks/baselines/binary_field_before_fusion.py --variant candidate=verify/library_checker/solutions/convolution_F_2_64.py --repeat 3 --timeout 120 --output verify/library_checker/benchmarks/comparisons/convolution_F_2_64-signed-comparison.json
```

`official_probe.py`は、診断timeout内に正しい出力が得られても、公式制限を超えれば終了code 1を返す。

## 2026-10-20の検証内容

専用testでは、carryless積の単純解、64個の基底の独立性と関係式、FFT値と直接の多項式評価、基底変換の往復、畳み込みの単純解、双線形性、非破壊、空列、二乗、不正な係数、末尾0、単独bundleを検査する。

今回追加した検査では、融合前後のFFT・基底変換の一致、符号付き64bit境界、等しい別配列の二乗も確認する。大規模畳み込みと合わせた専用18件が成功した。

2026-10-20の全体回帰testは1,289件成功し、full性能回帰検査も通過した。API・catalog・提出コード・Codon索引の同期検査と説明品質監査も成功。全体検査で見つかった同名testの読込衝突は、リポジトリ直下の`pytest.ini`でimportlib方式に揃え、別categoryと標準moduleの名前が衝突しないことを検査した。これはLibrary Checkerの公式全件通過とは別の検査である。

## 参照

- [公式の問題・実装](https://github.com/yosupo06/library-checker-problems/tree/1814c4e5205517e368bb57a8d1127eb961cfeaae/convolution/convolution_F_2_64)
- [Lin・Chung・Hanの多項式基底と加法FFT](https://arxiv.org/abs/1404.3458)
- [8bit間隔での初期試作](../benchmarks/experiments/binary_field_convolution.py)。各乗算で展開・圧縮する形と、途中で展開表現を保つ形の小入力比較器を含む。最大入力の公式制限通過を示すものではない。
