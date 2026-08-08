# harurun's library 作業規約

このリポジトリを変更する前に、`library_codex/docs/CONTRIBUTING.md` を読むこと。`library_codex` が現在の実装の正本で、`library` は過去の実装を調べるための参照資料とする。

## 設計

- 1モジュールは原則1目的とし、利用者が別々に選べる構造やアルゴリズムを寄せ集めない。
- よく使う公開APIには短く標準的な名前を選び、同じ処理を行う別名methodを増やさない。
- 互換aliasは原則として作らない。特別な理由で必要な場合だけ、理由・期限・削除条件をissueまたは保守文書へ残す。
- `v2` などの版番号を名前へ足して回避せず、置き換えるべき実装は自然な名前で置き換える。
- PyPyでの速度を優先し、原則として再帰を使わない。大きな前計算や常駐メモリを安易に増やさない。
- 二項演算`op`を受け取る構造では、非可換でも正しく動くように演算順を明記し、testする。
- 元の`library`からは有用な仕様や着想を拾ってよいが、実装は検証して`library_codex`の規約に合わせて書き直す。

## API・ドキュメント

- module冒頭に「何ができるか」を具体的に書く。
- 公開関数・class・methodごとに、用途、引数の意味、返り値の型と中身、計算量を確認できるようにする。
- `list`は要素の並び、`dict`はkeyとvalueの意味、tupleは各要素の意味まで記す。
- 計算量欄には通常のBig-Oを示す。アルゴリズム名だけで計算量の説明を済ませない。
- 「処理を実行します」のように名前を言い換えただけの説明や、同じ意味の日本語・英語の併記を避ける。
- APIを変えたら`library_codex/tools/api_metadata.py`も確認し、APIリファレンスを再生成する。
- ページの説明・数式・見た目を変える前に`library_codex/docs/PAGE_CONTENT_GUIDE.md`を読み、サイトだけの説明上書きを作らない。

## bundle

- bundleは、選択したmoduleと実際の依存だけを含む、単独実行できる普通のPythonコードにする。
- packageをインストールしていない環境で貼り付けて使えることを保つ。
- 無関係なclass、互換alias、疑似module wrapperを混ぜない。

## データ構造のデバッグ表示

- 有限の論理内容を無理なく列挙できる構造には、`tolist()`または`items()`と、内容を示す`__str__`・`__repr__`を用意する。
- 密な列はlist、2次元構造は2次元list、setは昇順list、multisetは重複を残す。疎で巨大な座標空間は使用中の`items`だけを返す。
- `__str__`は論理内容、`__repr__`は型名と同じ内容を表示する。遅延更新がある場合も現在の論理値を表示する。
- デバッグ表示だけのために提出時の通常操作へ大きな時間・メモリ負担を追加しない。
- 詳細な形式は`library_codex/docs/DEBUG_OUTPUT.md`に追記する。

## 検証と完了条件

- 正解を単純解と比較するrandomized test、空・要素1・重複・境界値のtestを追加する。
- データ構造ではデバッグ表示の内容と、表示後も状態が壊れないことをtestする。
- 反復中は`pypy3 library_codex/tools/check_changed.py`を使い、変更module・依存先・対応testだけを検査する。
- まとまったcheckpointでは`pypy3 library_codex/tools/check_library.py`を通す。
- full検査`pypy3 library_codex/tools/check_library.py --profile full`は、共通基盤の横断変更、大規模な性能変更、mainへmergeするrelease checkpointでだけ実行する。説明、サイト表示、1moduleの局所変更のたびには繰り返さない。
- サイト公開は小さな変更ごとに義務化せず、確認しやすいまとまりで行う。API dataは前回revisionから差分更新する。
- APIリファレンス、GitHubの配布物、サイトのJSONとZIPをsourceと同期してから完了とする。
