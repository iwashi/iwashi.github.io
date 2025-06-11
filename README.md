### 開発環境用

開発用のDockerイメージをビルドして起動します：

```bash
# 開発用Dockerイメージをビルド
docker build -f Dockerfile.dev -t iwashi-blog-dev .

# コンテナを起動（ファイルの変更が自動的に反映されます）
docker run -p 4000:4000 -p 35729:35729 -v $(pwd):/site iwashi-blog-dev
```

ブラウザで `http://localhost:4000` にアクセスしてサイトを確認可能。
