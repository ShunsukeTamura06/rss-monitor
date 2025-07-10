import functools
import traceback
from typing import Callable, Any, Optional
from datetime import datetime
import logging
import streamlit as st


class ErrorHandler:
    """エラーハンドリング用ユーティリティクラス"""
    
    @staticmethod
    def handle_rss_error(func: Callable) -> Callable:
        """
        RSS関連エラーをハンドリングするデコレータ
        
        Args:
            func: ラップする関数
            
        Returns:
            Callable: エラーハンドリング付き関数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = ErrorHandler._format_rss_error(e)
                logging.error(f"RSSエラー in {func.__name__}: {error_msg}")
                
                # Streamlitコンテキスト内でのみユーザーに表示
                try:
                    st.error(f"❌ RSS処理エラー: {error_msg}")
                except Exception:
                    pass  # Streamlitコンテキスト外では無視
                
                return None
        return wrapper
    
    @staticmethod
    def handle_config_error(func: Callable) -> Callable:
        """
        設定関連エラーをハンドリングするデコレータ
        
        Args:
            func: ラップする関数
            
        Returns:
            Callable: エラーハンドリング付き関数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = ErrorHandler._format_config_error(e)
                logging.error(f"設定エラー in {func.__name__}: {error_msg}")
                
                try:
                    st.warning(f"⚠️ 設定エラー: {error_msg}")
                except Exception:
                    pass
                
                return False  # 設定関連は通常ブール値を返す
        return wrapper
    
    @staticmethod
    def _format_rss_error(error: Exception) -> str:
        """
        RSSエラーをユーザーフレンドリーなメッセージに変換
        
        Args:
            error: エラーオブジェクト
            
        Returns:
            str: フォーマットされたエラーメッセージ
        """
        error_type = type(error).__name__
        error_str = str(error)
        
        # 一般的なエラーパターンをユーザーフレンドリーに変換
        if "timeout" in error_str.lower():
            return "タイムアウトが発生しました。サーバーが応答していない可能性があります。"
        elif "connection" in error_str.lower():
            return "ネットワーク接続エラーが発生しました。インターネット接続を確認してください。"
        elif "404" in error_str:
            return "RSSフィードが見つかりません。URLを確認してください。"
        elif "403" in error_str:
            return "アクセスが拒否されました。RSSフィードが制限されている可能性があります。"
        elif "500" in error_str:
            return "サーバーエラーが発生しました。しばらく待ってから再試行してください。"
        elif "invalid" in error_str.lower() or "parse" in error_str.lower():
            return "RSSフィードの形式が無効です。正しいRSS URLか確認してください。"
        else:
            return f"予期しないエラーが発生しました ({error_type})"
    
    @staticmethod
    def _format_config_error(error: Exception) -> str:
        """
        設定エラーをユーザーフレンドリーなメッセージに変換
        
        Args:
            error: エラーオブジェクト
            
        Returns:
            str: フォーマットされたエラーメッセージ
        """
        error_str = str(error)
        
        if "permission" in error_str.lower():
            return "ファイルの読み書き権限がありません。"
        elif "space" in error_str.lower() or "disk" in error_str.lower():
            return "ディスク容量が不足しています。"
        elif "json" in error_str.lower():
            return "設定ファイルの形式が無効です。"
        else:
            return "設定の保存または読み込みに失敗しました。"
    
    @staticmethod
    def log_error_details(error: Exception, context: str = "") -> None:
        """
        エラーの詳細情報をログに記録
        
        Args:
            error: エラーオブジェクト
            context: エラーのコンテキスト
        """
        logger = logging.getLogger("rss_monitor.error")
        
        error_details = {
            'timestamp': datetime.now().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        logger.error(f"エラー詳細: {error_details}")


# ショートハンドエイリアス
handle_rss_error = ErrorHandler.handle_rss_error
handle_config_error = ErrorHandler.handle_config_error
log_error_details = ErrorHandler.log_error_details
