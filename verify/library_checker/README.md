# Library Checker

[解答](solutions/) · [検証結果](results/) · [PyPyベンチマーク](benchmarks/README.md) · [対応状況](manifest.json)

## 解答を探す

問題URL末尾の名前でファイルを探す。たとえば`https://judge.yosupo.jp/problem/scc`なら、[solutions/scc.py](solutions/scc.py)。

`solutions/`のコードは依存を展開済みなので、ライブラリをインストールせず単独で実行できる。リポジトリ直下から実行する場合：

```sh
pypy3 verify/library_checker/solutions/scc.py < input.txt
```

実装を読んだり変更したりするときは[drivers/scc.py](drivers/scc.py)のimport先を辿る。driverは入出力、`library_codex`はアルゴリズムを担当する。生成済みの`solutions/`は直接編集しない。

## 検証済みか確認する

[manifest.json](manifest.json)に全問題の対応状況、使用モジュール、解答と結果のパスがある。個別の結果は`results/<問題名>.json`、反復測定は`benchmarks/<問題名>.json`。

| 状態 | 意味 |
| --- | --- |
| `local_passed` | 記録された公式問題versionの全ケースをローカルで通過 |
| `unimplemented` | 問題用の解答がない。ライブラリに必要な機能がないとは限らない |
| `unverified` | 解答はあるが検証結果がない |
| `stale` | 解答または公式問題が結果の記録時から変わっている |
| `incomplete` | 全ケースの検査が終わっていない |
| `failed` / `error` | ケースの不通過 / 生成・実行基盤の失敗 |

結果JSONにはケース別の判定と時間、実行環境、source hash、公式問題versionを記録する。保存済みの対応状況は、下の`list`で現在のsourceと公式checkoutに照らして更新できる。

オンライン提出は行っていない。公式checkerと時間制限を使うが、CPU・OS・PyPyの違いがあり、メモリ制限も強制していないため、オンラインACを保証するものではない。

## 手元で検証する

WSLのPyPy、g++、Gitを使う。以下はすべてリポジトリ直下で実行する。

初回だけ[公式問題リポジトリ](https://github.com/yosupo06/library-checker-problems)を取得する。取得先は任意で、以降の`--official`へ同じパスを渡す。

```sh
git clone https://github.com/yosupo06/library-checker-problems.git /home/harurun/.cache/harurun-library-checker/problems
```

特定の問題を検査する：

```sh
pypy3 library_codex/tools/check_library_checker.py test scc --official /home/harurun/.cache/harurun-library-checker/problems
```

- 問題名は複数指定できる。省略すると解答のある全問題を検査する。
- 公式生成器で入力・正解・checkerを用意し、公式hashと照合する。判定は出力の単純一致ではなく公式checkerで行う。
- 同じ解答・問題version・runner・実行環境で通過済みなら結果を再利用する。`--force`で再実行できる。
- `--reuse-tests <既存キャッシュ>`で、公式hashが一致する入力・正解だけをコピーして再利用できる。コピー元は変更しない。
- 実行は逐次。大きな入力・正解ファイルはGitへ入れない。

検査せず対応状況だけを更新する：

```sh
pypy3 library_codex/tools/check_library_checker.py list --official /home/harurun/.cache/harurun-library-checker/problems
```

公式リポジトリを更新した後もこのコマンドを使う。新しい問題は未対応として一覧へ加わる。

## 解答を追加・変更する

1. `library_codex`の実装と専用テストを追加・修正する。[保守手順](../../library_codex/docs/CONTRIBUTING.md)も参照。
2. `drivers/<問題名>.py`へ入出力を書く。同名の既存benchmark用解答がある場合、driverが優先される。
3. 以下で提出コードを再生成し、同期を検査する。
4. 上の`test`で公式全ケースを検査する。必要なら下の手順で性能を測る。

```sh
pypy3 library_codex/tools/check_library_checker.py build
pypy3 library_codex/tools/check_library_checker.py check
```

この2コマンドは公式リポジトリなしで使える。通常の`check_changed.py`・`check_library.py`は提出コードの同期とrunnerのテストを行うが、公式全ケースは実行しない。

## 速度を測る

公式全ケースの検証後、遅かった3ケースを各5回測る例：

```sh
pypy3 library_codex/benchmarks/official_benchmark.py scc --official /home/harurun/.cache/harurun-library-checker/problems --repeat 5 --slowest 3
```

- `--slowest 0`で全公式ケースを反復する。
- 各回は新しいPyPyプロセスで、起動・JIT・入出力を含む。ケース順を入れ替え、他の重い検査と同時に走らせない。
- 出力は毎回公式checkerで検査する。現在のsourceで公式全件検証が済んでいなければ測定しない。
- 時間・最大RSS・入力とsourceのhash・実行環境をJSONへ保存し、[一覧](benchmarks/README.md)を更新する。失敗時に以前の正常な測定結果を上書きしない。
- timeoutや不正解で止まった場合は、ケース名・何回目か・そこまでの測定値を`benchmarks/comparisons/<問題名>-failed-run.json`へ保存する。
- 測定用timeoutは最低30秒。公式時間制限の判定は`results/`で確認する。環境の異なる記録をそのまま速度比較しない。

実装方式や他の提出との比較は[比較記録の索引](../../library_codex/docs/BENCHMARKS.md)から探せる。
