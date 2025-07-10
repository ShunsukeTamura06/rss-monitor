import streamlit as st
import time
from datetime import datetime, timedelta
from typing import List, Optional

# プロジェクトモジュールのインポート
from src.services.rss_service import RSSService
from src.services.config_service import ConfigService
from src.services.scheduler_service import SchedulerService
from src.repositories.local_data_repository import LocalDataRepository
from src.models.client_config import UpdateFrequency
from src.models.rss_feed import RSSFeed
from src.utils.helpers import (
    format_datetime, format_timedelta, truncate_text,
    get_client_id_from_session, display_success, display_error,
    display_warning, display_info
)
from src.utils.config_loader import config
from src.utils.error_handler import handle_rss_error, handle_config_error
from src.utils.logger import setup_logger, log_rss_activity


def init_services() -> tuple[RSSService, ConfigService, SchedulerService]:
    """サービスインスタンスを初期化（設定とロギング統合版）"""
    if 'services_initialized' not in st.session_state:
        # ロガーを設定
        logger = setup_logger(
            level=getattr(__import__('logging'), config.get('logging', 'log_level', 'INFO'))
        )
        
        # リポジトリとサービスを初期化
        repository = LocalDataRepository(
            data_dir=config.get('app', 'data_dir', 'data')
        )
        rss_service = RSSService(repository)
        config_service = ConfigService(repository)
        scheduler_service = SchedulerService(rss_service, config_service)
        
        # スケジューラーを開始
        scheduler_service.start()
        
        st.session_state.rss_service = rss_service
        st.session_state.config_service = config_service
        st.session_state.scheduler_service = scheduler_service
        st.session_state.services_initialized = True
        
        logger.info("サービス初期化完了")
    
    return (
        st.session_state.rss_service,
        st.session_state.config_service,
        st.session_state.scheduler_service
    )


def render_sidebar_enhanced(config_service: ConfigService, scheduler_service: SchedulerService, client_id: str) -> None:
    """改良版サイドバーを描画"""
    st.sidebar.title(f"{config.get('app', 'app_icon', '📋')} 設定")
    
    client_config = config_service.get_client_config(client_id)
    
    # 更新頻度設定
    st.sidebar.subheader("📅 更新頻度")
    frequency_options = {
        UpdateFrequency.MANUAL: "手動更新",
        UpdateFrequency.HOURLY: "1時間ごと",
        UpdateFrequency.DAILY: "1日ごと",
        UpdateFrequency.WEEKLY: "1週間ごと"
    }
    
    current_freq = client_config.update_frequency
    selected_freq_name = st.sidebar.selectbox(
        "更新間隔を選択",
        options=list(frequency_options.values()),
        index=list(frequency_options.keys()).index(current_freq)
    )
    
    # 選択された頻度を取得
    selected_freq = None
    for freq, name in frequency_options.items():
        if name == selected_freq_name:
            selected_freq = freq
            break
    
    if selected_freq != current_freq:
        if config_service.update_frequency(client_id, selected_freq):
            # スケジューラーを更新
            scheduler_service.schedule_client_updates(client_id)
            st.sidebar.success("更新頻度を変更しました")
            log_rss_activity(client_id, "更新頻度変更", success=True)
            st.rerun()
    
    # スケジューラー状態表示
    if current_freq != UpdateFrequency.MANUAL:
        schedules = scheduler_service.get_active_schedules()
        client_schedule = next(
            (s for s in schedules if f"client_{client_id}" in s['id']), None
        )
        if client_schedule:
            st.sidebar.info(f"⏰ 次回更新: {client_schedule['next_run']}")
    
    st.sidebar.divider()
    
    # RSS追加フォーム
    st.sidebar.subheader("➕ RSS追加")
    with st.sidebar.form("add_rss_form"):
        new_url = st.text_input("RSS URL", placeholder="https://example.com/rss")
        new_alias = st.text_input("表示名（任意）", placeholder="例: ニュースサイト")
        
        if st.form_submit_button("追加", type="primary"):
            if new_url:
                rss_service, _, _ = init_services()
                
                # URL検証（エラーハンドリング付き）
                @handle_rss_error
                def validate_and_add_rss():
                    if not rss_service.validate_url(new_url):
                        raise ValueError("無効なURLです")
                    
                    success = config_service.add_rss_to_config(client_id, new_url, new_alias)
                    if success:
                        # 新しいRSSのスケジュールを設定
                        scheduler_service.schedule_client_updates(client_id)
                        display_success("RSSを追加しました")
                        log_rss_activity(client_id, "RSS追加", new_url, success=True)
                        return True
                    else:
                        raise Exception("RSS追加に失敗しました")
                
                if validate_and_add_rss():
                    st.rerun()
            else:
                display_warning("URLを入力してください")
    
    # 設定情報表示
    st.sidebar.divider()
    st.sidebar.subheader("ℹ️ 設定情報")
    st.sidebar.text(f"登録RSS数: {len(client_config.rss_configs)}")
    st.sidebar.text(f"最大表示数: {client_config.max_items_per_feed}")
    st.sidebar.text(f"作成日: {format_datetime(client_config.created_at, '%Y-%m-%d')}")


def render_rss_feed_card_enhanced(feed: RSSFeed, rss_config, config_service: ConfigService, client_id: str) -> None:
    """改良版RSSフィードカードを描画"""
    with st.container():
        # ヘッダー
        col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
        
        with col1:
            st.subheader(f"📰 {feed.title or rss_config.display_name}")
            st.caption(f"🔗 {truncate_text(feed.url, 60)}")
        
        with col2:
            # 更新情報
            now = datetime.now()
            time_diff = now - feed.last_fetch
            st.metric("最終更新", format_timedelta(time_diff))
        
        with col3:
            # 記事数
            st.metric("記事数", f"{len(feed.items)}件")
        
        with col4:
            # 削除ボタン
            if st.button("🗑️", key=f"delete_{feed.url}", help="削除"):
                @handle_config_error
                def delete_rss():
                    success = config_service.remove_rss_from_config(client_id, feed.url)
                    if success:
                        display_success("RSSを削除しました")
                        log_rss_activity(client_id, "RSS削除", feed.url, success=True)
                        return True
                    else:
                        raise Exception("削除に失敗しました")
                
                if delete_rss():
                    st.rerun()
        
        # フィード情報
        if feed.description:
            st.write(truncate_text(feed.description, 150))
        
        # 記事一覧（タブ表示）
        if feed.items:
            tab1, tab2 = st.tabs(["📋 記事一覧", "📊 詳細情報"])
            
            with tab1:
                max_items = config.getint('app', 'max_items_per_feed', 5)
                for i, item in enumerate(feed.items[:max_items]):
                    with st.expander(f"{i+1}. {truncate_text(item.title, 80)}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            if item.description:
                                st.write(truncate_text(item.description, 200))
                            st.markdown(f"[記事を読む]({item.link})")
                        
                        with col2:
                            if item.published:
                                st.caption(f"📅 {format_datetime(item.published)}")
                            if item.author:
                                st.caption(f"✍️ {item.author}")
            
            with tab2:
                # フィード統計情報
                st.metric("総記事数", len(feed.items))
                if feed.latest_item_date:
                    st.metric("最新記事日時", format_datetime(feed.latest_item_date))
                st.metric("フィード更新", format_datetime(feed.last_updated))
                
                # 記事の日付分布
                if len(feed.items) > 1:
                    dates = [item.published for item in feed.items if item.published]
                    if dates:
                        import pandas as pd
                        df = pd.DataFrame({'日付': dates})
                        df['日'] = df['日付'].dt.date
                        daily_counts = df['日'].value_counts().sort_index()
                        
                        st.subheader("📈 日別記事数")
                        st.bar_chart(daily_counts)
        else:
            st.info("記事が見つかりませんでした")
        
        st.divider()


def render_main_content_enhanced(rss_service: RSSService, config_service: ConfigService, scheduler_service: SchedulerService, client_id: str) -> None:
    """改良版メインコンテンツを描画"""
    client_config = config_service.get_client_config(client_id)
    
    # ヘッダー
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"{config.get('app', 'app_icon', '📡')} {config.get('app', 'app_title', 'RSS Monitor')}")
        st.markdown("**シンプルで洗練されたRSS更新監視ツール**")
    
    with col2:
        # パフォーマンスメトリクス（設定で有効な場合）
        if config.getboolean('ui', 'show_performance_metrics', False):
            if 'last_update_time' in st.session_state:
                st.metric("前回更新時間", f"{st.session_state.last_update_time:.2f}秒")
    
    if not client_config.rss_configs:
        # RSS未設定時の案内
        st.info("👈 サイドバーからRSSを追加して開始しましょう")
        
        # サンプルRSS提案
        st.subheader("🔥 人気RSS例")
        sample_rss = [
            ("NHKニュース", "https://www.nhk.or.jp/rss/news/cat0.xml"),
            ("Yahoo!ニュース", "https://news.yahoo.co.jp/rss/topics/top-picks.xml"),
            ("ITmedia", "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml")
        ]
        
        for name, url in sample_rss:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{name}**")
                st.caption(url)
            with col2:
                if st.button("追加", key=f"sample_{name}"):
                    @handle_config_error
                    def add_sample_rss():
                        success = config_service.add_rss_to_config(client_id, url, name)
                        if success:
                            scheduler_service.schedule_client_updates(client_id)
                            display_success(f"{name}を追加しました")
                            log_rss_activity(client_id, "サンプルRSS追加", url, success=True)
                            return True
                        else:
                            raise Exception("追加に失敗しました")
                    
                    if add_sample_rss():
                        st.rerun()
        return
    
    # 更新ボタンとステータス
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("🔄 すべて更新", type="primary"):
            start_time = time.time()
            update_all_feeds_enhanced(rss_service, config_service, client_id)
            st.session_state.last_update_time = time.time() - start_time
    
    with col2:
        st.metric("登録RSS数", len(client_config.rss_configs))
    
    with col3:
        enabled_count = len([cfg for cfg in client_config.rss_configs if cfg.enabled])
        st.metric("有効RSS数", enabled_count)
    
    with col4:
        st.metric("更新頻度", client_config.update_frequency.display_name)
    
    st.divider()
    
    # RSSフィード一覧
    feeds_loaded = 0
    
    for rss_config in client_config.rss_configs:
        if not rss_config.enabled:
            continue
        
        @handle_rss_error
        def load_feed():
            # フィードを取得（キャッシュ優先）
            feed = rss_service.get_feed_with_cache(rss_config.url)
            if feed:
                render_rss_feed_card_enhanced(feed, rss_config, config_service, client_id)
                return True
            else:
                raise Exception("フィード取得に失敗しました")
        
        if load_feed():
            feeds_loaded += 1
        else:
            # 取得失敗時の表示
            st.error(f"❌ **{rss_config.display_name}** の取得に失敗しました")
            st.caption(f"URL: {rss_config.url}")
            log_rss_activity(client_id, "RSS取得失敗", rss_config.url, success=False)
    
    if feeds_loaded == 0:
        st.warning("有効なRSSフィードがありません")


def update_all_feeds_enhanced(rss_service: RSSService, config_service: ConfigService, client_id: str) -> None:
    """改良版全RSS更新"""
    client_config = config_service.get_client_config(client_id)
    
    if not client_config.rss_configs:
        display_warning("更新するRSSがありません")
        return
    
    enabled_configs = [cfg for cfg in client_config.rss_configs if cfg.enabled]
    
    if not enabled_configs:
        display_warning("有効なRSSがありません")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    success_count = 0
    error_count = 0
    
    for i, rss_config in enumerate(enabled_configs):
        status_text.text(f"更新中: {rss_config.display_name} ({i+1}/{len(enabled_configs)})")
        
        @handle_rss_error
        def update_single_feed():
            # 強制更新
            feed = rss_service.get_feed_with_cache(rss_config.url, force_refresh=True)
            if feed:
                log_rss_activity(client_id, "RSS更新", rss_config.url, success=True)
                return True
            else:
                raise Exception("フィード更新失敗")
        
        if update_single_feed():
            success_count += 1
        else:
            error_count += 1
            log_rss_activity(client_id, "RSS更新失敗", rss_config.url, success=False)
        
        progress_bar.progress((i + 1) / len(enabled_configs))
        time.sleep(0.1)  # UI更新のための短い待機
    
    progress_bar.empty()
    status_text.empty()
    
    if error_count > 0:
        display_warning(f"{success_count}/{len(enabled_configs)} 件のRSSを更新しました（{error_count}件失敗）")
    else:
        display_success(f"{success_count}/{len(enabled_configs)} 件のRSSを更新しました")
    
    st.rerun()


def main():
    """改良版メイン関数"""
    # ページ設定
    st.set_page_config(
        page_title=config.get('app', 'app_title', 'RSS Monitor'),
        page_icon=config.get('app', 'app_icon', '📡'),
        layout=config.get('ui', 'default_layout', 'wide'),
        initial_sidebar_state=config.get('ui', 'sidebar_state', 'expanded')
    )
    
    # CSS スタイル
    st.markdown("""
    <style>
    .main > div {
        padding-top: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .feed-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # サービス初期化
    rss_service, config_service, scheduler_service = init_services()
    
    # クライアントID取得
    client_id = get_client_id_from_session()
    
    # 初回アクセス時にスケジュールを設定
    if 'schedule_initialized' not in st.session_state:
        scheduler_service.schedule_client_updates(client_id)
        st.session_state.schedule_initialized = True
    
    # サイドバー描画
    render_sidebar_enhanced(config_service, scheduler_service, client_id)
    
    # メインコンテンツ描画
    render_main_content_enhanced(rss_service, config_service, scheduler_service, client_id)
    
    # フッター
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            f"{config.get('app', 'app_title', 'RSS Monitor')} v1.0 | Built with Streamlit | "
            f"クライアントID: {client_id[:8]}..."
            "</div>",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
