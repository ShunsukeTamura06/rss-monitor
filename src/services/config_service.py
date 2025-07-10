import hashlib
from datetime import datetime
from typing import Optional

from src.interfaces.data_repository import IDataRepository
from src.models.client_config import ClientConfig, UpdateFrequency


class ConfigService:
    """2クライアント設定の管理を行うサービス"""
    
    def __init__(self, repository: IDataRepository):
        """初期化
        
        Args:
            repository: データリポジトリ
        """
        self._repository = repository
    
    def get_client_config(self, client_id: str) -> ClientConfig:
        """クライアント設定を取得（存在しない場合は作成）
        
        Args:
            client_id: クライアント識別子
            
        Returns:
            ClientConfig: クライアント設定
        """
        config = self._repository.load_client_config(client_id)
        if config is None:
            # 新規作成
            config = ClientConfig(client_id=client_id)
            self._repository.save_client_config(client_id, config)
        
        return config
    
    def save_client_config(self, config: ClientConfig) -> None:
        """クライアント設定を保存
        
        Args:
            config: クライアント設定
        """
        config.last_updated = datetime.now()
        self._repository.save_client_config(config.client_id, config)
    
    def generate_client_id(self, user_agent: str, remote_addr: str = "unknown") -> str:
        """クライアントIDを生成
        
        Args:
            user_agent: ユーザーエージェント
            remote_addr: リモートアドレス
            
        Returns:
            str: クライアントID
        """
        # ユーザーエージェントとIPアドレスからハッシュを生成
        source = f"{user_agent}:{remote_addr}"
        return hashlib.md5(source.encode()).hexdigest()[:16]
    
    def add_rss_to_config(self, client_id: str, url: str, alias: str = "") -> bool:
        """RSS設定を追加
        
        Args:
            client_id: クライアント識別子
            url: RSS URL
            alias: エイリアス
            
        Returns:
            bool: 成功時True
        """
        try:
            config = self.get_client_config(client_id)
            config.add_rss(url, alias)
            self.save_client_config(config)
            return True
        except Exception:
            return False
    
    def remove_rss_from_config(self, client_id: str, url: str) -> bool:
        """RSS設定を削除
        
        Args:
            client_id: クライアント識別子
            url: RSS URL
            
        Returns:
            bool: 成功時True
        """
        try:
            config = self.get_client_config(client_id)
            result = config.remove_rss(url)
            if result:
                self.save_client_config(config)
            return result
        except Exception:
            return False
    
    def update_frequency(self, client_id: str, frequency: UpdateFrequency) -> bool:
        """更新頻度を変更
        
        Args:
            client_id: クライアント識別子
            frequency: 更新頻度
            
        Returns:
            bool: 成功時True
        """
        try:
            config = self.get_client_config(client_id)
            config.update_frequency = frequency
            self.save_client_config(config)
            return True
        except Exception:
            return False
