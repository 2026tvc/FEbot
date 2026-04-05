# IPA 由来コーパス（`ipa-*.md`）の再生成手順

## 概要

`data/corpus/ipa-*.md` は、IPA が公表している PDF（基本情報技術者試験の CBT 公開問題・筆記過去問題・シラバス等）を [scripts/ipa_build_corpus.py](scripts/ipa_build_corpus.py) で **テキスト抽出**したものです。図表やレイアウトは欠落し、ページ順序が崩れる場合があります。試験の正式な内容は必ず公式 PDF で確認してください。

利用上の留意点は IPA の [試験に関するよくある質問（その他）](https://www.ipa.go.jp/shiken/faq.html#seido) および [過去問題トップ](https://www.ipa.go.jp/shiken/mondai-kaiotu/index.html) の説明に従ってください。

## 前提

- 依存: `pypdf`, `PyYAML`（`pip install -e .` または `requirements.txt` 相当で導入済みであること）
- バイナリ PDF は `data/ipa_raw/` に保存されるが、このディレクトリは **Git 対象外**（`.gitignore`）。リポジトリに載るのは抽出済み `.md` のみ。

## 再生成（ネットワークあり）

プロジェクトルートで:

```bash
python3 scripts/ipa_build_corpus.py --fetch
```

続けて埋め込みを更新する:

```bash
python3 scripts/ingest.py
```

## オフライン（PDF を手で置く）

1. [data/ipa_manifest.yaml](data/ipa_manifest.yaml) の `url` にあるファイル名と一致する名前で PDF を `data/ipa_raw/` に保存する（例: `2024r06_fe_kamoku_a_qs.pdf`）。
2. `--fetch` なしで実行する:

```bash
python3 scripts/ipa_build_corpus.py
```

## マニフェストの更新

- 対象 PDF を増やす場合は `data/ipa_manifest.yaml` の `entries` に `url`・`source_page`・`output_stem`（`ipa-*.md` のファイル名本体）・`doc_kind`（`past_questions` / `answers` / `commentary` / `syllabus`）を追加する。
- 筆記試験の PDF は年度ページごとにアップロードパス（`-att/` のディレクトリ名）が変わるため、IPA の HTML から `href` をそのままコピーするのが確実である。
- マニフェストから削除したエントリに対応する `data/corpus/ipa-*.md` は自動では消えない。不要なら手で削除してから `ingest` し直す。

## 具体例

- CBT 公開問題の一覧: `https://www.ipa.go.jp/shiken/mondai-kaiotu/sg_fe/koukai/index.html`
- シラバス一覧: `https://www.ipa.go.jp/shiken/syllabus/gaiyou.html`
- 現行マニフェストには例として、令和5〜7年度の FE 科目 A/B（問題・解答）、平成28〜30年度秋期の筆記 FE（午前・午後・採点講評）、シラバス ver9.2 が含まれる。
