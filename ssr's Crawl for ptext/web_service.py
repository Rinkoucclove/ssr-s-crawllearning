"""
Web 服务模块
提供爬虫的 Web 接口和控制功能
"""
from flask import Flask, jsonify, request, render_template_string
import logging
from threading import Thread
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from news_crawler.crawler import NewsCrawler
from news_crawler.config import DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR
from news_crawler.data.data_manager import NewsDataManager

app = Flask(__name__)

# 全局变量
crawler_thread = None
crawler_status = {
    'running': False,
    'last_run': None,
    'success': False,
    'message': '等待启动'
}


@app.route('/')
def index():
    """首页 - 显示爬虫状态"""
    html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>新闻爬虫 Web 服务</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 800px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            font-size: 32px;
            text-align: center;
        }
        .status-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .status-title {
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        .status-value {
            font-size: 24px;
            font-weight: bold;
        }
        .status-running {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .status-stopped {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
        }
        .api-list {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }
        .api-list h3 {
            margin-bottom: 15px;
            color: #333;
        }
        .api-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .api-item code {
            color: #e83e8c;
            font-weight: 600;
        }
        .message {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .success {
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        .error {
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕷️ 新闻爬虫 Web 服务</h1>

        <div class="status-card {% if crawler_status.running %}status-running{% else %}status-stopped{% endif %}">
            <div class="status-title">运行状态</div>
            <div class="status-value">
                {% if crawler_status.running %}🟢 运行中{% else %}🔴 已停止{% endif %}
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_articles }}</div>
                <div class="stat-label">已保存文章总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.unique_hash }}</div>
                <div class="stat-label">唯一文章数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.domain }}</div>
                <div class="stat-label">目标站点</div>
            </div>
        </div>

        {% if crawler_status.message %}
        <div class="message {% if crawler_status.success %}success{% else %}error{% endif %}">
            {{ crawler_status.message }}
        </div>
        {% endif %}

        <div class="api-list">
            <h3>📡 API 接口</h3>
            <div class="api-item">
                <code>POST /api/start</code> - 启动爬虫
            </div>
            <div class="api-item">
                <code>GET /api/status</code> - 查看状态
            </div>
            <div class="api-item">
                <code>GET /api/stats</code> - 统计信息
            </div>
            <div class="api-item">
                <code>GET /api/articles</code> - 文章列表
            </div>
        </div>
    </div>
</body>
</html>
    """

    # 获取统计信息
    stats = get_stats()
    return render_template_string(html_template, crawler_status=crawler_status, stats=stats)


@app.route('/api/status')
def api_status():
    """获取爬虫状态"""
    return jsonify({
        'status': 'success',
        'data': {
            'running': crawler_status['running'],
            'last_run': crawler_status['last_run'],
            'success': crawler_status['success'],
            'message': crawler_status['message']
        }
    })


@app.route('/api/stats')
def api_stats():
    """获取统计信息"""
    return jsonify({
        'status': 'success',
        'data': get_stats()
    })


@app.route('/api/start', methods=['POST'])
def api_start():
    """启动爬虫"""
    global crawler_thread, crawler_status

    if crawler_status['running']:
        return jsonify({
            'status': 'error',
            'message': '爬虫已经在运行中'
        }), 400

    try:
        crawler_status['running'] = True
        crawler_status['message'] = '爬虫启动中...'

        # 在后台线程中运行爬虫
        def run_crawler():
            global crawler_status
            try:
                crawler = NewsCrawler(DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR)
                success = crawler.run()
                crawler_status['running'] = False
                crawler_status['last_run'] = None
                crawler_status['success'] = success
                crawler_status['message'] = '爬取完成！' if success else '爬取失败'
                crawler.close()
            except Exception as e:
                crawler_status['running'] = False
                crawler_status['success'] = False
                crawler_status['message'] = f'爬取出错: {str(e)}'
                logging.error(f"爬虫运行失败: {e}")

        crawler_thread = Thread(target=run_crawler)
        crawler_thread.start()

        return jsonify({
            'status': 'success',
            'message': '爬虫启动成功'
        })

    except Exception as e:
        crawler_status['running'] = False
        crawler_status['message'] = f'启动失败: {str(e)}'
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/articles')
def api_articles():
    """获取文章列表"""
    try:
        articles = NewsDataManager.load_articles_from_json(TARGET_DIR)
        return jsonify({
            'status': 'success',
            'data': {
                'total': len(articles),
                'articles': [
                    {
                        'title': a.title,
                        'url': a.url,
                        'publish_time': a.publish_time,
                        'hash_id': a.hash_id
                    } for a in articles[:10]  # 只返回前 10 篇
                ]
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def get_stats():
    """获取统计信息"""
    try:
        # 加载已有文章
        articles = NewsDataManager.load_articles_from_json(TARGET_DIR)
        hash_ids = NewsDataManager.load_existing_hash_ids(TARGET_DIR)

        return {
            'total_articles': len(articles),
            'unique_hash': len(hash_ids),
            'domain': BASE_DOMAIN
        }
    except Exception as e:
        logging.error(f"获取统计信息失败: {e}")
        return {
            'total_articles': 0,
            'unique_hash': 0,
            'domain': BASE_DOMAIN
        }


def run_web_server(host='0.0.0.0', port=5000):
    """启动 Web 服务器"""
    logging.info(f"启动 Web 服务在 http://{host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    run_web_server()
