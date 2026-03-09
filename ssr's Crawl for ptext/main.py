"""
新闻爬虫入口文件
支持单次运行和定时运行模式
"""
import logging
import time
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from news_crawler.crawler import NewsCrawler
from news_crawler.config import (
    DEFAULT_HEADERS,
    BASE_DOMAIN,
    TARGET_DIR,
    INTERVAL_MINUTES
)


def single_run():
    """
    单次运行爬虫
    """
    logging.info("=======开始单次爬取=======")

    with NewsCrawler(DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR) as crawler:
        success = crawler.run()

    if success:
        logging.info("爬取成功，已完成")
    else:
        logging.info("没有新增或出错，请检查日志")


def scheduled_run():
    """
    定时运行爬虫（持续运行）
    """
    logging.info("=======启动定时爬虫=======")
    logging.info(f"定时间隔: {INTERVAL_MINUTES} 分钟")

    with NewsCrawler(DEFAULT_HEADERS, BASE_DOMAIN, TARGET_DIR) as crawler:
        while True:
            logging.info("=======开始一次定时爬取=======")
            success = crawler.run()

            if success:
                logging.info("爬取成功")
            else:
                logging.info("没有新增或出错，请检查日志")

            logging.info(f"{INTERVAL_MINUTES} 分钟后再进行下次爬取")
            time.sleep(INTERVAL_MINUTES * 60)


def main():
    """
    主函数
    根据命令行参数选择运行模式
    """
    import argparse

    parser = argparse.ArgumentParser(description='新闻爬虫工具')
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduled'],
        default='once',
        help='运行模式: once（单次运行）或 scheduled（定时运行）'
    )
    parser.add_argument(
        '--domain',
        default=BASE_DOMAIN,
        help=f'目标站点域名（默认: {BASE_DOMAIN}）'
    )
    parser.add_argument(
        '--output',
        default=TARGET_DIR,
        help=f'输出目录（默认: {TARGET_DIR}）'
    )

    args = parser.parse_args()

    # 如果提供了自定义参数，覆盖默认配置
    if args.domain != BASE_DOMAIN or args.output != TARGET_DIR:
        headers = DEFAULT_HEADERS.copy()
        crawler = NewsCrawler(headers, args.domain, args.output)
    else:
        crawler = NewsCrawler(DEFAULT_HEADERS, args.domain, args.output)

    try:
        if args.mode == 'once':
            logging.info("模式: 单次运行")
            crawler.run()
        else:
            logging.info("模式: 定时运行")
            while True:
                crawler.run()
                logging.info(f"{INTERVAL_MINUTES} 分钟后再进行下次爬取")
                time.sleep(INTERVAL_MINUTES * 60)
    except KeyboardInterrupt:
        logging.info("\n收到中断信号，正在退出...")
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
