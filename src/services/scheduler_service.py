import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.interfaces.rss_fetcher import IRSSFetcher
from src.services.config_service import ConfigService
from src.models.client_config import UpdateFrequency
import logging


class SchedulerService:
    """RSS自動更新スケジューラーサービス"""
    
    def __init__(self, rss_service: IRSSFetcher, config_service: ConfigService):
        """
        初期化
        
        Args:
            rss_service: RSSサービス
            config_service: 設定サービス
        """
        self._rss_service = rss_service
        self._config_service = config_service
        self._scheduler = BackgroundScheduler()
        self._active_jobs: Dict[str, str] = {}  # client_id -> job_id
        self._logger = logging.getLogger(__name__)
        
    def start(self) -> None:
        """スケジューラーを開始"""
        if not self._scheduler.running:
            self._scheduler.start()
            self._logger.info("スケジューラーが開始されました")
    
    def stop(self) -> None:
        """スケジューラーを停止"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            self._logger.info("スケジューラーが停止されました")
    
    def schedule_client_updates(self, client_id: str) -> bool:
        """
        クライアントの自動更新をスケジュール
        
        Args:
            client_id: クライアント識別子
            
        Returns:
            bool: 成功時True
        """
        try:
            config = self._config_service.get_client_config(client_id)
            
            # 既存のジョブを削除
            self._remove_client_job(client_id)
            
            # 手動更新の場合はスケジュールしない
            if config.update_frequency == UpdateFrequency.MANUAL:
                return True
            
            # インターバルを分単位で取得
            interval_minutes = config.update_frequency.interval_minutes
            
            if interval_minutes > 0:
                job = self._scheduler.add_job(
                    func=self._update_client_feeds,
                    trigger=IntervalTrigger(minutes=interval_minutes),
                    args=[client_id],
                    id=f"client_{client_id}",
                    name=f"RSS更新 - {client_id}",
                    replace_existing=True
                )
                
                self._active_jobs[client_id] = job.id
                self._logger.info(f"クライアント {client_id} の自動更新をスケジュール ({interval_minutes}分間隔)")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"スケジュール設定エラー: {str(e)}")
            return False
    
    def remove_client_schedule(self, client_id: str) -> bool:
        """
        クライアントのスケジュールを削除
        
        Args:
            client_id: クライアント識別子
            
        Returns:
            bool: 成功時True
        """
        return self._remove_client_job(client_id)
    
    def get_active_schedules(self) -> List[Dict[str, str]]:
        """
        アクティブなスケジュール一覧を取得
        
        Returns:
            List[Dict[str, str]]: スケジュール情報のリスト
        """
        schedules = []
        
        for job in self._scheduler.get_jobs():
            schedule_info = {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
            }
            schedules.append(schedule_info)
        
        return schedules
    
    def _update_client_feeds(self, client_id: str) -> None:
        """
        クライアントのRSSフィードを更新
        
        Args:
            client_id: クライアント識別子
        """
        try:
            config = self._config_service.get_client_config(client_id)
            updated_count = 0
            
            for rss_config in config.rss_configs:
                if not rss_config.enabled:
                    continue
                
                try:
                    # フィード更新を試行
                    feed = self._rss_service.get_feed_with_cache(
                        rss_config.url, force_refresh=True
                    )
                    
                    if feed:
                        # 最終チェック時刻を更新
                        rss_config.last_check = datetime.now()
                        updated_count += 1
                        
                except Exception as e:
                    self._logger.warning(f"RSS更新失敗 {rss_config.url}: {str(e)}")
            
            # 設定を保存
            self._config_service.save_client_config(config)
            
            self._logger.info(
                f"クライアント {client_id}: {updated_count}/{len(config.rss_configs)} RSS更新完了"
            )
            
        except Exception as e:
            self._logger.error(f"クライアント {client_id} の自動更新エラー: {str(e)}")
    
    def _remove_client_job(self, client_id: str) -> bool:
        """
        クライアントのジョブを削除
        
        Args:
            client_id: クライアント識別子
            
        Returns:
            bool: 成功時True
        """
        try:
            job_id = f"client_{client_id}"
            
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)
                
            if client_id in self._active_jobs:
                del self._active_jobs[client_id]
                
            self._logger.info(f"クライアント {client_id} のスケジュールを削除")
            return True
            
        except Exception as e:
            self._logger.warning(f"ジョブ削除エラー: {str(e)}")
            return False
