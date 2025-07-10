import feedparser
import requests
from datetime import datetime, timedelta
from typing import Optional, List
from urllib.parse import urlparse

from src.interfaces.rss_fetcher import IRSSFetcher
from src.interfaces.data_repository import IDataRepository
from src.models.rss_feed import RSSFeed, RSSItem
from src.models.client_config import ClientConfig, UpdateFrequency


class RSSService(IRSSFetcher):
    """RSS/RDFフィードの取得と管理を行うサービス"""
    
    def __init__(self, repository: IDataRepository):
        """初期化
        
        Args:
            repository: データリポジトリ
        """
        self._repository = repository
        self._timeout = 10  # タイムアウト秒数
    
    def fetch_feed(self, url: str) -> RSSFeed:
        """指定URLからRSS/RDFフィードを取得
        
        Args:
            url: RSS/RDF URL
            
        Returns:
            RSSFeed: 取得したフィード情報
            
        Raises:
            Exception: 取得失敗時
        """
        try:
            # feedparserでRSS/RDFを取得（RSS 1.0/2.0, Atom, RDF全対応）
            parsed = feedparser.parse(url)
            
            if parsed.bozo and not parsed.entries:
                raise Exception(f"RSS/RDFフィードの取得に失敗しました: {url}")
            
            # フィード情報を抽出
            feed_info = parsed.feed
            
            # アイテムを変換
            items = []
            for entry in parsed.entries:
                # 公開日時をパース
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                
                item = RSSItem(
                    title=entry.get('title', ''),
                    link=entry.get('link', ''),
                    description=entry.get('summary', entry.get('description', '')),
                    published=published,
                    author=entry.get('author', entry.get('dc_creator', ''))
                )
                items.append(item)
            
            # RSS/RDFフィードオブジェクトを作成
            feed = RSSFeed(
                title=feed_info.get('title', ''),
                link=feed_info.get('link', ''),
                description=feed_info.get('description', feed_info.get('subtitle', '')),
                url=url,
                items=items,
                last_updated=datetime.now(),
                last_fetch=datetime.now()
            )
            
            # キャッシュに保存
            self._repository.save_feed_cache(url, feed)
            
            return feed
            
        except Exception as e:
            # キャッシュから取得を試行
            cached_feed = self._repository.load_feed_cache(url)
            if cached_feed:
                return cached_feed
            raise Exception(f"RSS/RDF取得エラー: {str(e)}")
    
    def validate_url(self, url: str) -> bool:
        """RSS/RDF URLの有効性を検証
        
        Args:
            url: 検証するURL
            
        Returns:
            bool: 有効な場合True
        """
        try:
            # URL形式をチェック
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False
            
            # HTTPリクエストで存在確認
            response = requests.head(url, timeout=self._timeout)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_feed_with_cache(self, url: str, force_refresh: bool = False) -> Optional[RSSFeed]:
        """キャッシュを考慮したフィード取得
        
        Args:
            url: RSS/RDF URL
            force_refresh: 強制更新フラグ
            
        Returns:
            Optional[RSSFeed]: フィード情報
        """
        if not force_refresh:
            # キャッシュから取得を試行
            cached_feed = self._repository.load_feed_cache(url)
            if cached_feed and self._is_cache_valid(cached_feed):
                return cached_feed
        
        try:
            return self.fetch_feed(url)
        except Exception:
            # エラー時はキャッシュを返す
            return self._repository.load_feed_cache(url)
    
    def _is_cache_valid(self, feed: RSSFeed, max_age_minutes: int = 30) -> bool:
        """キャッシュの有効性を確認
        
        Args:
            feed: フィード情報
            max_age_minutes: 最大キャッシュ保持時間（分）
            
        Returns:
            bool: 有効な場合True
        """
        now = datetime.now()
        age = now - feed.last_fetch
        return age.total_seconds() < (max_age_minutes * 60)
