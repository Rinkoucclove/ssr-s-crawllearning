# 部署指南

本文档提供新闻爬虫项目的部署说明。

## 环境要求

- Python 3.7+
- pip（Python包管理器）

## 部署步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置参数

根据需要修改 `news_crawler/config.py` 中的配置参数：

```python
# 目标站点
BASE_DOMAIN = "https://ptext.nju.edu.cn"
TARGET_DIR = "./data/news"

# 爬虫参数
REQUEST_INTERVAL_SECONDS = 0.5  # 请求间隔
MAX_PAGES = 400                # 最大遍历页面数
INTERVAL_MINUTES = 60          # 定时间隔（分钟）
```

### 3. 运行爬虫

#### 单次运行

```bash
python main.py --mode once
```

#### 定时运行

```bash
python main.py --mode scheduled
```

#### 自定义参数

```bash
python main.py --mode once --domain https://example.com --output ./data/custom
```

## 部署方案

### 方案一：直接运行

适合开发测试阶段。

```bash
python main.py --mode scheduled
```

### 方案二：后台运行（Linux/Mac）

使用 nohup 命令在后台运行：

```bash
nohup python main.py --mode scheduled > crawler.log 2>&1 &
```

查看日志：

```bash
tail -f crawler.log
```

### 方案三：使用 Supervisor（推荐）

Supervisor 是一个进程管理工具，可以自动重启崩溃的进程。

1. 安装 Supervisor：

```bash
sudo apt-get install supervisor  # Ubuntu/Debian
sudo yum install supervisor      # CentOS/RHEL
```

2. 创建配置文件 `/etc/supervisor/conf.d/news_crawler.conf`：

```ini
[program:news_crawler]
command=/usr/bin/python3 /path/to/project/main.py --mode scheduled
directory=/path/to/project
user=your_username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/news_crawler.log
```

3. 启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start news_crawler
```

### 方案四：使用 Docker

1. 创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--mode", "scheduled"]
```

2. 创建 `.dockerignore`：

```
__pycache__
*.pyc
.venv
venv
.git
.gitignore
data/
*.log
```

3. 构建并运行：

```bash
docker build -t news-crawler .
docker run -d --name crawler news-crawler
```

### 方案五：使用 systemd（Linux系统服务）

创建服务文件 `/etc/systemd/system/news-crawler.service`：

```ini
[Unit]
Description=News Crawler Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/main.py --mode scheduled
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start news-crawler
sudo systemctl enable news-crawler  # 开机自启
```

查看状态：

```bash
sudo systemctl status news-crawler
```

查看日志：

```bash
sudo journalctl -u news-crawler -f
```

## 监控与维护

### 日志管理

程序日志会输出到标准输出，可以通过以下方式查看：

- 直接运行时：查看控制台输出
- Supervisor：查看 `/var/log/news_crawler.log`
- systemd：使用 `journalctl -u news-crawler`

### 数据备份

定期备份数据目录：

```bash
tar -czf news_data_$(date +%Y%m%d).tar.gz data/
```

### 性能监控

监控以下指标：

- 爬取成功率
- 每小时新增文章数
- 磁盘空间使用
- 内存占用

### 异常处理

常见问题：

1. **SSL证书错误**：
   - 检查 `utils/ssl_adapter.py` 中的SSL配置
   - 可能需要降低安全级别或更新证书

2. **请求超时**：
   - 检查网络连接
   - 增加 `config.py` 中的 `TIMEOUT` 值

3. **内存不足**：
   - 减少 `MAX_PAGES` 值
   - 增加系统内存或使用数据库存储

## 扩展站点支持

如需爬取其他站点，需要：

1. 修改 `config.py` 中的选择器配置：

```python
# 标题选择器
TITLE_SELECTORS = ['h1', '.article-title', '.title']

# 内容选择器
CONTENT_SELECTORS = ['div#content', 'div.article-body', 'article']

# 详情页URL模式
# 在 parsers/page_parser.py 中修改 collect_info_page_urls 方法
```

2. 修改域名配置：

```python
BASE_DOMAIN = "https://your-target-site.com"
```

3. 根据目标站点的特点调整解析逻辑

## 安全建议

1. **请求频率控制**：合理设置 `REQUEST_INTERVAL_SECONDS`，避免对目标站点造成压力
2. **遵守 robots.txt**：检查目标站点的爬取规则
3. **数据隐私**：不要爬取敏感信息
4. **定期更新**：保持依赖库最新版本
5. **访问控制**：生产环境建议使用防火墙限制访问

## 故障排查

### 问题：爬取不到任何文章

**可能原因**：
- 站点结构变化
- 选择器配置错误
- 网络连接问题

**排查方法**：
1. 检查目标站点是否可访问
2. 使用浏览器开发者工具查看页面结构
3. 调整选择器配置
4. 查看详细日志

### 问题：频繁超时

**可能原因**：
- 网络不稳定
- 目标站点响应慢
- 并发请求过多

**解决方法**：
1. 增加 `TIMEOUT` 值
2. 增大 `REQUEST_INTERVAL_SECONDS`
3. 检查网络连接

### 问题：重复文章

**可能原因**：
- 哈希值生成逻辑问题
- URL 模式匹配错误

**解决方法**：
1. 检查 `models.py` 中的哈希值生成逻辑
2. 确保 URL 模式正确匹配详情页

## 技术支持

如有问题，请查看：
1. 项目 README.md
2. 代码注释
3. 日志输出
4. GitHub Issues
