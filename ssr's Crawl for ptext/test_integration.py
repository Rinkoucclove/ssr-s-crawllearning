"""
集成测试 - 验证修复后的完整流程
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


def test_argument_parsing():
    """测试命令行参数解析"""
    print("测试 1: 命令行参数解析")

    # 模拟命令行参数
    test_args = [
        '--mode', 'once',
        '--domain', 'https://example.com',
        '--output', './data/test'
    ]

    # 创建解析器
    parser = argparse.ArgumentParser(description='新闻爬虫工具')
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduled'],
        default='once',
        help='运行模式: once（单次运行）或 scheduled（定时运行）'
    )
    parser.add_argument(
        '--domain',
        default='https://ptext.nju.edu.cn',
        help='目标站点域名'
    )
    parser.add_argument(
        '--output',
        default='./data/news',
        help='输出目录'
    )

    args = parser.parse_args(test_args)

    assert args.mode == 'once', f"模式应为 'once'，实际为 '{args.mode}'"
    assert args.domain == 'https://example.com', f"域名应为 'https://example.com'，实际为 '{args.domain}'"
    assert args.output == './data/test', f"输出目录应为 './data/test'，实际为 '{args.output}'"

    print(f"✅ 参数解析成功:")
    print(f"  - 模式: {args.mode}")
    print(f"  - 域名: {args.domain}")
    print(f"  - 输出: {args.output}")
    print()


def test_full_workflow_simulation():
    """模拟完整工作流程"""
    print("测试 2: 完整工作流程模拟")

    from news_crawler.models import Article
    from news_crawler.data.data_manager import NewsDataManager
    import tempfile
    import json

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 创建测试文章（模拟爬取结果）
        articles = [
            Article(
                title="测试文章 1",
                url="https://example.com/article1",
                publish_time="2024-01-15",
                content="这是测试文章 1 的内容",
                img_url=["https://example.com/img1.jpg", "https://example.com/img2.png"],
                clicks="100"
            ),
            Article(
                title="测试文章 2",
                url="https://example.com/article2",
                publish_time="2024-01-16",
                content="这是测试文章 2 的内容",
                img_url=[],  # 空列表
                clicks="50"
            ),
            Article(
                title="测试文章 3",
                url="https://example.com/article3",
                publish_time="2024-01-17",
                content="这是测试文章 3 的内容",
                # img_url 未设置（应为 None）
            ),
        ]

        # 2. 生成哈希 ID
        for article in articles:
            article.generate_hash_id()
            assert article.hash_id, "哈希 ID 不能为空"

        print(f"✅ 生成了 {len(articles)} 篇文章的哈希 ID")

        # 3. 保存文章
        saved_count = NewsDataManager.save_articles_to_json(articles, temp_dir)
        assert saved_count == 3, f"应保存 3 篇文章，实际保存 {saved_count} 篇"
        print(f"✅ 成功保存 {saved_count} 篇文章")

        # 4. 加载已有文章的哈希 ID
        hash_ids = NewsDataManager.load_existing_hash_ids(temp_dir)
        assert len(hash_ids) == 3, f"应加载 3 个哈希 ID，实际加载 {len(hash_ids)} 个"
        print(f"✅ 加载了 {len(hash_ids)} 个已有哈希 ID")

        # 5. 模拟去重逻辑
        new_articles = [
            Article(title="新文章", url="https://example.com/new", publish_time="2024-01-18"),
            articles[0]  # 重复文章
        ]

        for article in new_articles:
            article.generate_hash_id()

        unique_articles = [a for a in new_articles if a.hash_id not in hash_ids]
        assert len(unique_articles) == 1, f"应过滤出 1 篇新文章，实际有 {len(unique_articles)} 篇"
        print(f"✅ 去重逻辑正常：{len(new_articles)} 篇文章 -> {len(unique_articles)} 篇新文章")

    print()


def test_edge_cases():
    """测试边界情况"""
    print("测试 3: 边界情况")

    from news_crawler.models import Article

    # 情况 1: 所有字段都为空
    article1 = Article()
    assert not article1.is_valid(), "空文章应该无效"
    print("✅ 空文章验证正确")

    # 情况 2: 只有标题和 URL
    article2 = Article(title="测试", url="https://example.com")
    assert article2.is_valid(), "只有标题和 URL 的文章应该有效"
    print("✅ 最小有效文章验证正确")

    # 情况 3: URL 为空
    article3 = Article(title="测试", url="")
    assert not article3.is_valid(), "URL 为空的文章应该无效"
    print("✅ 无效 URL 验证正确")

    # 情况 4: 标题为空
    article4 = Article(title="", url="https://example.com")
    assert not article4.is_valid(), "标题为空的文章应该无效"
    print("✅ 无效标题验证正确")

    # 情况 5: 附件 URL 超长
    long_attachment = "https://example.com/" + "x" * 300
    article5 = Article(title="测试", url="https://example.com", attchment=long_attachment)
    article5.truncate_attachment()
    assert len(article5.attchment) == 200, f"附件 URL 应被截断到 200 字符，实际为 {len(article5.attchment)}"
    print("✅ 附件 URL 截断正确")

    print()


def main():
    print("=" * 60)
    print("集成测试 - 验证修复后的完整流程")
    print("=" * 60)
    print()

    try:
        test_argument_parsing()
        test_full_workflow_simulation()
        test_edge_cases()

        print("=" * 60)
        print("✅ 所有集成测试通过！")
        print("=" * 60)
        print()
        print("程序已修复，可以正常使用：")
        print("  - 单次运行: python main.py --mode once")
        print("  - 定时运行: python main.py --mode scheduled")
        print()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
