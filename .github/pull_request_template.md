## 変更内容

- 

## 確認

- [ ] 1モジュール1目的を守り、無関係な実装や冗長な別名APIを混ぜていない
- [ ] 公開APIの用途、引数、返り値の形式、methodごとの計算量を記載した
- [ ] `op`を受け取る場合は演算順を明記し、非可換のtestを追加した
- [ ] 単純解とのrandomized testと、空・要素1・重複・境界値のtestを追加した
- [ ] データ構造なら`tolist()`または`items()`、`str`、`repr`とそのtestを検討した
- [ ] bundleが選択moduleと実依存だけの単独実行可能なコードになっている
- [ ] `pypy3 library_codex/tools/build_api_reference.py`を実行した
- [ ] 反復中に`pypy3 library_codex/tools/check_changed.py`で差分検査した
- [ ] checkpointなら`pypy3 library_codex/tools/check_library.py`を通した
- [ ] 共通基盤・大規模性能変更・release checkpointなら`--profile full`も通した
- [ ] 公開する変更ならサイトのデータと配布ZIPも同期した
