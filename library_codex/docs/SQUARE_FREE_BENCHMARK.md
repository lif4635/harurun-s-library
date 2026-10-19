# 平方因子を持たない整数の計数

`prime/Sieve.py`の`count_square_free(number)`は、1以上number以下で1以外の平方数を因子に持たない整数の個数を返す。関数名・引数・返り値を保ち、平方根まで線形ふるいを作る実装を置き換えた。

[Pawlewiczの論文](https://arxiv.org/abs/1107.4890)のAlgorithm 2を用い、Möbius関数の累積和で大きい範囲をまとめる。前計算の境界は約N^(2/5)。整数演算をO(1)として、O(N^(2/5) log log N)時間、O(N^(2/5))メモリ。論文後半のブロック分割による省メモリ版は採用していない。

## 検証

公式revision `1814c4e5205517e368bb57a8d1127eb961cfeaae`の`counting_squarefrees`を、公式生成器・checkerで25 / 25ケース検証した。上限は10^18、制限時間10秒。単発測定の最大は約1.16秒。

[専用test](../verify/prime/test_sieve.py)では、小さい整数の直接判定と比較し、五乗根・平方根の境界付近やランダムな入力を、平方根までのMöbius和と照合する。0以下の返り値と、10^12での値も検査する。

同じmoduleを含む`counting_primes`、`enumerate_primes`、`sum_of_totient_function`の提出コードも再生成し、公式全ケースと反復測定を更新した。

通常テスト309件とサイト45件が通過した。共通の性能検査では、今回変更していないCSR Dijkstraの速度比が初回1.033倍で基準1.05倍を下回った。同じ条件で性能検査のみ再実行すると1.243倍となり、全項目が通過した。基準やCSR実装は変更していない。

## 公式ケースの反復測定

PyPy 3.10.14 / 7.3.16、Ryzen 7 3700X、WSL Linux。全件検証で遅かった3ケースを各5回、新しいprocessで逐次測定した。起動・JIT・入出力を含み、実行順を入れ替え、毎回公式checkerで検査している。

| ケース | 中央値 | 最大RSS |
| --- | ---: | ---: |
| max_03 | 1.056秒 | 231,344 KiB |
| max_00 | 1.054秒 | 231,392 KiB |
| max_04 | 1.047秒 | 231,404 KiB |

オンライン提出と全25ケースの反復測定は行っていない。メモリ制限は強制していない。

## 旧実装との比較

変更前の`LinearSieve`と`count_square_free`を[比較用ファイル](../benchmarks/baselines/count_square_free_before.py)に保存した。入力ごとに各5回、別processで逐次実行し、答えの一致・時間・最大RSSを検査した。測定には起動、JIT、同じ測定用スクリプトの読み込みを含むため、上の提出コード単独の時間とは直接比較しない。

| 上限 | 旧実装の中央値 | 採用版の中央値 | 旧実装の最大RSS | 採用版の最大RSS |
| --- | ---: | ---: | ---: | ---: |
| 10^10 | 0.287秒 | 0.280秒 | 77,784 KiB | 75,644 KiB |
| 10^12 | 0.333秒 | 0.277秒 | 103,328 KiB | 76,532 KiB |
| 10^14 | 0.954秒 | 0.306秒 | 356,400 KiB | 79,884 KiB |

旧実装を10^18で実行すると10億要素規模の表が必要になるため、この比較では10^14までに制限した。最速提出との比較ではない。

- [公式全件の判定](../../verify/library_checker/results/counting_squarefrees.json)
- [公式ケースの各回の時間・RSS・hash](../../verify/library_checker/benchmarks/counting_squarefrees.json)
- [新旧実装の比較記録](../benchmarks/results/square_free_comparison.json)
- [再実行用スクリプト](../benchmarks/square_free_benchmark.py)

## 再実行

```sh
pypy3 -m pytest -q library_codex/verify/prime/test_sieve.py
pypy3 library_codex/tools/check_library_checker.py test counting_squarefrees --official /path/to/library-checker-problems
pypy3 library_codex/benchmarks/official_benchmark.py counting_squarefrees --official /path/to/library-checker-problems --repeat 5 --slowest 3
pypy3 library_codex/benchmarks/square_free_benchmark.py
```
