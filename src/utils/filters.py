from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
import re
from dataclasses import dataclass

from src.models.rss_feed import RSSItem, RSSFeed


@dataclass
class FilterRule:
    """フィルタリングルール"""
    field: str  # 'title', 'description', 'author'
    operator: str  # 'contains', 'not_contains', 'regex', 'equals'
    value: str
    case_sensitive: bool = False
    
    def apply(self, item: RSSItem) -> bool:
        """
        アイテムにフィルタルールを適用
        
        Args:
            item: 対象のRSSアイテム
            
        Returns:
            bool: フィルタ条件に一致する場合True
        """
        field_value = getattr(item, self.field, "")
        if field_value is None:
            field_value = ""
        
        if not self.case_sensitive:
            field_value = field_value.lower()
            compare_value = self.value.lower()
        else:
            compare_value = self.value
        
        if self.operator == "contains":
            return compare_value in field_value
        elif self.operator == "not_contains":
            return compare_value not in field_value
        elif self.operator == "equals":
            return field_value == compare_value
        elif self.operator == "regex":
            try:
                pattern = re.compile(compare_value, re.IGNORECASE if not self.case_sensitive else 0)
                return bool(pattern.search(field_value))
            except re.error:
                return False
        
        return False


@dataclass
class DateFilter:
    """日付フィルタ"""
    days_back: int = 7  # 過去何日分を表示するか
    
    def apply(self, item: RSSItem) -> bool:
        """
        日付フィルタを適用
        
        Args:
            item: 対象のRSSアイテム
            
        Returns:
            bool: フィルタ条件に一致する場合True
        """
        if not item.published:
            return True  # 日付不明の場合は表示
        
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        return item.published >= cutoff_date


class RSSFilter:
    """RSS記事フィルタリング機能"""
    
    def __init__(self):
        self.content_rules: List[FilterRule] = []
        self.date_filter: Optional[DateFilter] = None
        self.max_items: int = 50
    
    def add_content_rule(self, field: str, operator: str, value: str, case_sensitive: bool = False) -> None:
        """
        コンテンツフィルタルールを追加
        
        Args:
            field: フィルタ対象フィールド
            operator: フィルタ演算子
            value: フィルタ値
            case_sensitive: 大文字小文字を区別するか
        """
        rule = FilterRule(field, operator, value, case_sensitive)
        self.content_rules.append(rule)
    
    def set_date_filter(self, days_back: int) -> None:
        """
        日付フィルタを設定
        
        Args:
            days_back: 過去何日分を表示するか
        """
        self.date_filter = DateFilter(days_back)
    
    def set_max_items(self, max_items: int) -> None:
        """
        最大表示アイテム数を設定
        
        Args:
            max_items: 最大アイテム数
        """
        self.max_items = max_items
    
    def apply_to_feed(self, feed: RSSFeed) -> RSSFeed:
        """
        フィードにフィルタを適用
        
        Args:
            feed: 対象のRSSフィード
            
        Returns:
            RSSFeed: フィルタ適用後のフィード
        """
        filtered_items = []
        
        for item in feed.items:
            # コンテンツフィルタを適用
            if self.content_rules:
                content_match = any(rule.apply(item) for rule in self.content_rules)
                if not content_match:
                    continue
            
            # 日付フィルタを適用
            if self.date_filter and not self.date_filter.apply(item):
                continue
            
            filtered_items.append(item)
        
        # 最大アイテム数で制限
        filtered_items = filtered_items[:self.max_items]
        
        # 新しいフィードオブジェクトを作成
        filtered_feed = RSSFeed(
            title=feed.title,
            link=feed.link,
            description=feed.description,
            url=feed.url,
            items=filtered_items,
            last_updated=feed.last_updated,
            last_fetch=feed.last_fetch
        )
        
        return filtered_feed
    
    def clear_rules(self) -> None:
        """すべてのフィルタルールをクリア"""
        self.content_rules.clear()
        self.date_filter = None
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """
        現在のフィルタ設定の要約を取得
        
        Returns:
            Dict[str, Any]: フィルタ設定の要約
        """
        return {
            'content_rules_count': len(self.content_rules),
            'date_filter_days': self.date_filter.days_back if self.date_filter else None,
            'max_items': self.max_items,
            'rules': [
                {
                    'field': rule.field,
                    'operator': rule.operator,
                    'value': rule.value,
                    'case_sensitive': rule.case_sensitive
                }
                for rule in self.content_rules
            ]
        }


class SmartFilter:
    """スマートフィルタリング機能（AI風の自動分類）"""
    
    def __init__(self):
        self.keywords = {
            'technology': ['AI', '人工知能', 'プログラミング', 'ソフトウェア', 'アプリ', 'システム'],
            'news': ['ニュース', '速報', '発表', '最新', '更新'],
            'business': ['経済', 'ビジネス', '企業', '市場', '投資'],
            'sports': ['スポーツ', '野球', 'サッカー', 'オリンピック'],
            'entertainment': ['エンタメ', '映画', '音楽', 'アニメ', 'ゲーム']
        }
    
    def categorize_item(self, item: RSSItem) -> str:
        """
        記事を自動分類
        
        Args:
            item: 対象のRSSアイテム
            
        Returns:
            str: カテゴリ名
        """
        text = f"{item.title} {item.description}".lower()
        
        category_scores = {}
        
        for category, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text)
            if score > 0:
                category_scores[category] = score
        
        if not category_scores:
            return 'other'
        
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    def group_by_category(self, feed: RSSFeed) -> Dict[str, List[RSSItem]]:
        """
        記事をカテゴリ別にグループ化
        
        Args:
            feed: 対象のRSSフィード
            
        Returns:
            Dict[str, List[RSSItem]]: カテゴリ別記事辞書
        """
        categories = {}
        
        for item in feed.items:
            category = self.categorize_item(item)
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        return categories
    
    def get_category_display_name(self, category: str) -> str:
        """
        カテゴリの表示名を取得
        
        Args:
            category: カテゴリ名
            
        Returns:
            str: 表示用カテゴリ名
        """
        display_names = {
            'technology': '🖥️ テクノロジー',
            'news': '📰 ニュース',
            'business': '💼 ビジネス',
            'sports': '⚽ スポーツ',
            'entertainment': '🎬 エンタメ',
            'other': '📋 その他'
        }
        return display_names.get(category, f'📂 {category}')
