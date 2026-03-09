"""
爬虫主模块
整合所有组件，提供统一的爬虫接口
"""
import logging
import time
from typing import Dict

from .models import Article
from .session import NewsSessionManager
from .parsers.page_parser import NewsPageParser
from .data.data_manager import NewsDataManager
from .config import REQUEST_INTERVAL_SECONDS


class NewsCrawler:
    """
    新闻爬虫主类（针对 ptext.nju.edu.cn）

    整合会话管理、页面解析和数据存储功能
    """

    def __init__(self, headers: Dict[str, str], base_domain: str, target_dir: str):
        """
        初始化爬虫

        Args:
            headers: HTTP请求头
            base_domain: 目标站点域名
            target_dir: 数据存储目录
        """
        self.headers = headers
        self.base_domain = base_domain
        self.target_dir = target_dir

        # 初始化各个组件
        self.session_manager = NewsSessionManager(headers)
        self.page_parser = NewsPageParser(self.session_manager, base_domain)
        self.data_manager = NewsDataManager()

    def run(self) -> bool:
        """
        运行爬虫主流程 - 基于MD5哈希值去重

        Returns:
            bool: 是否有新文章保存
        """
        try:
            # 读取已存在文章的 hash_id 集合
            existing_hash_ids = self.data_manager.load_existing_hash_ids(self.target_dir)
            logging.info(f"已保存文章哈希值数量: {len(existing_hash_ids)}")

            start_url = f"{self.base_domain}/"
            logging.info(f"起始URL: {start_url}")

            logging.info("开始在站内收集所有 info 详情页链接...")
            all_news_links = self.page_parser.collect_info_page_urls(start_url)
            logging.info(f"共收集到 {len(all_news_links)} 个详情页链接")

            # 基于MD5哈希值进行去重
            new_articles = []
            skipped_count = 0

            logging.info("开始解析新闻详情并基于哈希值去重...")
            for i, news_url in enumerate(all_news_links, 1):
                logging.info(f"解析进度: {i}/{len(all_news_links)} - {news_url}")
                article = self.page_parser.parse_news_detail(news_url)

                if article:
                    if article.hash_id in existing_hash_ids:
                        logging.info(f"跳过重复文章，Hash ID已存在: {article.hash_id} - {article.title}")
                        skipped_count += 1
                    else:
                        new_articles.append(article)
                        existing_hash_ids.add(article.hash_id)  # 避免本次 run 内重复
                        logging.info(f"发现新文章: {article.title} - Hash: {article.hash_id}")

                time.sleep(REQUEST_INTERVAL_SECONDS)

            logging.info(f"基于哈希值去重结果: 新文章 {len(new_articles)} 篇，重复文章 {skipped_count} 篇")

            if not new_articles:
                logging.info("没有检测到新文章，本次任务结束")
                return False

            logging.info("开始保存数据...")
            saved_count = self.data_manager.save_articles_to_json(new_articles, self.target_dir)

            logging.info(f"爬虫任务完成! 本次新增保存 {saved_count} 篇文章")
            return saved_count > 0

        except Exception as e:
            logging.error(f"爬虫运行失败: {e}")
            return False

    def close(self):
        """
        关闭爬虫资源
        """
        if self.session_manager:
            self.session_manager.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
