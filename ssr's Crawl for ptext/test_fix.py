"""
测试脚本 - 验证数据类型问题修复
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from news_crawler.models import Article


def test_article_with_none_img_url():
    """测试 img_url 为 None 的情况"""
    print("测试 1: img_url 为 None")
    article = Article(title="测试", url="https://example.com", img_url=None)
    assert isinstance(article.img_url, list), "img_url 应该是列表"
    assert len(article.img_url) == 0, "img_url 应该是空列表"
    hash_id = article.generate_hash_id()
    print(f"✅ 通过 - Hash ID: {hash_id}")
    print()


def test_article_with_empty_list():
    """测试 img_url 为空列表的情况"""
    print("测试 2: img_url 为空列表")
    article = Article(title="测试", url="https://example.com", img_url=[])
    assert isinstance(article.img_url, list), "img_url 应该是列表"
    hash_id = article.generate_hash_id()
    print(f"✅ 通过 - Hash ID: {hash_id}")
    print()


def test_article_with_string_img_url():
    """测试 img_url 为字符串的情况（模拟数据损坏）"""
    print("测试 3: img_url 为字符串（模拟数据损坏）")
    article = Article(title="测试", url="https://example.com", img_url="not_a_list")
    # __post_init__ 应该会将其转换为空列表
    assert isinstance(article.img_url, list), "img_url 应该是列表"
    hash_id = article.generate_hash_id()
    print(f"✅ 通过 - Hash ID: {hash_id}")
    print()


def test_article_with_valid_img_urls():
    """测试 img_url 包含有效 URL 的情况"""
    print("测试 4: img_url 包含有效 URL")
    urls = ["https://example.com/img1.jpg", "https://example.com/img2.png"]
    article = Article(title="测试", url="https://example.com", img_url=urls.copy())
    assert isinstance(article.img_url, list), "img_url 应该是列表"
    assert len(article.img_url) == 2, "img_url 应该包含 2 个 URL"
    hash_id = article.generate_hash_id()
    print(f"✅ 通过 - Hash ID: {hash_id}")
    print()


def test_data_manager_load_with_corrupted_data():
    """测试数据管理器加载损坏的数据"""
    import json
    import tempfile
    from news_crawler.data.data_manager import NewsDataManager

    print("测试 5: 数据管理器加载损坏的数据")

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建一个损坏的 JSON 文件（img_url 是字符串）
        corrupted_data = {
            "url": "https://example.com",
            "title": "测试",
            "img_url": "not_a_list",  # 损坏的数据
            "hash_id": "test123"
        }

        file_path = Path(temp_dir) / "test.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(corrupted_data, f)

        # 加载文章
        articles = NewsDataManager.load_articles_from_json(temp_dir)
        assert len(articles) == 1, "应该加载 1 篇文章"
        assert isinstance(articles[0].img_url, list), "加载的 img_url 应该是列表"
        print(f"✅ 通过 - 成功加载并修复损坏的数据")
    print()


def test_article_dict_conversion():
    """测试文章转字典"""
    print("测试 6: 文章转字典")
    article = Article(
        title="测试标题",
        url="https://example.com",
        publish_time="2024-01-15",
        img_url=["https://example.com/img.jpg"]
    )
    article_dict = article.to_dict()
    assert isinstance(article_dict['img_url'], list), "字典中的 img_url 应该是列表"
    print(f"✅ 通过 - 字典转换正确")
    print()


def main():
    print("=" * 60)
    print("开始测试数据类型修复")
    print("=" * 60)
    print()

    try:
        test_article_with_none_img_url()
        test_article_with_empty_list()
        test_article_with_string_img_url()
        test_article_with_valid_img_urls()
        test_data_manager_load_with_corrupted_data()
        test_article_dict_conversion()

        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
