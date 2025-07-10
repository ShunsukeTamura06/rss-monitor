import unittest
from unittest.mock import Mock
from datetime import datetime

from src.services.config_service import ConfigService
from src.models.client_config import ClientConfig, UpdateFrequency
from src.repositories.local_data_repository import LocalDataRepository


class TestConfigService(unittest.TestCase):
    """Configサービスのテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.mock_repository = Mock()
        self.config_service = ConfigService(self.mock_repository)
    
    def test_generate_client_id(self):
        """Client ID生成テスト"""
        client_id = self.config_service.generate_client_id(
            "test-agent", "127.0.0.1"
        )
        self.assertEqual(len(client_id), 16)
        self.assertIsInstance(client_id, str)
    
    def test_get_client_config_new(self):
        """Client設定取得テスト（新規）"""
        # Mockが新規ケースを返す
        self.mock_repository.load_client_config.return_value = None
        
        result = self.config_service.get_client_config("test-client")
        
        self.assertIsInstance(result, ClientConfig)
        self.assertEqual(result.client_id, "test-client")
        self.mock_repository.save_client_config.assert_called_once()
    
    def test_add_rss_to_config(self):
        """RSS追加テスト"""
        # 既存設定をMock
        existing_config = ClientConfig(client_id="test-client")
        self.mock_repository.load_client_config.return_value = existing_config
        
        result = self.config_service.add_rss_to_config(
            "test-client", "https://example.com/rss", "Test RSS"
        )
        
        self.assertTrue(result)
        self.assertEqual(len(existing_config.rss_configs), 1)
        self.assertEqual(existing_config.rss_configs[0].url, "https://example.com/rss")


if __name__ == '__main__':
    unittest.main()
