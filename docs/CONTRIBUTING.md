# コントリビューションガイド

RSS Monitorへのコントリビューションを歓迎します！

## 開発環境のセットアップ

### 前提条件
- Python 3.8+
- Git
- pip

### 環境構築

```bash
# リポジトリをフォークしてクローン
git clone https://github.com/your-username/rss-monitor.git
cd rss-monitor

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 開発用依存ライブラリをインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用ライブラリがある場合

# pre-commitフックをインストール
pre-commit install
```

## コードスタイル

### Pythonコーディング規約
- PEP 8に準拠
- 最大1行80文字まで
- 関数とクラスにはdocstringを記述
- 型ヒントを積極的に使用

### コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/)に準拠：

```
<type>: <description>

[optional body]

[optional footer(s)]
```

#### Typeの例
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードスタイル変更
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルドプロセスやツール変更

#### 例
```
feat: RSS自動更新スケジューラーを追加

fix: RSS取得時のタイムアウトエラーを修正

docs: APIドキュメントを更新
```

## プルリクエスト手順

### 1. Issueの作成

新機能やバグ修正の前に、関連するIssueを作成してください。

### 2. ブランチの作成

```bash
# 最新のmainブランチを取得
git checkout main
git pull origin main

# 新しいブランチを作成
git checkout -b feature/issue-number-description
# 例: git checkout -b feature/123-add-rss-scheduler
```

### 3. 開発とテスト

```bash
# コードを更新
# ...

# テストを実行
python -m pytest tests/

# コード品質チェック
flake8 src/
black src/
mypy src/

# アプリケーションの動作テスト
streamlit run app.py
```

### 4. コミットとプッシュ

```bash
# 変更をコミット
git add .
git commit -m "feat: RSS自動更新スケジューラーを追加"

# ブランチをプッシュ
git push origin feature/123-add-rss-scheduler
```

### 5. プルリクエストの作成

GitHubでプルリクエストを作成し、以下を含めてください：

- 変更内容の説明
- 関連Issueへの参照
- テスト結果
- スクリーンショット（UI変更の場合）

## テスト

### テストの実行

```bash
# すべてのテストを実行
python -m pytest

# カバレッジ付きで実行
python -m pytest --cov=src

# 特定のテストファイルを実行
python -m pytest tests/test_rss_service.py

# 特定のテスト関数を実行
python -m pytest tests/test_rss_service.py::test_fetch_feed_success
```

### テストの書き方

```python
import unittest
from unittest.mock import Mock, patch

class TestNewFeature(unittest.TestCase):
    """新機能のテスト"""
    
    def setUp(self):
        """テスト初期化"""
        # テスト用のセットアップ
        pass
    
    def test_normal_case(self):
        """正常ケースのテスト"""
        # テスト実装
        pass
    
    def test_error_case(self):
        """エラーケースのテスト"""
        # テスト実装
        pass
```

## ドキュメント

### Docstringの書き方

Googleスタイルのdocstringを使用：

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """機能の概要を簡潔に説明
    
    より詳細な説明が必要な場合はここに記述。
    
    Args:
        param1: 第1パラメータの説明
        param2: 第2パラメータの説明（デフォルト: 0）
        
    Returns:
        bool: 成功時True、失敗時False
        
    Raises:
        ValueError: param1が空文字列の場合
        
    Example:
        >>> result = example_function("test", 1)
        >>> print(result)
        True
    """
    pass
```

### READMEやドキュメントの更新

新機能を追加した場合は、関連するドキュメントも同時に更新してください：

- `README.md`: メインの説明
- `docs/API.md`: APIドキュメント
- `docs/DEPLOYMENT.md`: デプロイメントガイド

## コードレビュー

### レビュー観点

1. **機能性**: 要件を満たしているか
2. **コード品質**: 可読性、保守性が高いか
3. **テスト**: 適切なテストが含まれているか
4. **ドキュメント**: 必要なドキュメントが更新されているか
5. **パフォーマンス**: パフォーマンスに影響はないか

### フィードバックの対応

レビューコメントには速やかに対応し、必要に応じてコードを修正してください。

## イシューテンプレート

### バグレポート

```markdown
## バグの説明
簡潔で明確なバグの説明

## 再現手順
1. ステップを記述
2. ...
3. ...

## 期待される動作
本来どう動作すべきか

## 実際の動作
実際にどう動作したか

## 環境
- OS: [e.g. Ubuntu 20.04]
- Pythonバージョン: [e.g. 3.9.0]
- ブラウザ: [e.g. Chrome 91]

## 追加情報
スクリーンショットやログなど
```

### 機能リクエスト

```markdown
## 機能の概要
新機能の簡潔な説明

## 動機
なぜこの機能が必要か

## 詳細仕様
- 機能の詳細
- UI/UXの要件
- パフォーマンス要件

## 参考情報
関連するリンクや資料
```

## 貪獻

疑問や提案がある場合は、以下の方法でお気軽にお知らせください：

- GitHub Issues
- GitHub Discussions
- Pull Requestのコメント

あなたのコントリビューションをお待ちしています！
