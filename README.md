# iwashi.co

個人技術ブログのリポジトリです。

## Dockerを使った起動方法

### 本番環境用（nginx）

本番環境用のDockerイメージをビルドして起動します：

```bash
# Dockerイメージをビルド
docker build -t iwashi-blog .

# コンテナを起動（ポート8080でアクセス可能）
docker run -p 8080:80 iwashi-blog
```

ブラウザで `http://localhost:8080` にアクセスしてサイトを確認できます。

### 開発環境用（ライブリロード付き）

開発用のDockerイメージをビルドして起動します：

```bash
# 開発用Dockerイメージをビルド
docker build -f Dockerfile.dev -t iwashi-blog-dev .

# コンテナを起動（ファイルの変更が自動的に反映されます）
docker run -p 4000:4000 -p 35729:35729 -v $(pwd):/site iwashi-blog-dev
```

ブラウザで `http://localhost:4000` にアクセスしてサイトを確認できます。
ファイルを編集すると自動的にブラウザがリロードされます。

## ローカル環境での起動方法

Dockerを使わない場合：

```bash
# 依存関係をインストール
bundle install

# 開発サーバーを起動
bundle exec jekyll serve
```

## サイト情報

- URL: https://iwashi.co
- Jekyll version: 4.3.2
- 主な内容: WebRTC、クラウドインフラ、エンジニアリングマネジメントに関する技術記事