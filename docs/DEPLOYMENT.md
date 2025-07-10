# デプロイメントガイド

## 概要

RSS Monitorは以下の方法でデプロイできます：

1. **ローカル実行**: 開発やテスト用
2. **Docker**: コンテナベースのデプロイ
3. **Docker Compose**: サービス管理と永続データ保持
4. **クラウドプラットフォーム**: 本格的な運用

## ローカル実行

### 前提条件
- Python 3.8+
- pip

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor

# 仮想環境を作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存ライブラリをインストール
pip install -r requirements.txt

# アプリケーションを実行
streamlit run app.py
```

### アクセス
ブラウザで `http://localhost:8501` にアクセス

## Dockerデプロイ

### 前提条件
- Docker
- Docker Compose（オプション）

### Dockerイメージのビルドと実行

```bash
# イメージをビルド
docker build -t rss-monitor .

# コンテナを実行
docker run -d \
  --name rss-monitor \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  rss-monitor
```

### Docker Composeでの実行

```bash
# サービスを開始
docker-compose up -d

# サービスの状態確認
docker-compose ps

# ログの確認
docker-compose logs -f

# サービスを停止
docker-compose down
```

## クラウドデプロイ

### Streamlit Cloud

1. GitHubリポジトリをフォーク
2. [Streamlit Cloud](https://streamlit.io/cloud) にサインアップ
3. リポジトリを選択してデプロイ

**注意**: Streamlit Cloudではファイルシステムへの書き込みが制限されるため、データの永続化に制約があります。

### Heroku

```bash
# Heroku CLIでログイン
heroku login

# アプリケーションを作成
heroku create your-app-name

# 環境変数を設定
heroku config:set PYTHONPATH=/app/src

# デプロイ
git push heroku main
```

**必要なファイル**:
- `Procfile`: `web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- `runtime.txt`: `python-3.11.0`

### AWS EC2

```bash
# EC2インスタンスにサーバーをセットアップ
sudo apt update
sudo apt install docker.io docker-compose

# リポジトリをクローン
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor

# Docker Composeで実行
sudo docker-compose up -d

# セキュリティグループでポート8501を開放
```

## 環境変数設定

以下の環境変数でアプリケーションをカスタマイズできます：

```bash
# ログレベル設定
LOG_LEVEL=INFO

# データディレクトリパス
DATA_DIR=/app/data

# RSSタイムアウト設定
RSS_TIMEOUT=10

# キャッシュ有効時間（分）
CACHE_TIMEOUT=30
```

## パフォーマンス最適化

### メモリ使用量最適化

```bash
# Dockerでメモリ制限を設定
docker run -d \
  --name rss-monitor \
  --memory=512m \
  --cpus=0.5 \
  -p 8501:8501 \
  rss-monitor
```

### キャッシュ設定

`config.ini` でキャッシュの有効時間を調整：

```ini
[app]
cache_timeout_minutes = 15  # キャッシュ有効時間を短縮
```

## セキュリティ

### HTTPS設定

Nginxをリバースプロキシとして使用：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### ファイアウォール設定

```bash
# UFWでポートを制限
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## モニタリング

### ログ監視

```bash
# リアルタイムログ監視
tail -f logs/rss_monitor.log

# Dockerコンテナのログ
docker logs -f rss-monitor
```

### ヘルスチェック

アプリケーションの稼働状態を確認：

```bash
# HTTPステータスコード確認
curl -I http://localhost:8501/_stcore/health

# Streamlitヘルスチェック
wget --spider -q http://localhost:8501/_stcore/health
```

## バックアップと復元

### データバックアップ

```bash
# 設定ファイルとキャッシュをバックアップ
tar -czf rss-monitor-backup-$(date +%Y%m%d).tar.gz data/

# S3にアップロード（AWS CLIが必要）
aws s3 cp rss-monitor-backup-$(date +%Y%m%d).tar.gz s3://your-backup-bucket/
```

### 自動バックアップスクリプト

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/rss-monitor-$DATE.tar.gz data/

# 古いバックアップを削除（7日以上古いもの）
find $BACKUP_DIR -name "rss-monitor-*.tar.gz" -mtime +7 -delete
```

```bash
# cronで毎日実行
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## トラブルシューティング

### 一般的な問題

1. **アプリケーションが起動しない**
   - ポート8501が使用中でないか確認
   - `requirements.txt` のライブラリがインストールされているか確認

2. **RSS取得エラー**
   - URLが正しいか確認
   - ネットワーク接続を確認
   - ログで詳細エラーを確認

3. **データが保存されない**
   - `data/` ディレクトリの権限を確認
   - ディスク容量を確認

### ログレベルの変更

デバッグ情報を得るために `config.ini` でログレベルを変更：

```ini
[logging]
log_level = DEBUG
```
