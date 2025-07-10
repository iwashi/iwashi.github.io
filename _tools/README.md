# OGP Image Generator

ブログ記事のタイトルからOGP画像を自動生成するPythonスクリプトです。日本語テキストに対応しています。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. フォントのダウンロード

日本語フォント（Noto Sans CJK JP）をダウンロードします：

```bash
./download_font.sh
```

または手動でダウンロードする場合：

```bash
python generate_ogp.py --setup-font
```

## 使い方

### 全記事のOGP画像を生成

```bash
python generate_ogp.py
```

デフォルトでは `_posts/` ディレクトリ内のすべてのMarkdownファイルを処理し、`assets/images/ogp/` に画像を出力します。

### 特定の記事のOGP画像を生成

```bash
python generate_ogp.py ../_posts/2025-07-06-12-factor-agents.md
```

### 出力ディレクトリを指定

```bash
python generate_ogp.py -o custom/output/path
```

## 画像仕様

- サイズ: 1200×630ピクセル（標準的なOGPサイズ）
- 背景色: ダークブルー (#0E3868)
- テキストエリア: 白
- ブログタイトル: "iwashi.co"（上部）
- 記事タイトル: Markdownファイルのtitleフィールドから取得（中央）

## トラブルシューティング

### フォントが見つからない場合

```
Error: Font file not found at _tools/fonts/NotoSansCJKjp-Regular.otf
```

このエラーが表示される場合は、`./download_font.sh` を実行してフォントをダウンロードしてください。

### 日本語が表示されない場合

Noto Sans CJK JPフォントが正しくダウンロードされているか確認してください。フォントファイルは `_tools/fonts/NotoSansCJKjp-Regular.otf` に配置されている必要があります。