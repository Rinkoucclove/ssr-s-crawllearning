"""
使用示例
演示如何使用新闻爬虫的各种功能
"""
import logging
from news_crawler.crawler import NewsCrawler
from news_crawler.config import DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR


def example_basic_usage():
    """基础使用示例：单次爬取"""
    print("示例 1: 基础使用 - 单次爬取")

    crawler = NewsCrawler(
        headers=DEFAULT_HEADERS,
        base_domain=BASE_DOMAIN,
        target_dir=TARGET_DIR
    )

    try:
        success = crawler.run()
        if success:
            print("✅ 爬取成功")
        else:
            print("ℹ️ 没有新文章或出现错误")
    finally:
        crawler.close()


def example_custom_domain():
    """自定义站点示例"""
    print("示例 2: 爬取自定义站点")

    custom_headers = DEFAULT_HEADERS.copy()
    custom_domain = "https://your-target-site.com"
    custom_output = "./data/custom_news"

    crawler = NewsCrawler(
        headers=custom_headers,
        base_domain=custom_domain,
        target_dir=custom_output
    )

    try:
        success = crawler.run()
        print(f"爬取结果: {success}")
    finally:
        crawler.close()


def example_context_manager():
    """使用上下文管理器示例"""
    print("示例 3: 使用上下文管理器（推荐）")

    with NewsCrawler(DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR) as crawler:
        success = crawler.run()
        print(f"爬取结果: {success}")


def example_load_existing_articles():
    """加载已有文章示例"""
    from news_crawler.data.data_manager import NewsDataManager

    print("示例 4: 加载已有的文章数据")

    # 读取已有的哈希ID集合
    hash_ids = NewsDataManager.load_existing_hash_ids(TARGET_DIR)
    print(f"已保存文章数量: {len(hash_ids)}")

    # 加载所有文章
    articles = NewsDataManager.load_articles_from_json(TARGET_DIR)
    print(f"加载文章总数: {len(articles)}")

    if articles:
        print("\n最新 5 篇文章:")
        for article in articles[:5]:
            print(f"- {article.title} ({article.publish_time})")


def example_direct_parser():
    """直接使用解析器示例"""
    from news_crawler.session import NewsSessionManager
    from news_crawler.parsers.page_parser import NewsPageParser

    print("示例 5: 直接使用解析器")

    # 创建会话管理器
    session_manager = NewsSessionManager(DEFAULT_HEADERS)

    # 创建解析器
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 收集所有详情页链接
    start_url = f"{BASE_DOMAIN}/"
    urls = parser.collect_info_page_urls(start_url, max_pages=10)  # 限制只爬10页
    print(f"发现 {len(urls)} 个详情页")

    # 解析第一个页面
    if urls:
        article = parser.parse_news_detail(urls[0])
        if article:
            print(f"\n解析成功:")
            print(f"标题: {article.title}")
            print(f"时间: {article.publish_time}")
            print(f"点击量: {article.clicks}")
            print(f"图片数: {len(article.img_url)}")
            print(f"附件: {article.attchment}")

    session_manager.close()


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("新闻爬虫使用示例")
    print("=" * 60)

    # 运行示例（取消注释以运行）
    # example_basic_usage()
    # example_custom_domain()
    # example_context_manager()
    example_load_existing_articles()
    # example_direct_parser()

    print("\n提示: 取消注释其他示例函数来尝试不同的用法")
