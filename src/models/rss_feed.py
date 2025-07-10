from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RSSItem:
    """RSS記事アイテム"""
    title: str
    link: str
    description: str
    published: Optional[datetime] = None
    author: Optional[str] = None
    
    def __post_init__(self):
        """初期化後処理"""
        if isinstance(self.published, str):
            # 文字列形式の日時をdatetimeに変換
            try:
                from email.utils import parsedate_to_datetime
                self.published = parsedate_to_datetime(self.published)
            except (ValueError, TypeError):
                self.published = None


@dataclass
class RSSFeed:
    """RSSフィード情報"""
    title: str
    link: str
    description: str
    url: str
    items: List[RSSItem] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    last_fetch: datetime = field(default_factory=datetime.now)
    
    @property
    def latest_item_date(self) -> Optional[datetime]:
        """最新記事の投稿日時を取得"""
        valid_dates = [item.published for item in self.items if item.published]
        return max(valid_dates) if valid_dates else None
    
    @property
    def item_count(self) -> int:
        """記事数を取得"""
        return len(self.items)
