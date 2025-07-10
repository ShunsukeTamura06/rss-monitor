#!/bin/bash
# 開発環境セットアップスクリプト

set -e

echo "🚀 RSS Monitor 開発環境のセットアップを開始します"

# Python バージョンチェック
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 が見つかりません。Python 3.8+ をインストールしてください。"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "❌ Python 3.8+ が必要です。現在のバージョン: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION が利用可能です"

# 仮想環境の作成
if [ ! -d "venv" ]; then
    echo "📦 仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境のアクティベート
echo "🔧 仮想環境をアクティベート中..."
source venv/bin/activate

# 依存ライブラリのインストール
echo "📚 依存ライブラリをインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

# Pre-commitフックのインストール
if command -v pre-commit &> /dev/null; then
    echo "🪝 Pre-commitフックをインストール中..."
    pre-commit install
fi

# ディレクトリの作成
echo "📁 必要なディレクトリを作成中..."
mkdir -p data/configs data/cache logs

# 設定ファイルのコピー
if [ ! -f "config.ini" ]; then
    echo "⚙️ 設定ファイルを作成中..."
    # config.ini は既に存在する前提
fi

echo "✨ セットアップが完了しました！"
echo ""
echo "📝 次のステップ:"
echo "   1. 仮想環境をアクティベート: source venv/bin/activate"
echo "   2. アプリケーションを起動: streamlit run app.py"
echo "   3. テストを実行: pytest"
echo "   4. コード品質チェック: flake8 src/"
echo ""
echo "🔗 詳細な情報は docs/CONTRIBUTING.md を参照してください"
