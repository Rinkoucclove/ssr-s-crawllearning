"""
页面解析器测试 - 验证 join 操作修复
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from bs4 import BeautifulSoup
from news_crawler.parsers.page_parser import NewsPageParser
from news_crawler.session import NewsSessionManager
from news_crawler.config import DEFAULT_HEADERS, BASE_DOMAIN


def test_pattern_compilation():
    """测试正则表达式编译"""
    print("测试 1: 正则表达式编译")

    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 验证模式已成功编译
    assert parser.file_ext_pattern is not None, "file_ext_pattern 应该被编译"
    assert parser.attach_pattern is not None, "attach_pattern 应该被编译"

    print(f"✅ 正则表达式编译成功")
    print(f"  - file_ext_pattern: {parser.file_ext_pattern.pattern[:50]}...")
    print(f"  - attach_pattern: {parser.attach_pattern.pattern[:50]}...")

    session_manager.close()
    print()


def test_extract_content_with_empty_paragraphs():
    """测试提取空段落内容"""
    print("测试 2: 提取空段落内容")

    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 模拟没有段落的 HTML
    html = """
    <div class="content">
        <p></p>
        <p>   </p>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.select_one('.content')

    # 测试 _extract_content_paragraphs
    paragraphs = parser._extract_content_paragraphs(content_div)
    content = parser._extract_content(soup)

    # 应该返回空字符串而不是崩溃
    assert isinstance(content, str), "content 应该是字符串"
    print(f"✅ 空段落处理正确: '{content}'")

    session_manager.close()
    print()


def test_extract_content_with_valid_paragraphs():
    """测试提取有效段落内容"""
    print("测试 3: 提取有效段落内容")

    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 模拟有段落的 HTML
    html = """
    <div class="content">
        <p>第一段内容</p>
        <p>第二段内容</p>
        <p>第三段内容</p>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = parser._extract_content(soup)

    # 应该返回用换行符连接的段落
    assert isinstance(content, str), "content 应该是字符串"
    assert "第一段内容" in content, "应该包含第一段"
    assert "第二段内容" in content, "should contain second paragraph"
    assert "\n\n" in content, "应该包含双换行符"

    print(f"✅ 有效段落提取正确")
    print(f"  内容长度: {len(content)} 字符")
    print(f"  段落数: {content.count('\n\n') + 1}")

    session_manager.close()
    print()


def test_extract_content_with_mixed_types():
    """测试提取混合类型内容"""
    print("测试 4: 提取混合类型内容")

    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 模拟混合 HTML
    html = """
    <div class="content">
        <p>段落一</p>
        <div>非段落文本</div>
        <p>段落二</p>
        <span>跨度文本</span>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = parser._extract_content(soup)

    # 应该正常处理
    assert isinstance(content, str), "content 应该是字符串"
    print(f"✅ 混合类型处理正确")

    session_manager.close()
    print()


def test_extract_content_with_no_content_div():
    """测试没有内容区域的情况"""
    print("测试 5: 没有内容区域")

    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 模拟没有内容区域的 HTML
    html = """
    <html>
        <body>
            <h1>标题</h1>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = parser._extract_content(soup)

    # 应该返回空字符串
    assert isinstance(content, str), "content 应该是字符串"
    assert content == "", "没有内容区域应该返回空字符串"

    print(f"✅ 无内容区域处理正确")

    session_manager.close()
    print()


def test_pattern_matching():
    """测试正则表达式匹配"""
    print("测试 6: 正则表达式匹配")

    session_manager = NewsSessionManager(DEFAULT_HEADERS)
    parser = NewsPageParser(session_manager, BASE_DOMAIN)

    # 测试媒体文件扩展名匹配
    test_urls = [
        ("https://example.com/file.pdf", True),
        ("https://example.com/file.doc", True),
        ("https://example.com/file.jpg", True),
        ("https://example.com/file.html", False),
        ("https://example.com/file.htm", False),
    ]

    for url, should_match in test_urls:
        matches = parser.file_ext_pattern.search(url)
        if should_match:
            assert matches is not None, f"{url} 应该匹配"
        else:
            assert matches is None, f"{url} 不应该匹配"
        print(f"  - {url}: {'✅ 匹配' if (matches is not None) == should_match else '❌ 错误'}")

    print(f"✅ 正则表达式匹配测试通过")

    session_manager.close()
    print()


def main():
    print("=" * 60)
    print("页面解析器测试 - join 操作修复验证")
    print("=" * 60)
    print()

    try:
        test_pattern_compilation()
        test_extract_content_with_empty_paragraphs()
        test_extract_content_with_valid_paragraphs()
        test_extract_content_with_mixed_types()
        test_extract_content_with_no_content_div()
        test_pattern_matching()

        print("=" * 60)
        print("✅ 所有页面解析器测试通过！")
        print("=" * 60)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
