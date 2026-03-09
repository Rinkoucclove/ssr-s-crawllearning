"""
配置模块
集中管理爬虫的各类配置参数
"""
import logging

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 爬虫配置
REQUEST_INTERVAL_SECONDS = 0.5  # 每篇文章之间的请求间隔（秒）
MAX_PAGES = 400  # 最大遍历页面数，防止跑飞
TIMEOUT = 15  # 请求超时时间（秒）

# 数据库字段限制
ATTACHMENT_MAX_LENGTH = 200  # 附件URL最大长度
FILENAME_MAX_LENGTH = 100  # 文件名最大长度

# 定时任务配置
INTERVAL_MINUTES = 60  # 定时爬取间隔（分钟）

# HTTP 请求头配置
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# 目标站点配置
BASE_DOMAIN = "https://ptext.nju.edu.cn"
TARGET_DIR = "./data/news"

# 内容选择器配置
CONTENT_SELECTORS = [
    'div#vsb_content',
    'div.v_news_content',
    'div.article',
    'div.content',
    'div.cont',
    'article',
]

# 标题选择器配置（按优先级）
TITLE_SELECTORS = ['h1', '.article-title', '.title', 'h2']

# 过滤关键词
FILTER_KEYWORDS = ['学术链接', '版权所有', '上一篇', '下一篇']

# 附件文件扩展名
ATTACHMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar']

# 媒体文件扩展名（跳过）
MEDIA_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar',
                   'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'rmvb']
