import configparser
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigLoader:
    """設定ファイルの読み込みと管理を行うクラス"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """シングルトンパターンでインスタンスを作成"""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = "config.ini"):
        """
        初期化
        
        Args:
            config_path: 設定ファイルのパス
        """
        if self._config is None:
            self._config_path = Path(config_path)
            self._load_config()
    
    def _load_config(self) -> None:
        """設定ファイルを読み込み"""
        self._config = configparser.ConfigParser()
        
        if self._config_path.exists():
            try:
                self._config.read(self._config_path, encoding='utf-8')
                logging.info(f"設定ファイルを読み込みました: {self._config_path}")
            except Exception as e:
                logging.warning(f"設定ファイル読み込みエラー: {str(e)}")
                self._load_default_config()
        else:
            logging.info("設定ファイルが見つからないため、デフォルト設定を使用します")
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """デフォルト設定を読み込み"""
        default_config = {
            'app': {
                'app_title': 'RSS Monitor',
                'app_icon': '📡',
                'max_items_per_feed': '20',
                'cache_timeout_minutes': '30'
            },
            'logging': {
                'log_level': 'INFO',
                'log_file_max_size': '10MB',
                'log_backup_count': '5'
            },
            'rss': {
                'request_timeout': '10',
                'max_retries': '3',
                'user_agent': 'RSS-Monitor/1.0'
            },
            'scheduler': {
                'max_concurrent_jobs': '5',
                'misfire_grace_time': '300'
            },
            'ui': {
                'default_layout': 'wide',
                'sidebar_state': 'expanded',
                'show_performance_metrics': 'false'
            }
        }
        
        for section, options in default_config.items():
            self._config.add_section(section)
            for option, value in options.items():
                self._config.set(section, option, value)
    
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """
        設定値を取得
        
        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値
            
        Returns:
            str: 設定値
        """
        try:
            return self._config.get(section, option, fallback=fallback)
        except Exception:
            return fallback
    
    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """
        整数設定値を取得
        
        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値
            
        Returns:
            int: 設定値
        """
        try:
            return self._config.getint(section, option, fallback=fallback)
        except Exception:
            return fallback
    
    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """
        ブール設定値を取得
        
        Args:
            section: セクション名
            option: オプション名
            fallback: デフォルト値
            
        Returns:
            bool: 設定値
        """
        try:
            return self._config.getboolean(section, option, fallback=fallback)
        except Exception:
            return fallback
    
    def get_section(self, section: str) -> Dict[str, str]:
        """
        セクション全体を辞書で取得
        
        Args:
            section: セクション名
            
        Returns:
            Dict[str, str]: セクションの設定辞書
        """
        try:
            return dict(self._config.items(section))
        except Exception:
            return {}


# グローバルインスタンス
config = ConfigLoader()
