import streamlit as st
import time
from datetime import datetime, timedelta
from typing import List, Optional

# プロジェクトモジュールのインポート
from src.services.rss_service import RSSService
from src.services.config_service import ConfigService
from src.repositories.local_data_repository import LocalDataRepository
from src.models.client_config import UpdateFrequency
from src.models.rss_feed import RSSFeed
from src.utils.helpers import (
    format_datetime, format_timedelta, truncate_text,
    get_client_id_from_session, display_success, display_error,
    display_warning, display_info
)


def init_services() -> tuple[RSSService, ConfigService]:
    """サービスインスタンスを初期化"""
    if 'services_initialized' not in st.session_state:
        repository = LocalDataRepository()
        rss_service = RSSService(repository)
        config_service = ConfigService(repository)
        
        st.session_state.rss_service = rss_service
        st.session_state.config_service = config_service
        st.session_state.services_initialized = True
    
    return st.session_state.rss_service, st.session_state.config_service


def render_sidebar(config_service: ConfigService, client_id: str) -> None:
    """サイドバーを描画"""
    st.sidebar.title("📋 設定")
    
    config = config_service.get_client_config(client_id)
    
    # 更新頻度設定
    st.sidebar.subheader("更新頻度")
    frequency_options = {
        UpdateFrequency.MANUAL: "手動更新",
        UpdateFrequency.HOURLY: "1時間ごと",
        UpdateFrequency.DAILY: "1日ごと",
        UpdateFrequency.WEEKLY: "1週間ごと"
    }
    
    current_freq = config.update_frequency
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
        config_service.update_frequency(client_id, selected_freq)
        st.sidebar.success("更新頻度を変更しました")
        st.rerun()
    
    # RSS追加フォーム
    st.sidebar.subheader("RSS追加")
    with st.sidebar.form("add_rss_form"):
        new_url = st.text_input("RSS URL", placeholder="https://example.com/rss")
        new_alias = st.text_input("表示名（任意）", placeholder="例: ニュースサイト")
        
        if st.form_submit_button("追加"):
            if new_url:
                rss_service, _ = init_services()
                
                # URL検証
                if not rss_service.validate_url(new_url):
                    display_error("無効なURLです")
                else:
                    success = config_service.add_rss_to_config(client_id, new_url, new_alias)
                    if success:
                        display_success("RSSを追加しました")
                        st.rerun()
                    else:
                        display_error("RSS追加に失敗しました")
            else:
                display_warning("URLを入力してください")


def render_rss_feed_card(feed: RSSFeed, rss_config, config_service: ConfigService, client_id: str) -> None:
    """RSSフィードカードを描画"""
    with st.container():
        # ヘッダー
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(f"📰 {feed.title or rss_config.display_name}")
            st.caption(f"🔗 {feed.url}")
        
        with col2:
            # 更新情報
            now = datetime.now()
            time_diff = now - feed.last_fetch
            st.metric("最終更新", format_timedelta(time_diff))
        
        with col3:
            # 削除ボタン
            if st.button("🗑️ 削除", key=f"delete_{feed.url}"):
                if config_service.remove_rss_from_config(client_id, feed.url):
                    display_success("RSSを削除しました")
                    st.rerun()
                else:
                    display_error("削除に失敗しました")
        
        # フィード情報
        if feed.description:
            st.write(truncate_text(feed.description, 150))
        
        # 記事一覧
        if feed.items:
            st.write(f"**最新記事 ({len(feed.items)}件)**")
            
            for i, item in enumerate(feed.items[:5]):  # 最新5件を表示
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
        else:
            st.info("記事が見つかりませんでした")
        
        st.divider()


def render_main_content(rss_service: RSSService, config_service: ConfigService, client_id: str) -> None:
    """メインコンテンツを描画"""
    config = config_service.get_client_config(client_id)
    
    # ヘッダー
    st.title("📡 RSS Monitor")
    st.markdown("**シンプルで洗練されたRSS更新監視ツール**")
    
    if not config.rss_configs:
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
                    success = config_service.add_rss_to_config(client_id, url, name)
                    if success:
                        display_success(f"{name}を追加しました")
                        st.rerun()
        return
    
    # 更新ボタンとステータス
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🔄 すべて更新", type="primary"):
            update_all_feeds(rss_service, config_service, client_id)
    
    with col2:
        st.metric("登録RSS数", len(config.rss_configs))
    
    with col3:
        st.metric("更新頻度", config.update_frequency.display_name)
    
    st.divider()
    
    # RSSフィード一覧
    feeds_loaded = 0
    
    for rss_config in config.rss_configs:
        if not rss_config.enabled:
            continue
        
        try:
            # フィードを取得（キャッシュ優先）
            feed = rss_service.get_feed_with_cache(rss_config.url)
            
            if feed:
                render_rss_feed_card(feed, rss_config, config_service, client_id)
                feeds_loaded += 1
            else:
                # 取得失敗時の表示
                st.error(f"❌ **{rss_config.display_name}** の取得に失敗しました")
                st.caption(f"URL: {rss_config.url}")
                
        except Exception as e:
            st.error(f"❌ **{rss_config.display_name}**: {str(e)}")
    
    if feeds_loaded == 0:
        st.warning("有効なRSSフィードがありません")


def update_all_feeds(rss_service: RSSService, config_service: ConfigService, client_id: str) -> None:
    """すべてのRSSフィードを更新"""
    config = config_service.get_client_config(client_id)
    
    if not config.rss_configs:
        display_warning("更新するRSSがありません")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_feeds = len([cfg for cfg in config.rss_configs if cfg.enabled])
    
    if total_feeds == 0:
        display_warning("有効なRSSがありません")
        return
    
    success_count = 0
    
    for i, rss_config in enumerate([cfg for cfg in config.rss_configs if cfg.enabled]):
        status_text.text(f"更新中: {rss_config.display_name}")
        
        try:
            # 強制更新
            feed = rss_service.get_feed_with_cache(rss_config.url, force_refresh=True)
            if feed:
                success_count += 1
        except Exception:
            pass  # エラーは無視して続行
        
        progress_bar.progress((i + 1) / total_feeds)
        time.sleep(0.1)  # UI更新のための短い待機
    
    progress_bar.empty()
    status_text.empty()
    
    display_success(f"{success_count}/{total_feeds} 件のRSSを更新しました")
    st.rerun()


def main():
    """メイン関数"""
    # ページ設定
    st.set_page_config(
        page_title="RSS Monitor",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS スタイル
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
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
    rss_service, config_service = init_services()
    
    # クライアントID取得
    client_id = get_client_id_from_session()
    
    # サイドバー描画
    render_sidebar(config_service, client_id)
    
    # メインコンテンツ描画
    render_main_content(rss_service, config_service, client_id)
    
    # フッター
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "RSS Monitor v1.0 | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
