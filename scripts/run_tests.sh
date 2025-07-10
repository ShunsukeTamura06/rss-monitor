#!/bin/bash
# テスト実行スクリプト

set -e

echo "🧪 テストスイートを実行中..."

# 仮想環境のアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# コードスタイルチェック
echo "📋 コードスタイルをチェック中..."
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# 型チェック
echo "🔍 型チェックを実行中..."
mypy src/ --ignore-missing-imports

# 単体テスト
echo "🧪 単体テストを実行中..."
pytest tests/ -v --cov=src --cov-report=term-missing

echo "✅ すべてのテストが完了しました！"
