# 一个微爬虫

结构化、模块化的网站爬虫工具，专门用于爬取南京大学马克思主义社会理论研究中心（实践与文本）网站的新闻内容。

## 项目结构

```
news_crawler/
├── __init__.py                 # 包初始化文件
├── config.py                   # 配置模块（常量、参数）
├── models.py                   # 数据模型（Article类）
├── session.py                  # 会话管理器
├── crawler.py                  # 爬虫主类
├── utils/                      # 工具模块
│   ├── __init__.py
│   └── ssl_adapter.py          # SSL适配器
├── parsers/                    # 解析器模块
│   ├── __init__.py
│   └── page_parser.py          # 页面解析器
└── data/                       # 数据管理模块
    ├── __init__.py
    └── data_manager.py         # 数据管理器

main.py                         # 入口文件
README.md                       # 项目说明（本文档）
DEPLOYMENT.md                   # 部署指南
QUICKSTART.md                   # 快速开始
.example.py                     # 使用示例
```

## 功能特性

- **站点遍历**：使用BFS算法遍历站点，收集所有详情页链接
- **智能解析**：自动提取标题、日期、正文、图片、附件、点击量等信息
- **去重机制**：基于MD5哈希值实现文章去重，避免重复保存
- **灵活配置**：集中管理配置参数，便于调整
- **定时运行**：支持单次运行和定时运行两种模式
- **数据持久化**：将文章数据保存为JSON文件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 单次运行

```bash
python main.py --mode once
```

### 2. 定时运行

```bash
python main.py --mode scheduled
```

定时模式下，爬虫会每隔 60 分钟自动运行一次（可在 `config.py` 中修改 `INTERVAL_MINUTES`）。

### 3. 自定义参数

```bash
python main.py --mode once --domain https://example.com --output ./data/news
```

参数说明：
- `--mode`: 运行模式，`once`（单次）或 `scheduled`（定时）
- `--domain`: 目标站点域名
- `--output`: 数据保存目录

## 配置说明

所有配置参数集中在 `news_crawler/config.py` 文件中：

### 爬虫配置

```python
REQUEST_INTERVAL_SECONDS = 0.5  # 请求间隔（秒）
MAX_PAGES = 400                # 最大遍历页面数
TIMEOUT = 15                   # 请求超时时间（秒）
```

### 目标站点配置

```python
BASE_DOMAIN = "https://ptext.nju.edu.cn"
TARGET_DIR = "./data/news"
```

### 定时任务配置

```python
INTERVAL_MINUTES = 60  # 定时爬取间隔（分钟）
```

### 内容选择器配置

如需爬取其他站点，需要修改以下配置：

```python
CONTENT_SELECTORS = [
    'div#vsb_content',
    'div.v_news_content',
    'div.article',
    'div.content',
    'div.cont',
    'article',
]

TITLE_SELECTORS = ['h1', '.article-title', '.title', 'h2']
```

## 数据模型

每篇文章包含以下字段：

```python
{
    "url": "",              # 文章链接
    "title": "",            # 标题
    "publish_time": "",     # 发布时间（YYYY-MM-DD）
    "content": "",          # 正文内容
    "attchment": "",        # 附件链接
    "img_url": [],          # 图片链接列表
    "clicks": "",           # 点击量
    "hash_id": ""           # 唯一标识（MD5哈希）
}
```

## 二次开发

### 扩展新的解析规则

1. 修改 `news_crawler/parsers/page_parser.py` 中的选择器配置
2. 根据目标站点的HTML结构调整解析逻辑

### 支持新的数据存储方式

1. 在 `news_crawler/data/` 目录下创建新的数据管理器
2. 实现 `save_articles_to_json()` 和 `load_existing_hash_ids()` 方法
3. 在 `NewsCrawler` 类中替换数据管理器

### 添加新的功能模块

1. 在相应目录下创建新的模块文件
2. 在 `__init__.py` 中导出必要的类和函数
3. 在主类或入口文件中引入使用

## 注意事项

1. **请求频率**：请合理设置 `REQUEST_INTERVAL_SECONDS`，避免对目标站点造成过大压力
2. **SSL配置**：如遇到SSL证书问题，可调整 `utils/ssl_adapter.py` 中的SSL配置
3. **去重机制**：基于MD5哈希值去重，确保文章内容的唯一性
4. **日志输出**：所有操作都会记录日志，便于调试和监控

## 许可证

本项目仅供学习和研究使用，请遵守目标站点的 robots.txt 规则和相关法律法规。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进本项目。

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

---

---

## 🌐 Web 服务

项目现在包含一个 Web 服务，提供爬虫的 Web 界面和 API 接口。

### 启动 Web 服务

```bash
# 方式 1：直接运行
python web_service.py

# 方式 2：使用 coze 命令
coze dev

# 方式 3：后台运行
python web_service.py > /app/work/logs/bypass/web.log 2>&1 &
```

### 访问界面

打开浏览器访问：http://localhost:5000

### API 接口

#### 1. 查看状态
```bash
curl http://localhost:5000/api/status
```

#### 2. 查看统计
```bash
curl http://localhost:5000/api/stats
```

#### 3. 启动爬虫
```bash
curl -X POST http://localhost:5000/api/start
```

#### 4. 查看文章列表
```bash
curl http://localhost:5000/api/articles
```

### API 响应示例

```json
{
  "status": "success",
  "data": {
    "running": false,
    "last_run": null,
    "success": false,
    "message": "等待启动"
  }
}
```

### Web 界面功能

- 🟢 运行状态显示
- 📊 统计信息展示
- 📡 API 接口列表
- 🎨 现代化 UI 设计

### 技术栈

- Flask - Web 框架
- Python 3.12+
- HTML5 + CSS3

