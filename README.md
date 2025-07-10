# RSS Monitor 📡

**シンプルで洗練されたRSS更新監視WEBアプリ**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 特徴

- **🎯 シンプルなUI**: パッと見ただけで使い方が分かる洗練されたインターフェース
- **⚙️ 柔軟な設定**: RSS URLの追加・変更・削除が簡単
- **🔄 自動更新**: 1時間～1日間隔での自動更新監視
- **👤 クライアント別設定**: ブラウザごとに設定が自動保持
- **🚀 認証不要**: すぐに使い始められる
- **📊 豊富な機能**: フィルタリング、通知、分析機能付き
- **🐳 Docker対応**: コンテナで簡単デプロイ

## 🎬 デモ

```bash
# クイックスタート
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
pip install -r requirements.txt
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス

## 📋 要件

- Python 3.8+
- 安定したインターネット接続

## 🚀 インストール

### 標準インストール

```bash
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
pip install -r requirements.txt
```

### 仮想環境を使用（推奨）

```bash
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### Dockerを使用

```bash
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
docker build -t rss-monitor .
docker run -p 8501:8501 -v $(pwd)/data:/app/data rss-monitor
```

### Docker Compose

```bash
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
docker-compose up -d
```

## 💻 使用方法

### 基本的な使い方

1. **アプリケーション起動**
   ```bash
   streamlit run app.py
   ```

2. **RSS追加**
   - サイドバーの「RSS追加」フォームにURLを入力
   - 表示名（任意）を設定して「追加」をクリック

3. **更新頻度設定**
   - サイドバーで更新間隔を選択（手動/1時間/1日/1週間ごと）

4. **記事確認**
   - メイン画面で最新記事を確認
   - 記事タイトルをクリックして詳細を表示

### 高度な機能

#### 🔍 フィルタリング
- **キーワードフィルタ**: 特定のキーワードを含む記事のみ表示
- **日付フィルタ**: 過去N日間の記事のみ表示
- **スマートカテゴリ**: AI風の自動記事分類

#### 📧 通知機能
- **メール通知**: SMTP設定で新着記事をメール配信
- **Webhook通知**: カスタムWebhook URLに通知送信
- **Slack通知**: Slack Incoming Webhookで通知

#### 📊 分析機能
- **フィード統計**: 更新頻度、記事数の分析
- **トレンド分析**: 記事数の推移を可視化
- **システム分析**: 全体的なパフォーマンス監視

## 🏗️ アーキテクチャ

本プロジェクトはSOLID原則に基づいた拡張性の高い設計を採用：

```
rss-monitor/
├── app.py                    # メインアプリケーション
├── app_enhanced.py           # 機能拡張版アプリ
├── requirements.txt          # 依存ライブラリ
├── config.ini               # 設定ファイル
├── src/
│   ├── interfaces/          # 抽象インターフェース
│   │   ├── rss_fetcher.py
│   │   └── data_repository.py
│   ├── models/              # データモデル
│   │   ├── rss_feed.py
│   │   └── client_config.py
│   ├── services/            # ビジネスロジック
│   │   ├── rss_service.py
│   │   ├── config_service.py
│   │   └── scheduler_service.py
│   ├── repositories/        # データアクセス層
│   │   └── local_data_repository.py
│   └── utils/               # ユーティリティ
│       ├── helpers.py
│       ├── logger.py
│       ├── config_loader.py
│       ├── error_handler.py
│       ├── filters.py
│       ├── notifications.py
│       └── analytics.py
├── tests/                   # テストコード
├── docs/                    # ドキュメント
├── data/                    # ローカルデータ保存
└── logs/                    # ログファイル
```

### 設計原則

- **🎯 単一責任の原則**: 各クラスが明確な責任を持つ
- **🔓 開放閉鎖の原則**: 拡張に開放、修正に閉鎖
- **🔄 依存関係逆転の原則**: 抽象化に依存、具象に依存しない
- **📝 詳細なドキュメント**: 日本語docstringと豊富なコメント

## ⚙️ 設定

### config.ini

```ini
[app]
app_title = RSS Monitor
max_items_per_feed = 20
cache_timeout_minutes = 30

[logging]
log_level = INFO
log_file_max_size = 10MB

[rss]
request_timeout = 10
max_retries = 3
user_agent = RSS-Monitor/1.0
```

### 環境変数

```bash
# ログレベル設定
LOG_LEVEL=INFO

# データディレクトリパス
DATA_DIR=/app/data

# RSSタイムアウト設定
RSS_TIMEOUT=10
```

## 🧪 テスト

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=src

# 特定のテストファイル
pytest tests/test_rss_service.py
```

## 🐳 デプロイメント

### ローカル開発

```bash
# 開発環境セットアップ
./scripts/setup_dev.sh

# アプリケーション起動
streamlit run app.py
```

### Docker Compose (本番推奨)

```bash
# サービス起動
docker-compose up -d

# ログ確認
docker-compose logs -f

# サービス停止
docker-compose down
```

### クラウドプラットフォーム

#### Streamlit Cloud
1. GitHubリポジトリをフォーク
2. [Streamlit Cloud](https://streamlit.io/cloud) にサインアップ
3. リポジトリを選択してデプロイ

#### Heroku
```bash
heroku create your-app-name
heroku config:set PYTHONPATH=/app/src
git push heroku main
```

#### AWS EC2
```bash
# EC2インスタンスでDocker Composeを使用
sudo apt update && sudo apt install docker.io docker-compose
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
sudo docker-compose up -d
```

## 📈 パフォーマンス

- **軽量**: 最小512MBメモリで動作
- **高速**: インメモリキャッシュで高速表示
- **スケーラブル**: 数百のRSSフィードに対応
- **安定**: 自動エラー回復とログ記録

## 🔧 開発

### 開発環境構築

```bash
# 開発用セットアップ
pip install -r requirements-dev.txt
pre-commit install

# コード品質チェック
flake8 src/
black src/
mypy src/

# テスト実行
pytest tests/
```

### 新機能の追加

1. 適切なinterface/modelを定義
2. service層にビジネスロジックを実装
3. repository層でデータアクセスを実装
4. テストを作成
5. ドキュメントを更新

詳細は [CONTRIBUTING.md](docs/CONTRIBUTING.md) を参照

## 📊 使用例

### 人気RSSフィード例

```python
# ニュースサイト
"https://www.nhk.or.jp/rss/news/cat0.xml"
"https://news.yahoo.co.jp/rss/topics/top-picks.xml"

# 技術ブログ
"https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml"
"https://zenn.dev/topics/tech/feed"

# GitHub
"https://github.com/trending.atom"
```

### API使用例

```python
from src.services.rss_service import RSSService
from src.repositories.local_data_repository import LocalDataRepository

# サービス初期化
repository = LocalDataRepository()
rss_service = RSSService(repository)

# RSSフィード取得
feed = rss_service.fetch_feed("https://example.com/rss")
print(f"タイトル: {feed.title}")
print(f"記事数: {len(feed.items)}")
```

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'feat: Add AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

詳細は [CONTRIBUTING.md](docs/CONTRIBUTING.md) を参照してください。

## 📄 ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。

## 🙏 謝辞

- [Streamlit](https://streamlit.io/) - 素晴らしいWebアプリフレームワーク
- [feedparser](https://github.com/kurtmckee/feedparser) - 高機能RSSパーサー
- [APScheduler](https://github.com/agronholm/apscheduler) - 柔軟なスケジューラー

## 📞 サポート

- 📝 [Issues](https://github.com/ShunsukeTamura06/rss-monitor/issues) - バグ報告・機能要求
- 💬 [Discussions](https://github.com/ShunsukeTamura06/rss-monitor/discussions) - 質問・議論
- 📖 [Wiki](https://github.com/ShunsukeTamura06/rss-monitor/wiki) - 詳細ドキュメント

## 🗺️ ロードマップ

- [ ] 📱 PWA対応でモバイルアプリ化
- [ ] 🌐 多言語対応（英語・中国語・韓国語）
- [ ] 🔍 全文検索機能
- [ ] 📱 プッシュ通知対応
- [ ] 🤖 AI要約機能
- [ ] 📊 より高度な分析ダッシュボード
- [ ] 🔗 外部API連携（Twitter, Slack等）

---

**RSS Monitor** - シンプルで強力なRSS監視ツール 🚀
