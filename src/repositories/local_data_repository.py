import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from src.interfaces.data_repository import IDataRepository
from src.models.client_config import ClientConfig, UpdateFrequency, RSSConfig
from src.models.rss_feed import RSSFeed, RSSItem


class LocalDataRepository(IDataRepository):
    """ローカルファイルシステムでのデータ永続化実装"""
    
    def __init__(self, data_dir: str = "data"):
        """初期化
        
        Args:
            data_dir: データ保存ディレクトリ
        """
        self._data_dir = Path(data_dir)
        self._config_dir = self._data_dir / "configs"
        self._cache_dir = self._data_dir / "cache"
        
        # ディレクトリを作成
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_client_config(self, client_id: str, config: ClientConfig) -> None:
        """クライアント設定を保存
        
        Args:
            client_id: クライアント識別子
            config: 設定情報
        """
        file_path = self._config_dir / f"{client_id}.json"
        config_data = self._config_to_dict(config)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            raise Exception(f"設定保存エラー: {str(e)}")
    
    def load_client_config(self, client_id: str) -> Optional[ClientConfig]:
        """クライアント設定を読み込み
        
        Args:
            client_id: クライアント識別子
            
        Returns:
            Optional[ClientConfig]: 設定情報（存在しない場合None）
        """
        file_path = self._config_dir / f"{client_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                return self._dict_to_config(config_data)
        except Exception:
            return None
    
    def save_feed_cache(self, url: str, feed: RSSFeed) -> None:
        """フィードキャッシュを保存
        
        Args:
            url: RSS URL
            feed: フィード情報
        """
        # URLをファイル名に変換
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        file_path = self._cache_dir / f"{url_hash}.json"
        
        feed_data = self._feed_to_dict(feed)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(feed_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            raise Exception(f"キャッシュ保存エラー: {str(e)}")
    
    def load_feed_cache(self, url: str) -> Optional[RSSFeed]:
        """フィードキャッシュを読み込み
        
        Args:
            url: RSS URL
            
        Returns:
            Optional[RSSFeed]: キャッシュされたフィード（存在しない場合None）
        """
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        file_path = self._cache_dir / f"{url_hash}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                feed_data = json.load(f)
                return self._dict_to_feed(feed_data)
        except Exception:
            return None
    
    def _config_to_dict(self, config: ClientConfig) -> Dict[str, Any]:
        """設定オブジェクトを辞書に変換"""
        rss_configs_data = []
        for rss_config in config.rss_configs:
            rss_configs_data.append({
                'url': rss_config.url,
                'alias': rss_config.alias,
                'enabled': rss_config.enabled,
                'last_check': rss_config.last_check.isoformat()
            })
        
        return {
            'client_id': config.client_id,
            'rss_configs': rss_configs_data,
            'update_frequency': config.update_frequency.value,
            'max_items_per_feed': config.max_items_per_feed,
            'created_at': config.created_at.isoformat(),
            'last_updated': config.last_updated.isoformat()
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ClientConfig:
        """辞書を設定オブジェクトに変換"""
        rss_configs = []
        for rss_data in data.get('rss_configs', []):
            rss_config = RSSConfig(
                url=rss_data['url'],
                alias=rss_data.get('alias', ''),
                enabled=rss_data.get('enabled', True),
                last_check=datetime.fromisoformat(rss_data['last_check'])
            )
            rss_configs.append(rss_config)
        
        return ClientConfig(
            client_id=data['client_id'],
            rss_configs=rss_configs,
            update_frequency=UpdateFrequency(data.get('update_frequency', 'daily')),
            max_items_per_feed=data.get('max_items_per_feed', 20),
            created_at=datetime.fromisoformat(data['created_at']),
            last_updated=datetime.fromisoformat(data['last_updated'])
        )
    
    def _feed_to_dict(self, feed: RSSFeed) -> Dict[str, Any]:
        """フィードオブジェクトを辞書に変換"""
        items_data = []
        for item in feed.items:
            items_data.append({
                'title': item.title,
                'link': item.link,
                'description': item.description,
                'published': item.published.isoformat() if item.published else None,
                'author': item.author
            })
        
        return {
            'title': feed.title,
            'link': feed.link,
            'description': feed.description,
            'url': feed.url,
            'items': items_data,
            'last_updated': feed.last_updated.isoformat(),
            'last_fetch': feed.last_fetch.isoformat()
        }
    
    def _dict_to_feed(self, data: Dict[str, Any]) -> RSSFeed:
        """辞書をフィードオブジェクトに変換"""
        items = []
        for item_data in data.get('items', []):
            published = None
            if item_data.get('published'):
                published = datetime.fromisoformat(item_data['published'])
            
            item = RSSItem(
                title=item_data['title'],
                link=item_data['link'],
                description=item_data['description'],
                published=published,
                author=item_data.get('author')
            )
            items.append(item)
        
        return RSSFeed(
            title=data['title'],
            link=data['link'],
            description=data['description'],
            url=data['url'],
            items=items,
            last_updated=datetime.fromisoformat(data['last_updated']),
            last_fetch=datetime.fromisoformat(data['last_fetch'])
        )
