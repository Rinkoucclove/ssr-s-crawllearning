"""
快速测试 - 验证主程序能否正常启动
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from news_crawler.models import Article
from news_crawler.session import NewsSessionManager
from news_crawler.parsers.page_parser import NewsPageParser
from news_crawler.data.data_manager import NewsDataManager
from news_crawler.config import DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR


def test_components_initialization():
    """测试各组件能否正常初始化"""
    print("测试 1: 组件初始化")

    # 测试 Article
    article = Article(title="测试", url="https://example.com")
    article.generate_hash_id()
    print(f"✅ Article 初始化成功 - Hash: {article.hash_id[:8]}...")

    # 测试 SessionManager
    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    print("✅ SessionManager 初始化成功")

    # 测试 PageParser
    parser = NewsPageParser(session_manager, BASE_DOMAIN)
    print("✅ PageParser 初始化成功")

    # 测试 DataManager
    hash_ids = NewsDataManager.load_existing_hash_ids(TARGET_DIR)
    print(f"✅ DataManager 初始化成功 - 已有文章: {len(hash_ids)}")

    # 清理
    session_manager.close()
    print()


def test_crawler_initialization():
    """测试爬虫能否正常初始化"""
    print("测试 2: 爬虫初始化")

    from news_crawler.crawler import NewsCrawler

    crawler = NewsCrawler(DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR)
    print("✅ NewsCrawler 初始化成功")

    crawler.close()
    print()


def test_import_all_modules():
    """测试所有模块能否正常导入"""
    print("测试 3: 模块导入")

    try:
        import news_crawler.config
        import news_crawler.models
        import news_crawler.session
        import news_crawler.crawler
        import news_crawler.utils.ssl_adapter
        import news_crawler.parsers.page_parser
        import news_crawler.data.data_manager
        print("✅ 所有模块导入成功")
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        raise
    print()


def main():
    print("=" * 60)
    print("组件初始化测试")
    print("=" * 60)
    print()

    try:
        test_import_all_modules()
        test_components_initialization()
        test_crawler_initialization()

        print("=" * 60)
        print("✅ 所有组件测试通过！程序可以正常启动。")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
