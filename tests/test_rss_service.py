import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.rss_service import RSSService
from src.models.rss_feed import RSSFeed, RSSItem
from src.repositories.local_data_repository import LocalDataRepository


class TestRSSService(unittest.TestCase):
    """RSSサービスのテスト"""
    
    def setUp(self):
        """テスト初期化"""
        self.mock_repository = Mock()
        self.rss_service = RSSService(self.mock_repository)
    
    def test_validate_url_valid(self):
        """URL検証テスト（正常ケース）"""
        with patch('requests.head') as mock_head:
            mock_head.return_value.status_code = 200
            result = self.rss_service.validate_url("https://example.com/rss")
            self.assertTrue(result)
    
    def test_validate_url_invalid(self):
        """URL検証テスト（異常ケース）"""
        result = self.rss_service.validate_url("invalid-url")
        self.assertFalse(result)
    
    @patch('feedparser.parse')
    def test_fetch_feed_success(self, mock_parse):
        """RSS取得テスト（成功ケース）"""
        # Mock feedparser response
        mock_parse.return_value = Mock()
        mock_parse.return_value.bozo = False
        mock_parse.return_value.entries = [
            Mock(title="Test Title", link="https://example.com", 
                 summary="Test Summary", published_parsed=None, author="Test Author")
        ]
        mock_parse.return_value.feed = Mock(
            title="Test Feed", link="https://example.com", description="Test Description"
        )
        
        result = self.rss_service.fetch_feed("https://example.com/rss")
        
        self.assertIsInstance(result, RSSFeed)
        self.assertEqual(result.title, "Test Feed")
        self.assertEqual(len(result.items), 1)


if __name__ == '__main__':
    unittest.main()
