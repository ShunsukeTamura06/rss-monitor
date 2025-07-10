from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any
from enum import Enum


class UpdateFrequency(Enum):
    """更新頻度設定"""
    MANUAL = "manual"          # 手動更新
    HOURLY = "hourly"          # 1時間ごと
    DAILY = "daily"            # 1日ごと
    WEEKLY = "weekly"          # 1週間ごと
    
    @property
    def interval_minutes(self) -> int:
        """インターバルを分単位で取得"""
        mapping = {
            self.MANUAL: 0,
            self.HOURLY: 60,
            self.DAILY: 24 * 60,
            self.WEEKLY: 7 * 24 * 60
        }
        return mapping[self]
    
    @property
    def display_name(self) -> str:
        """表示用名称を取得"""
        mapping = {
            self.MANUAL: "手動更新",
            self.HOURLY: "1時間ごと",
            self.DAILY: "1日ごと",
            self.WEEKLY: "1週間ごと"
        }
        return mapping[self]


@dataclass
class RSSConfig:
    """RSS設定"""
    url: str
    alias: str = ""
    enabled: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    
    @property
    def display_name(self) -> str:
        """表示用名称"""
        return self.alias if self.alias else self.url


@dataclass
class ClientConfig:
    """クライアント設定"""
    client_id: str
    rss_configs: List[RSSConfig] = field(default_factory=list)
    update_frequency: UpdateFrequency = UpdateFrequency.DAILY
    max_items_per_feed: int = 20
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_rss(self, url: str, alias: str = "") -> None:
        """RSS設定を追加"""
        if not any(config.url == url for config in self.rss_configs):
            self.rss_configs.append(RSSConfig(url=url, alias=alias))
            self.last_updated = datetime.now()
    
    def remove_rss(self, url: str) -> bool:
        """RSS設定を削除"""
        original_count = len(self.rss_configs)
        self.rss_configs = [config for config in self.rss_configs if config.url != url]
        if len(self.rss_configs) < original_count:
            self.last_updated = datetime.now()
            return True
        return False
    
    def get_rss_config(self, url: str) -> RSSConfig:
        """指定URLのRSS設定を取得"""
        for config in self.rss_configs:
            if config.url == url:
                return config
        raise ValueError(f"RSS設定が見つかりません: {url}")
    
    def update_rss_config(self, url: str, **kwargs) -> bool:
        """RSS設定を更新"""
        try:
            config = self.get_rss_config(url)
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            self.last_updated = datetime.now()
            return True
        except ValueError:
            return False
