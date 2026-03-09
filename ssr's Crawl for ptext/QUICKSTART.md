# 快速开始指南

本指南帮助你快速上手使用新闻爬虫项目。

## 5分钟快速开始

### 第一步：安装依赖

```bash
cd /path/to/project
pip install -r requirements.txt
```

### 第二步：单次测试运行

```bash
python main.py --mode once
```

这会执行一次完整的爬取流程，数据会保存到 `./data/news/` 目录。

### 第三步：查看结果

爬取完成后，检查输出目录：

```bash
ls -lh data/news/
```

每个新闻都会保存为一个独立的 JSON 文件。

### 第四步：定时运行（可选）

如果需要定期爬取，使用定时模式：

```bash
python main.py --mode scheduled
```

## 常用命令

### 查看帮助

```bash
python main.py --help
```

### 自定义目标站点

```bash
python main.py --mode once --domain https://example.com --output ./data/custom
```

### 使用上下文管理器（代码示例）

```python
from news_crawler.crawler import NewsCrawler
from news_crawler.config import DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR

with NewsCrawler(DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR) as crawler:
    crawler.run()
```

### 加载已有文章

```python
from news_crawler.data.data_manager import NewsDataManager

# 加载所有文章
articles = NewsDataManager.load_articles_from_json("./data/news")
print(f"共有 {len(articles)} 篇文章")

# 读取已保存的哈希ID集合
hash_ids = NewsDataManager.load_existing_hash_ids("./data/news")
print(f"已保存 {len(hash_ids)} 个唯一文章")
```

## 数据格式

每篇文章保存为一个 JSON 文件，格式如下：

```json
{
  "url": "https://ptext.nju.edu.cn/info/12345.htm",
  "title": "文章标题",
  "publish_time": "2024-01-15",
  "content": "文章正文内容...",
  "attchment": "https://ptext.nju.edu.cn/_upload/article/files/xxx.pdf",
  "img_url": [
    "https://ptext.nju.edu.cn/_upload/article/images/001.jpg",
    "https://ptext.nju.edu.cn/_upload/article/images/002.jpg"
  ],
  "clicks": "123",
  "hash_id": "a1b2c3d4e5f6..."
}
```

## 配置调整

### 修改爬取间隔

编辑 `news_crawler/config.py`：

```python
REQUEST_INTERVAL_SECONDS = 1.0  # 改为 1 秒
```

### 修改定时间隔

编辑 `news_crawler/config.py`：

```python
INTERVAL_MINUTES = 120  # 改为 2 小时
```

### 修改最大遍历页面数

编辑 `news_crawler/config.py`：

```python
MAX_PAGES = 1000  # 增加到 1000 页
```

## 常见问题

### Q1: 爬取时出现 SSL 错误怎么办？

**A**: 检查 `news_crawler/utils/ssl_adapter.py` 中的 SSL 配置，或者尝试降低安全级别。

### Q2: 如何爬取其他网站？

**A**:
1. 修改 `config.py` 中的 `BASE_DOMAIN`
2. 修改 `config.py` 中的选择器配置（`TITLE_SELECTORS`, `CONTENT_SELECTORS`）
3. 根据 `parsers/page_parser.py` 中的逻辑调整解析规则

### Q3: 数据保存在哪里？

**A**: 默认保存在 `./data/news/` 目录，可以通过 `--output` 参数或修改 `config.py` 中的 `TARGET_DIR` 来改变。

### Q4: 如何避免重复爬取？

**A**: 系统会自动基于 MD5 哈希值去重。如果文章的 `hash_id` 已经存在，会自动跳过。

### Q5: 如何查看爬取进度？

**A**: 程序会在控制台输出详细的日志信息，包括：
- 当前遍历页面
- 发现的详情页数量
- 解析进度
- 保存结果

## 下一步

- 查看 [README.md](README.md) 了解完整功能
- 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 了解部署方案
- 查看 [example.py](example.py) 查看更多使用示例
- 阅读代码注释了解实现细节

## 技术支持

遇到问题？
1. 查看日志输出
2. 检查配置文件
3. 参考示例代码
4. 提交 Issue
