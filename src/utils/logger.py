import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "rss_monitor", level: int = logging.INFO) -> logging.Logger:
    """
    ロガーを設定
    
    Args:
        name: ロガー名
        level: ログレベル
        
    Returns:
        logging.Logger: 設定済みロガー
    """
    logger = logging.getLogger(name)
    
    # 既に設定済みの場合はそのまま返す
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # フォーマッターを作成
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラー（ローテーション付き）
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "rss_monitor.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def log_performance(func):
    """
    関数の実行時間をログに記録するデコレータ
    
    Args:
        func: 対象関数
        
    Returns:
        実行時間ログ付きの関数
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("rss_monitor.performance")
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"{func.__name__} 実行時間: {execution_time:.2f}秒")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} エラー終了 ({execution_time:.2f}秒): {str(e)}")
            raise
    
    return wrapper


def log_rss_activity(client_id: str, action: str, url: str = None, success: bool = True, error: str = None) -> None:
    """
    RSS活動をログに記録
    
    Args:
        client_id: クライアント識別子
        action: 実行されたアクション
        url: 対象URL（任意）
        success: 成功フラグ
        error: エラーメッセージ（任意）
    """
    logger = logging.getLogger("rss_monitor.activity")
    
    status = "成功" if success else "失敗"
    url_info = f" URL:{url}" if url else ""
    error_info = f" エラー:{error}" if error else ""
    
    message = f"[{client_id}] {action} - {status}{url_info}{error_info}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)
