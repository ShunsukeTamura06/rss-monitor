# RSS Monitor API ドキュメント

## アーキテクチャ概要

RSS MonitorはSOLID原則に基づいたモジュラー設計を採用しています。

## 主要コンポーネント

### Interfaces (インターフェース層)

#### `IRSSFetcher`
RSS取得の抽象インターフェース

```python
class IRSSFetcher(ABC):
    @abstractmethod
    def fetch_feed(self, url: str) -> RSSFeed:
        """RSSフィードを取得"""
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """URLの有効性を検証"""
        pass
```

#### `IDataRepository`
データ永続化の抽象インターフェース

```python
class IDataRepository(ABC):
    @abstractmethod
    def save_client_config(self, client_id: str, config: ClientConfig) -> None:
        """Client設定を保存"""
        pass
    
    @abstractmethod
    def load_client_config(self, client_id: str) -> Optional[ClientConfig]:
        """Client設定を読み込み"""
        pass
```

### Models (データモデル層)

#### `RSSFeed`
RSSフィード情報を表現するデータクラス

```python
@dataclass
class RSSFeed:
    title: str
    link: str
    description: str
    url: str
    items: List[RSSItem]
    last_updated: datetime
    last_fetch: datetime
```

#### `ClientConfig`
クライアント設定を表現するデータクラス

```python
@dataclass
class ClientConfig:
    client_id: str
    rss_configs: List[RSSConfig]
    update_frequency: UpdateFrequency
    max_items_per_feed: int
```

### Services (ビジネスロジック層)

#### `RSSService`
RSS関連のビジネスロジックを担当

主要メソッド:
- `fetch_feed(url: str) -> RSSFeed`: RSS取得
- `validate_url(url: str) -> bool`: URL検証
- `get_feed_with_cache(url: str, force_refresh: bool) -> Optional[RSSFeed]`: キャッシュを考慮した取得

#### `ConfigService`
設定管理のビジネスロジックを担当

主要メソッド:
- `get_client_config(client_id: str) -> ClientConfig`: 設定取得
- `add_rss_to_config(client_id: str, url: str, alias: str) -> bool`: RSS追加
- `remove_rss_from_config(client_id: str, url: str) -> bool`: RSS削除

### Repositories (データアクセス層)

#### `LocalDataRepository`
ローカルファイルシステムでのデータ永続化実装

データ保存場所:
- `data/configs/`: クライアント設定ファイル
- `data/cache/`: RSSフィードキャッシュ

## 使用例

### 基本的な使用方法

```python
from src.services.rss_service import RSSService
from src.services.config_service import ConfigService
from src.repositories.local_data_repository import LocalDataRepository

# サービス初期化
repository = LocalDataRepository()
rss_service = RSSService(repository)
config_service = ConfigService(repository)

# RSS追加
client_id = "sample_client"
config_service.add_rss_to_config(client_id, "https://example.com/rss", "Example RSS")

# RSS取得
feed = rss_service.fetch_feed("https://example.com/rss")
print(f"タイトル: {feed.title}")
print(f"記事数: {len(feed.items)}")
```

## 拡張性

### 新しいデータソースへの対応

`IDataRepository`インターフェースを実装することで、簡単に新しいデータソースに対応できます。

```python
class DatabaseRepository(IDataRepository):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save_client_config(self, client_id: str, config: ClientConfig) -> None:
        # SQLで設定保存を実装
        pass
```

### 新しいRSS取得方法の追加

`IRSSFetcher`インターフェースを実装することで、特殊なRSSフォーマットに対応できます。

```python
class CustomRSSFetcher(IRSSFetcher):
    def fetch_feed(self, url: str) -> RSSFeed:
        # カスタムRSS取得ロジックを実装
        pass
```
