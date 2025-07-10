from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.models.rss_feed import RSSFeed, RSSItem


class IRSSFetcher(ABC):
    """RSS取得の抽象インターフェース"""
    
    @abstractmethod
    def fetch_feed(self, url: str) -> RSSFeed:
        """指定URLからRSSフィードを取得
        
        Args:
            url: RSS URL
            
        Returns:
            RSSFeed: 取得したフィード情報
            
        Raises:
            Exception: 取得失敗時
        """
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """RSS URLの有効性を検証
        
        Args:
            url: 検証するURL
            
        Returns:
            bool: 有効な場合True
        """
        pass
