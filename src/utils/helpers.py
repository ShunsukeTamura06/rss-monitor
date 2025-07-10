from datetime import datetime, timedelta
from typing import Optional
import streamlit as st


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M") -> str:
    """日時を文字列にフォーマット
    
    Args:
        dt: 日時オブジェクト
        format_str: フォーマット文字列
        
    Returns:
        str: フォーマットされた文字列
    """
    if dt is None:
        return "不明"
    return dt.strftime(format_str)


def format_timedelta(td: timedelta) -> str:
    """時間差を読みやすい形式に変換
    
    Args:
        td: 時間差オブジェクト
        
    Returns:
        str: 読みやすい時間差文字列
    """
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}秒前"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}分前"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours}時間前"
    else:
        days = total_seconds // 86400
        return f"{days}日前"


def truncate_text(text: str, max_length: int = 100) -> str:
    """テキストを指定文字数で省略
    
    Args:
        text: 対象テキスト
        max_length: 最大文字数
        
    Returns:
        str: 省略されたテキスト
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_client_id_from_session() -> str:
    """セッションからクライアントIDを取得
    
    Returns:
        str: クライアントID
    """
    # Streamlitのsession_stateから取得
    if 'client_id' not in st.session_state:
        # ユーザーエージェントベースのIDを生成
        import hashlib
        import time
        user_agent = st.context.headers.get('user-agent', 'unknown')
        timestamp = str(time.time())
        source = f"{user_agent}:{timestamp}"
        client_id = hashlib.md5(source.encode()).hexdigest()[:16]
        st.session_state.client_id = client_id
    
    return st.session_state.client_id


def display_success(message: str) -> None:
    """成功メッセージを表示
    
    Args:
        message: 表示メッセージ
    """
    st.success(f"✅ {message}")


def display_error(message: str) -> None:
    """エラーメッセージを表示
    
    Args:
        message: 表示メッセージ
    """
    st.error(f"❌ {message}")


def display_warning(message: str) -> None:
    """警告メッセージを表示
    
    Args:
        message: 表示メッセージ
    """
    st.warning(f"⚠️ {message}")


def display_info(message: str) -> None:
    """情報メッセージを表示
    
    Args:
        message: 表示メッセージ
    """
    st.info(f"ℹ️ {message}")
