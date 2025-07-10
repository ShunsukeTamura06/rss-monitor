from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.models.client_config import ClientConfig
from src.models.rss_feed import RSSFeed


class IDataRepository(ABC):
    """データ永続化の抽象インターフェース"""
    
    @abstractmethod
    def save_client_config(self, client_id: str, config: ClientConfig) -> None:
        """クライアント設定を保存
        
        Args:
            client_id: クライアント識別子
            config: 設定情報
        """
        pass
    
    @abstractmethod
    def load_client_config(self, client_id: str) -> Optional[ClientConfig]:
        """クライアント設定を読み込み
        
        Args:
            client_id: クライアント識別子
            
        Returns:
            Optional[ClientConfig]: 設定情報（存在しない場合None）
        """
        pass
    
    @abstractmethod
    def save_feed_cache(self, url: str, feed: RSSFeed) -> None:
        """フィードキャッシュを保存
        
        Args:
            url: RSS URL
            feed: フィード情報
        """
        pass
    
    @abstractmethod
    def load_feed_cache(self, url: str) -> Optional[RSSFeed]:
        """フィードキャッシュを読み込み
        
        Args:
            url: RSS URL
            
        Returns:
            Optional[RSSFeed]: キャッシュされたフィード（存在しない場合None）
        """
        pass
