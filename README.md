# RSS Monitor

シンプルで洗練されたRSS更新監視WEBアプリ

## 特徴

- **シンプルなUI**: パッと見ただけで使い方が分かる洗練されたインターフェース
- **柔軟な設定**: RSS URLの追加・変更・削除が簡単
- **自動更新**: 1時間～1日間隔での自動更新監視
- **クライアント別設定**: ブラウザごとに設定が自動保持
- **認証不要**: すぐに使い始められる

## 技術仕様

- **フレームワーク**: Streamlit
- **設計原則**: SOLID原則準拠
- **言語**: Python 3.8+

## インストール

```bash
git clone https://github.com/ShunsukeTamura06/rss-monitor.git
cd rss-monitor
pip install -r requirements.txt
```

## 実行

```bash
streamlit run app.py
```

## プロジェクト構造

```
rss-monitor/
├── app.py              # メインアプリケーション
├── requirements.txt    # 依存ライブラリ
├── src/
│   ├── interfaces/    # 抽象インターフェース
│   ├── models/        # データモデル
│   ├── services/      # ビジネスロジック
│   ├── repositories/  # データアクセス層
│   └── utils/         # ユーティリティ
└── data/              # ローカルデータ保存
```

## アーキテクチャ

SOLID原則に基づいた拡張性の高い設計：

- **単一責任の原則**: 各クラスが明確な責任を持つ
- **開放閉鎖の原則**: 拡張に開放、修正に閉鎖
- **依存関係逆転の原則**: 抽象化に依存、具象に依存しない

## ライセンス

MIT License
