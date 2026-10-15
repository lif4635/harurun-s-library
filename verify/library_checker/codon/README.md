# CodonのLibrary Checker検証

[解答](solutions/) · [公式全件の結果とPyPy比較](results/)

SCCと2-SATの解答をCodon 0.19.3でコンパイルし、公式生成器・checkerで検証する。既存のPyPy driverと`library_codex`が正本。ここにある`.codon`は単独でコンパイルできる生成物で、直接編集しない。

```sh
codon build --release -o a.out verify/library_checker/codon/solutions/scc.codon
./a.out < input.txt
```

## 再検証

```sh
pypy3 library_codex/tools/check_codon_library_checker.py test --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5
```

- 全公式ケースをCodonで検査した後、遅かった3ケースをCodonとPyPyで各5回測る。
- 起動・入出力を含め、コンパイル時間は分離する。各回の出力を公式checkerで確認する。
- JSONには入力・コード・checkerのhash、処理系、実行時間、最大RSSを保存する。
- メモリ制限は強制していない。ローカルでの通過であり、オンライン提出は行わない。
- 失敗した公式検証は`failures/`へ記録し、前の成功結果を置き換えない。成功結果の`sourceSha256`が現在の生成コードと一致するかも確認する。

生成・同期確認だけなら公式リポジトリは不要。

```sh
pypy3 library_codex/tools/check_codon_library_checker.py build
pypy3 library_codex/tools/check_codon_library_checker.py check
```
